from pydantic import BaseModel, Field


class LLMSentimentResponse(BaseModel):
    sentiment: str = Field(..., description="One of 'positive', 'negative', or 'neutral'")
    score: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")
    summary: str = Field(..., description="Brief explanation of the sentiment determination") 