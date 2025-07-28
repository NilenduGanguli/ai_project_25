from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnalysisMode(str, Enum):
    VECTOR = "vector"
    MULTIMODAL = "multimodal"


class SummaryType(str, Enum):
    COMPREHENSIVE = "comprehensive"
    BRIEF = "brief"
    DETAILED = "detailed"


class SummaryResponse(BaseModel):
    message: str = Field(..., description="Success message")
    mode: AnalysisMode = Field(..., description="Summarization mode used")
    summary_type: str = Field(..., description="Type of summary requested")
    filename: str = Field(..., description="Name of the summarized file")
    summary: str = Field(..., description="Generated summary of the document")
    key_points: List[str] = Field(..., description="Key points extracted from the document")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    error_type: Optional[str] = Field(None, description="Type of error")


class SummaryRequest(BaseModel):
    summary_type: SummaryType = Field(
        default=SummaryType.COMPREHENSIVE,
        description="Type of summary to generate"
    )
    mode: AnalysisMode = Field(
        default=AnalysisMode.VECTOR,
        description="Summarization mode to use"
    )
