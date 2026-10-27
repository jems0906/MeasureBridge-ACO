import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ImportBatch, Snapshot
from app.services.equity_summary import equity_summary
from app.services.measure_engine import summarize
from app.services.population import population, specification


def digest(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def freeze(db: Session, actor: str) -> Snapshot:
    rows = population(db)
    counts = summarize([row["result"] for row in rows])
    imports = [{"id": batch.id, "filename": batch.filename, "accepted": batch.accepted, "errors": batch.errors, "disposition": batch.disposition} for batch in db.scalars(select(ImportBatch).order_by(ImportBatch.id))]
    blockers = []
    if not rows:
        blockers.append("Empty population")
    if counts["unresolved"]:
        blockers.append(f"{counts['unresolved']} unresolved calculation or eligibility records")
    if any(batch["errors"] and not batch["disposition"] for batch in imports):
        blockers.append("Undispositioned import errors")
    reconciled = counts["total"] == counts["numerator"] + counts["not_met"] + counts["unresolved"] + counts["excluded"] and sum(batch["accepted"] for batch in imports) == counts["total"]
    if not reconciled:
        blockers.append("Reconciliation mismatch")
    payload = {
        "label": "INTERNAL EDUCATIONAL PACKAGE - NOT A CMS SUBMISSION",
        "specification": specification(db), "counts": counts, "rows": rows, "imports": imports,
        "baseline_counts": summarize([row["baseline_result"] for row in rows]),
        "reconciliation": {"passed": reconciled, "unique_patient_ids": len({row["id"] for row in rows}), "accepted_import_rows": sum(batch["accepted"] for batch in imports)},
        "blockers": blockers,
        "equity": {dimension: equity_summary(rows, dimension) for dimension in ("facility_type", "access_barrier")},
    }
    snapshot = Snapshot(prepared_by=actor, payload=payload, digest=digest(payload))
    db.add(snapshot)
    db.commit()
    return snapshot