from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    page: int | None = None
    heading: str | None = None
    score: float
    text: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float | None = Field(default=None, ge=0, le=1)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    grounded: bool
    refused: bool = False


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str
    qdrant_collection: str
    embedding_model: str
    reranker_model: str
