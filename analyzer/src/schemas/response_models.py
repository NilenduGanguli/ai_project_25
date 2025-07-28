from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class AnalysisMode(str, Enum):
    VECTOR = "vector"
    MULTIMODAL = "multimodal"


class RetrievedVector(BaseModel):
    page_content: str = Field(..., description="Content of the document chunk")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata associated with the chunk")


class AnalysisResponse(BaseModel):
    message: str = Field(..., description="Success message")
    mode: AnalysisMode = Field(..., description="Analysis mode used")
    search_query: str = Field(..., description="Query used for analysis")
    filename: str = Field(..., description="Name of the analyzed file")
    response: Union[str, Dict[str, Any]
                    ] = Field(..., description="Analysis result from LLM")
    analysis_type: str = Field(..., description="Type of analysis performed")
    retrieved_vectors: Optional[List[RetrievedVector]] = Field(
        None,
        description="Retrieved document chunks (for vector mode only)"
    )


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    error_type: Optional[str] = Field(None, description="Type of error")


class AnalysisRequest(BaseModel):
    search_query: str = Field(
        default="Summarize this",
        description="Query to apply to the PDF content",
        min_length=1
    )
    mode: AnalysisMode = Field(
        default=AnalysisMode.VECTOR,
        description="Analysis mode to use"
    )
