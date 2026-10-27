from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ImportBatch, get_db, timestamp
from app.schemas import ReviewInput
from app.services.population import ingest


router = APIRouter(prefix="/api/imports", tags=["Synthetic imports"])


def batch_json(batch: ImportBatch) -> dict:
    return {"id": batch.id, "filename": batch.filename, "created_at": batch.created_at, "accepted": batch.accepted, "errors": batch.errors, "disposition": batch.disposition}


@router.get("")
def list_imports(db: Session = Depends(get_db)):
    return [batch_json(batch) for batch in db.scalars(select(ImportBatch).order_by(ImportBatch.id.desc()))]


@router.post("")
async def upload(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read(2_000_001)
    if len(content) > 2_000_000:
        raise HTTPException(413, "CSV exceeds 2 MB")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(422, "CSV must be UTF-8")
    return batch_json(ingest(db, text, Path((file.filename or "upload.csv").replace("\\", "/")).name[:255]))


@router.post("/{batch_id}/disposition")
def disposition(batch_id: int, request: ReviewInput, db: Session = Depends(get_db)):
    if request.role != "ACO Operations":
        raise HTTPException(403, "ACO Operations must review ingestion errors")
    batch = db.get(ImportBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Import not found")
    if batch.disposition or not batch.errors:
        raise HTTPException(409, "No open import errors")
    batch.disposition = request.model_dump() | {"created_at": timestamp(), "action": "Rejected rows reviewed; not silently added to denominator"}
    db.commit()
    return batch_json(batch)