from functools import lru_cache

from .config import get_settings
from .database import ChunkStore
from .document_parser import DocumentParser
from .rag_chain import GroqRagChain
from .retrieval import HybridRetriever
from .vector_store import QdrantVectorStore


@lru_cache
def get_chunk_store() -> ChunkStore:
    return ChunkStore(get_settings().sqlite_path)


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore(get_settings())


@lru_cache
def get_parser() -> DocumentParser:
    return DocumentParser()


@lru_cache
def get_retriever() -> HybridRetriever:
    return HybridRetriever(get_settings(), get_chunk_store(), get_vector_store())


@lru_cache
def get_rag_chain() -> GroqRagChain:
    return GroqRagChain(get_settings())
