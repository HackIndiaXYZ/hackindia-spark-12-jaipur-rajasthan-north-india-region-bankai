from typing import List
from pydantic import BaseModel, Field


class AIAnalysisResult(BaseModel):
    summary: str = Field(..., description="High-level operational summary of the incident analysis.")
    why_detected: List[str] = Field(..., description="List of evidence points explaining why the incident was classified.")
    recommended_actions: List[str] = Field(..., description="List of recommended operator actions.")
    confidence_note: str = Field(..., description="Explanation of confidence and topology correlation.")
    limitations: str = Field(..., description="Disclaimer regarding model-derived estimates and physical limitations.")


class AIAnalysisResponse(BaseModel):
    incident_id: str
    analysis: AIAnalysisResult
    provider: str = Field(..., example="gemini", description="Provider used ('gemini' or 'deterministic_fallback').")
