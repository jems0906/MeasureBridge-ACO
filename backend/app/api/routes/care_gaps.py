from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Assignment, Patient, get_db, timestamp
from app.schemas import AssignmentInput
from app.services.population import population


router = APIRouter(prefix="/api/care-gaps", tags=["Follow-up work"])


@router.get("")
def gaps(db: Session = Depends(get_db)):
    return [row for row in population(db) if row["result"]["status"] not in {"met", "excluded"}]


@router.put("/{patient_id}/assignment")
def assign(patient_id: str, request: AssignmentInput, db: Session = Depends(get_db)):
    if request.role != "ACO Operations":
        raise HTTPException(403, "ACO Operations owns assignment decisions")
    if not db.get(Patient, patient_id):
        raise HTTPException(404, "Fictional patient not found")
    assignment = db.get(Assignment, patient_id)
    if not assignment:
        assignment = Assignment(patient_id=patient_id, history=[])
        db.add(assignment)
    assignment.history = assignment.history + [request.model_dump(mode="json") | {"created_at": timestamp()}]
    assignment.owner, assignment.role = request.owner, request.assigned_role
    assignment.due_date, assignment.barrier = request.due_date.isoformat(), request.barrier
    db.commit()
    return {"saved": True}