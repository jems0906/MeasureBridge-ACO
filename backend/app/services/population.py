import json

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import ROOT
from app.models import Assignment, ImportBatch, Measure, Patient, WorkflowEvent
from app.services.measure_engine import evaluate, summarize
from app.services.validation import parse_csv


MEASURE_KEY = "EDU-DOC-2026:1.0.0"


def specification(db: Session) -> dict:
    measure = db.get(Measure, MEASURE_KEY)
    if not measure:
        raise HTTPException(409, "Run seed_demo to register the educational specification")
    return measure.specification


def population(db: Session) -> list[dict]:
    spec = specification(db)
    events: dict[str, list] = {}
    for event in db.scalars(select(WorkflowEvent).order_by(WorkflowEvent.id)):
        events.setdefault(event.patient_id, []).append(event)
    assignments = {item.patient_id: item for item in db.scalars(select(Assignment))}
    rows = []
    for patient in db.scalars(select(Patient).order_by(Patient.id)):
        history = events.get(patient.id, [])
        effective = dict(patient.original)
        for event in history:
            effective.update(event.patch)
        result = evaluate(effective, spec)
        assignment = assignments.get(patient.id)
        rows.append({
            "id": patient.id, "original": patient.original, "record": effective,
            "result": result, "baseline_result": evaluate(patient.original, spec),
            "events": [{"id": event.id, "actor": event.actor, "role": event.role, "provenance": event.provenance, "evidence": event.evidence, "created_at": event.created_at, "patch": event.patch} for event in history],
            "assignment": {"owner": assignment.owner, "role": assignment.role, "due_date": assignment.due_date, "barrier": assignment.barrier, "history": assignment.history} if assignment else None,
        })
    return rows


def ingest(db: Session, content: str, filename: str) -> ImportBatch:
    accepted, errors = parse_csv(content, set(db.scalars(select(Patient.id))), filename)
    batch = ImportBatch(filename=filename, accepted=len(accepted), errors=errors)
    db.add(batch)
    db.flush()
    for record in accepted:
        db.add(Patient(id=record["patient_id"], batch_id=batch.id, original=record))
    db.commit()
    return batch


def seed(db: Session) -> None:
    if not db.get(Measure, MEASURE_KEY):
        spec = json.loads((ROOT / "fixtures/educational_measure_v1.json").read_text())
        db.add(Measure(id=MEASURE_KEY, specification=spec))
        db.commit()
    if not db.scalar(select(Patient.id).limit(1)):
        ingest(db, (ROOT / "fixtures/synthetic_population.csv").read_text(), "synthetic_population.csv")
        for row in population(db):
            if row["result"]["status"] != "met":
                category = row["result"]["category"]
                role = {"missing_documentation": "Clinical Assistant", "true_care_gap": "Provider", "patient_preference": "Provider", "data_pipeline_defect": "EHR/IT", "eligibility_question": "ACO Operations"}[category]
                db.add(Assignment(patient_id=row["id"], owner={"Clinical Assistant": "Jamie Chen", "Provider": "Dr. Alex Morgan", "EHR/IT": "Taylor Reed", "ACO Operations": "Sam Rivera"}[role], role=role, due_date="2026-11-06", barrier=category, history=[]))
        db.commit()


def dashboard(db: Session) -> dict:
    rows = population(db)
    current = summarize([row["result"] for row in rows])
    baseline = summarize([row["baseline_result"] for row in rows])
    changes = {key: 0 for key in ("documentation_completion", "data_repair", "simulated_care_event")}
    for row in rows:
        if row["baseline_result"]["status"] != "met" and row["result"]["status"] == "met" and row["events"]:
            changes[row["events"][-1]["provenance"]] += 1
    batches = list(db.scalars(select(ImportBatch)))
    return {"current": current, "baseline": baseline, "changes": changes, "open_import_errors": sum(len(batch.errors) for batch in batches if not batch.disposition), "specification": specification(db)}