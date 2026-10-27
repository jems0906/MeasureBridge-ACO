from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Patient, WorkflowEvent, get_db
from app.schemas import WorkflowInput
from app.services.measure_engine import evaluate
from app.services.population import population, specification


router = APIRouter(prefix="/api/workflows", tags=["Simulated point of care"])


@router.post("/{patient_id}")
def document(patient_id: str, request: WorkflowInput, db: Session = Depends(get_db)):
    patient = db.scalar(select(Patient).where(Patient.id == patient_id).with_for_update())
    if not patient:
        raise HTTPException(404, "Fictional patient not found")
    row = next(row for row in population(db) if row["id"] == patient_id)
    latest = row["events"][-1]["id"] if row["events"] else 0
    if request.expected_event_id != latest:
        raise HTTPException(409, "Record changed; reload before saving")
    if row["result"]["status"] in {"met", "excluded"}:
        raise HTTPException(409, "No editable gap; original and completed evidence are preserved")
    category = row["result"]["category"]
    if row["record"]["documentation_status"] == "patient_declined":
        raise HTTPException(409, "Patient preference is preserved; no automatic completion")
    allowed = {"documentation_completion": {"missing_documentation"}, "data_repair": {"data_pipeline_defect"}, "simulated_care_event": {"true_care_gap", "missing_documentation"}}
    if category not in allowed[request.provenance]:
        raise HTTPException(422, "Provenance does not match the classified gap")
    roles = {"documentation_completion": {"Clinical Assistant", "Provider"}, "data_repair": {"EHR/IT"}, "simulated_care_event": {"Provider"}}
    if request.role not in roles[request.provenance]:
        raise HTTPException(403, "Role cannot perform this workflow action")
    patch = request.model_dump(mode="json", include={"documentation_status", "observation_date", "systolic", "diastolic", "units"})
    if request.documentation_status != "completed" and any(patch[field] is not None for field in ("observation_date", "systolic", "diastolic")):
        raise HTTPException(422, "Non-completed status cannot contain observation values")
    outcome = evaluate(row["record"] | patch, specification(db))
    if outcome["status"] == "unresolved":
        raise HTTPException(422, outcome["reason"])
    event = WorkflowEvent(patient_id=patient_id, actor=request.actor, role=request.role, provenance=request.provenance, evidence=request.evidence, patch=patch)
    db.add(event)
    db.commit()
    return {"event_id": event.id, "result": outcome}