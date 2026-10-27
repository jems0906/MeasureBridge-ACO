from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Role = Literal["Provider", "Clinical Assistant", "ACO Operations", "EHR/IT"]


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Identity(StrictInput):
    actor: str = Field(min_length=2, max_length=120)
    role: Role


class WorkflowInput(Identity):
    provenance: Literal["documentation_completion", "data_repair", "simulated_care_event"]
    evidence: str = Field(min_length=10, max_length=2000)
    documentation_status: Literal["completed", "not_documented", "not_completed", "patient_declined"]
    observation_date: date | None = None
    systolic: float | None = Field(default=None, ge=50, le=300, allow_inf_nan=False)
    diastolic: float | None = Field(default=None, ge=30, le=200, allow_inf_nan=False)
    units: Literal["mmHg"] = "mmHg"
    expected_event_id: int = Field(default=0, ge=0)


class AssignmentInput(Identity):
    owner: str = Field(min_length=2, max_length=120)
    assigned_role: Role
    due_date: date
    barrier: Literal["missing_documentation", "true_care_gap", "patient_preference", "data_pipeline_defect", "eligibility_question", "transport", "language", "none"]


class ReviewInput(Identity):
    evidence: str = Field(min_length=10, max_length=2000)


class FreezeInput(Identity):
    pass