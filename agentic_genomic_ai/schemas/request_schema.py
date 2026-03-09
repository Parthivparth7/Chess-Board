from __future__ import annotations

from pydantic import BaseModel, Field


class ChatQuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User genomic question")
    analysis_summary: str | None = Field(default=None, description="Optional analysis summary context")
