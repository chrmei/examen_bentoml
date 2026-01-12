"""Pydantic models for admission prediction API."""

from pydantic import BaseModel, Field, field_validator
from typing import List


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class AdmissionInput(BaseModel):
    """Single admission prediction input model."""
    gre_score: float = Field(..., ge=0, le=340, description="GRE test score (0-340)")
    toefl_score: float = Field(..., ge=0, le=120, description="TOEFL test score (0-120)")
    university_rating: float = Field(..., ge=1, le=5, description="University rating (1-5)")
    sop: float = Field(..., ge=1, le=5, description="Statement of Purpose (1-5)")
    lor: float = Field(..., ge=1, le=5, description="Letter of Recommendation (1-5)")
    cgpa: float = Field(..., ge=0, le=10, description="Cumulative GPA (0-10)")
    research: int = Field(..., ge=0, le=1, description="Research experience (0 or 1)")


class BatchAdmissionInput(BaseModel):
    """Batch admission prediction input model."""
    inputs: List[AdmissionInput] = Field(..., min_length=1, description="List of admission inputs")

    @field_validator("inputs")
    @classmethod
    def validate_batch_size(cls, v: List[AdmissionInput]) -> List[AdmissionInput]:
        """Validate batch size does not exceed maximum."""
        if len(v) > 1000:
            raise ValueError("Batch size cannot exceed 1000 records")
        return v


class AdmissionOutput(BaseModel):
    """Single admission prediction output model."""
    chance_of_admit: float = Field(..., ge=0, le=1, description="Predicted chance of admission (0-1)")


class BatchJobResponse(BaseModel):
    """Batch job submission response model."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status (pending)")
    message: str = Field(..., description="Status message")


class BatchStatusResponse(BaseModel):
    """Batch job status response model."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status (pending/processing/completed/failed)")


class BatchResultsResponse(BaseModel):
    """Batch prediction results response model."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    results: List[AdmissionOutput] = Field(..., description="List of prediction results")
    total: int = Field(..., description="Total number of predictions")

