from typing import Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator

class IngestRequest(BaseModel):
    type: Literal["text", "url"]
    content: str = Field(min_length=5, max_length=100_000)

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, value: str):
        if not value.strip():
            raise ValueError("Content cannot be blank")
        return value.strip()

class IngestResponse(BaseModel):
    id: int
    title: str
    source_type: str
    chunk_count: int
    message: str

class ItemResponse(BaseModel):
    id: int
    title: str
    source_type: str
    source_url: str | None
    created_at: str
    preview: str

class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)

class SourceResponse(BaseModel):
    chunk_id: int
    item_id: int
    title: str
    source_type: str
    source_url: str | None
    snippet: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
