from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("measures", sa.Column("id", sa.String(80), primary_key=True), sa.Column("specification", sa.JSON(), nullable=False))
    op.create_table("import_batches", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("filename", sa.String(255), nullable=False), sa.Column("created_at", sa.String(50), nullable=False), sa.Column("accepted", sa.Integer(), nullable=False), sa.Column("errors", sa.JSON(), nullable=False), sa.Column("disposition", sa.JSON(), nullable=True))
    op.create_table("patients", sa.Column("id", sa.String(40), primary_key=True), sa.Column("batch_id", sa.Integer(), sa.ForeignKey("import_batches.id"), nullable=False), sa.Column("original", sa.JSON(), nullable=False))
    op.create_table("workflow_events", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("patient_id", sa.String(40), sa.ForeignKey("patients.id"), nullable=False), sa.Column("created_at", sa.String(50), nullable=False), sa.Column("actor", sa.String(120), nullable=False), sa.Column("role", sa.String(50), nullable=False), sa.Column("provenance", sa.String(50), nullable=False), sa.Column("evidence", sa.Text(), nullable=False), sa.Column("patch", sa.JSON(), nullable=False))
    op.create_index("ix_workflow_events_patient_id", "workflow_events", ["patient_id"])
    op.create_table("assignments", sa.Column("patient_id", sa.String(40), sa.ForeignKey("patients.id"), primary_key=True), sa.Column("owner", sa.String(120), nullable=False), sa.Column("role", sa.String(50), nullable=False), sa.Column("due_date", sa.String(10), nullable=False), sa.Column("barrier", sa.String(60), nullable=False), sa.Column("history", sa.JSON(), nullable=False))
    op.create_table("snapshots", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("created_at", sa.String(50), nullable=False), sa.Column("prepared_by", sa.String(120), nullable=False), sa.Column("payload", sa.JSON(), nullable=False), sa.Column("digest", sa.String(64), nullable=False), sa.Column("signoff", sa.JSON(), nullable=True))


def downgrade():
    for table in ("snapshots", "assignments", "workflow_events", "patients", "import_batches", "measures"):
        op.drop_table(table)