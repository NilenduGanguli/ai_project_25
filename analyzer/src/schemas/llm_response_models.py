from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    response: str = Field(..., description="The detailed analysis or response to the query")
