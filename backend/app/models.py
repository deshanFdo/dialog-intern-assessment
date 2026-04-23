from __future__ import annotations

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    chunks_added: int
    total_chunks: int
    source: str


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=10)
    conversation_id: str | None = None


class SourceChunk(BaseModel):
    id: int
    score: float
    text: str
    source: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
