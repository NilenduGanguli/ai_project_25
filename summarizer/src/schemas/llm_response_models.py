from pydantic import BaseModel, Field
from typing import List


class LLMSummaryResponse(BaseModel):
    summary: str = Field(..., description="The comprehensive summary of the document")
    summary_type: str = Field(..., description="Type of summary generated (comprehensive, brief, detailed)")
    key_points: List[str] = Field(..., description="Key points extracted from the document") 