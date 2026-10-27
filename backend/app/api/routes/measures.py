from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Measure, get_db
from app.services.equity_summary import equity_summary
from app.services.population import dashboard, population


router = APIRouter(prefix="/api", tags=["Registry and evaluation"])


@router.get("/measures")
def measures(db: Session = Depends(get_db)):
    return [item.specification for item in db.scalars(select(Measure))]


@router.get("/programs")
def programs():
    return [
        {"id": "EDUCATIONAL_MSSP_CONTEXT", "enabled": True, "description": "Fictional rule; CMS resources provide context only"},
        {"id": "LEAD", "enabled": False, "description": "Distinct program; exact specifications and phased digital reporting not implemented"},
        {"id": "FICTIONAL_COMMERCIAL", "enabled": False, "description": "No real payer contract or Bluestone terms implemented"},
    ]


@router.get("/dashboard")
def overview(db: Session = Depends(get_db)):
    return dashboard(db)


@router.get("/patients")
def patients(db: Session = Depends(get_db)):
    return population(db)


@router.get("/patients/{patient_id}")
def patient(patient_id: str, db: Session = Depends(get_db)):
    row = next((row for row in population(db) if row["id"] == patient_id), None)
    if not row:
        raise HTTPException(404, "Fictional patient not found")
    return row


@router.get("/equity")
def equity(dimension: str = "facility_type", db: Session = Depends(get_db)):
    if dimension not in {"facility_type", "access_barrier"}:
        raise HTTPException(422, "Unsupported stratification")
    return equity_summary(population(db), dimension)