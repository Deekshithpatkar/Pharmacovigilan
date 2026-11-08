from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.ai.extraction import ExtractedCaseInfo
from app.ai.label_retrieval import LabelEvidence

class ReporterType(str, Enum):
    PATIENT = "patient"
    NURSE = "nurse"
    DOCTOR = "doctor"
    PHARMACIST = "pharmacist"
    OTHER = "other"

class CaseStatus(str, Enum):
    SUBMITTED = "submitted"
    NEEDS_INFO = "needs_information"
    PROCESSING = "processing"
    HUMAN_REVIEW = "human_review"
    COMPLETED = "completed"

class AdverseEventCaseCreate(BaseModel):
    """Information submitted by the reporter"""
    model_config = ConfigDict(str_strip_whitespace=True)
    reporter_type: ReporterType
    patient_age: Optional[int] = Field(default=None, ge=0, le=130, description="patient age in years")
    patient_sex: Optional[str] = Field(default=None, description="patient sex")
    suspected_drug: str = Field(min_length=1, max_length=200, description="name the suspected medicine")
    reaction_description: str = Field(min_length=5, max_length=5000, description="description of the suspected adverse event")
    drug_start_date: Optional[date] = None
    reaction_start_date: Optional[date] = None
    outcome: Optional[str] = Field(default=None, max_length=100)
    additional_information: Optional[str] = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def validate_dates(self):
        if (self.drug_start_date is not None and self.reaction_start_date is not None and self.reaction_start_date < self.drug_start_date):
            raise ValueError('reaction start date cannot be before drug start date')
        return self

class AdverseEventCaseResponse(BaseModel):
    """case information returned by API"""
    case_id: str
    status: CaseStatus
    message: str
    duplicate_of: Optional[str] = None
    extracted_info: Optional[ExtractedCaseInfo] = None
    evidence: List[LabelEvidence] = Field(default_factory=list)
    triage_priority: Optional[str] = None
    requires_human_review: Optional[bool] = None
    review_reason: Optional[str] = None
