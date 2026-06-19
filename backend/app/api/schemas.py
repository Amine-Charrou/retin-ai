"""
RetinAI Backend — Pydantic Schemas
Request / Response models for the API.
"""
from pydantic import BaseModel
from typing import Optional


class PatientCreate(BaseModel):
    id: str
    name: str
    birthdate: Optional[str] = None
    gender: str = "M"


class PatientOut(BaseModel):
    id: str
    name: str
    birthdate: Optional[str] = None
    gender: str


class AnalysisOut(BaseModel):
    id: str
    patient_id: str
    patient_name: Optional[str] = None
    patient_gender: Optional[str] = None
    stage: int
    confidence: float
    referable: int
    urgency: Optional[str] = None
    image_path: str
    heatmap_path: str
    description: Optional[str] = None
    clinical_report: Optional[str] = None
    pdf_url: Optional[str] = None
    created_at: str
