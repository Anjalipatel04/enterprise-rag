from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedSection:
    text: str
    heading: str | None
    page: int | None


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    filename: str
    text: str
    heading: str | None
    page: int | None


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    dense_score: float = 0.0
    bm25_score: float = 0.0
    fused_score: float = 0.0
    rerank_score: float = 0.0
