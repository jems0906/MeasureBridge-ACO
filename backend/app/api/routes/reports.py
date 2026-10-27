import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Snapshot, get_db, timestamp
from app.schemas import FreezeInput, ReviewInput
from app.services.reporting_snapshots import digest, freeze


router = APIRouter(prefix="/api/reports", tags=["Internal reporting packages"])


def summary(snapshot: Snapshot) -> dict:
    return {"id": snapshot.id, "created_at": snapshot.created_at, "prepared_by": snapshot.prepared_by, "digest": snapshot.digest, "counts": snapshot.payload["counts"], "blockers": snapshot.payload["blockers"], "reconciliation": snapshot.payload["reconciliation"], "signoff": snapshot.signoff}


@router.get("")
def reports(db: Session = Depends(get_db)):
    return [summary(item) for item in db.scalars(select(Snapshot).order_by(Snapshot.id.desc()))]


@router.post("")
def create(request: FreezeInput, db: Session = Depends(get_db)):
    if request.role != "ACO Operations":
        raise HTTPException(403, "ACO Operations prepares reporting packages")
    return summary(freeze(db, request.actor))


@router.post("/{snapshot_id}/signoff")
def signoff(snapshot_id: int, request: ReviewInput, db: Session = Depends(get_db)):
    snapshot = db.scalar(select(Snapshot).where(Snapshot.id == snapshot_id).with_for_update())
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    if request.role != "ACO Operations" or request.actor.casefold() == snapshot.prepared_by.casefold():
        raise HTTPException(403, "A different ACO Operations reviewer must sign off")
    if snapshot.signoff or snapshot.payload["blockers"]:
        raise HTTPException(409, "Already signed or frozen blockers remain; resolve live data and freeze a new version")
    if digest(snapshot.payload) != snapshot.digest:
        raise HTTPException(409, "Snapshot integrity check failed")
    snapshot.signoff = request.model_dump() | {"created_at": timestamp(), "digest": snapshot.digest}
    db.commit()
    return summary(snapshot)


@router.get("/{snapshot_id}/export")
def export(snapshot_id: int, format: str = "json", db: Session = Depends(get_db)):
    import json

    snapshot = db.get(Snapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    if format not in {"csv", "json"}:
        raise HTTPException(422, "Export format must be csv or json")
    if digest(snapshot.payload) != snapshot.digest:
        raise HTTPException(409, "Snapshot integrity check failed")
    headers = {"Content-Disposition": f'attachment; filename="INTERNAL-EDUCATIONAL-snapshot-{snapshot.id}.{format}"'}
    if format == "json":
        return Response(json.dumps(summary(snapshot) | {"package": snapshot.payload}, indent=2), media_type="application/json", headers=headers)
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["package_label", "snapshot_id", "review_status", "digest", "patient_id", "status", "eligible", "reason", "category", "rule_version", "source_fixture", "source_row", "event_ids", "provenance"])
    for row in snapshot.payload["rows"]:
        result = row["result"]
        writer.writerow([snapshot.payload["label"], snapshot.id, "signed" if snapshot.signoff else "DRAFT_NOT_APPROVED", snapshot.digest, row["id"], result["status"], result["eligible"], result["reason"], result["category"], result["rule_version"], result["source_fixture"], result["source_row"], ";".join(str(event["id"]) for event in row["events"]), ";".join(event["provenance"] for event in row["events"])])
    return Response(stream.getvalue(), media_type="text/csv", headers=headers)