from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AnalysisMode(str, Enum):
    VECTOR = "vector"
    MULTIMODAL = "multimodal"


class SentimentResult(BaseModel):
    sentiment: str = Field(..., description="One of 'positive', 'negative', or 'neutral'")
    score: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")
    summary: str = Field(..., description="Brief explanation of the sentiment determination")


class SentimentAnalysisResponse(BaseModel):
    message: str = Field(..., description="Success message")
    mode: AnalysisMode = Field(..., description="Analysis mode used")
    filename: Optional[str] = Field(None, description="Name of the analyzed file")
    result: SentimentResult = Field(..., description="Sentiment analysis result")


class TextSentimentRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for sentiment", min_length=1)


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    error_type: Optional[str] = Field(None, description="Type of error")
