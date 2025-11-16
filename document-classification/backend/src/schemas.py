from pydantic import BaseModel, Field
from typing import List


class PageClassification(BaseModel):
    page: int = Field(description="Page number")
    document_type: str = Field(
        description="Type of document identified on this page")
    confidence: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Reasoning for the classification")


class ClassificationResponse(BaseModel):
    page_classifications: List[PageClassification] = Field(
        description="Brief page-by-page classifications with reasoning and confidence")
