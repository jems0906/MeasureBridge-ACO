from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import settings


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


class Measure(Base):
    __tablename__ = "measures"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    specification: Mapped[dict] = mapped_column(JSON)


class ImportBatch(Base):
    __tablename__ = "import_batches"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[str] = mapped_column(String(50), default=timestamp)
    accepted: Mapped[int]
    errors: Mapped[list] = mapped_column(JSON, default=list)
    disposition: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"))
    original: Mapped[dict] = mapped_column(JSON)


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    created_at: Mapped[str] = mapped_column(String(50), default=timestamp)
    actor: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(50))
    provenance: Mapped[str] = mapped_column(String(50))
    evidence: Mapped[str] = mapped_column(Text)
    patch: Mapped[dict] = mapped_column(JSON)


class Assignment(Base):
    __tablename__ = "assignments"
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), primary_key=True)
    owner: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(50))
    due_date: Mapped[str] = mapped_column(String(10))
    barrier: Mapped[str] = mapped_column(String(60))
    history: Mapped[list] = mapped_column(JSON, default=list)


class Snapshot(Base):
    __tablename__ = "snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[str] = mapped_column(String(50), default=timestamp)
    prepared_by: Mapped[str] = mapped_column(String(120))
    payload: Mapped[dict] = mapped_column(JSON)
    digest: Mapped[str] = mapped_column(String(64))
    signoff: Mapped[dict | None] = mapped_column(JSON, nullable=True)


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    with SessionLocal() as session:
        yield session