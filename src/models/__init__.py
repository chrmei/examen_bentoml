"""Data models for admission prediction service."""

from src.models.input_model import (
    AdmissionInput,
    BatchAdmissionInput,
    AdmissionOutput,
    BatchJobResponse,
    BatchStatusResponse,
    BatchResultsResponse,
    LoginRequest,
)

__all__ = [
    "AdmissionInput",
    "BatchAdmissionInput",
    "AdmissionOutput",
    "BatchJobResponse",
    "BatchStatusResponse",
    "BatchResultsResponse",
    "LoginRequest",
]

