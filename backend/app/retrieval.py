import re

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from .config import Settings
from .database import ChunkStore
from .embeddings import embed_texts
from .models import RetrievedChunk
from .vector_store import QdrantVectorStore


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


class HybridRetriever:
    def __init__(self, settings: Settings, store: ChunkStore, vectors: QdrantVectorStore) -> None:
        self.settings = settings
        self.store = store
        self.vectors = vectors
        self.reranker = CrossEncoder(settings.reranker_model)

    def retrieve(self, question: str, top_k: int) -> list[RetrievedChunk]:
        candidate_limit = max(top_k * 5, 20)
        query_vector = embed_texts([question])[0]
        dense_hits = self.vectors.search(query_vector, candidate_limit)
        dense_rank = {chunk_id: (rank, score) for rank, (chunk_id, score) in enumerate(dense_hits, start=1)}

        all_chunks = self.store.all_chunks()
        bm25_rank: dict[str, tuple[int, float]] = {}
        if all_chunks:
            bm25 = BM25Okapi([tokenize(chunk.text) for chunk in all_chunks])
            scores = bm25.get_scores(tokenize(question))
            ranked = sorted(zip(all_chunks, scores, strict=True), key=lambda item: item[1], reverse=True)[:candidate_limit]
            bm25_rank = {chunk.id: (rank, float(score)) for rank, (chunk, score) in enumerate(ranked, start=1)}

        ids = set(dense_rank) | set(bm25_rank)
        fused: list[RetrievedChunk] = []
        for chunk_id in ids:
            chunk = self.store.get_chunk(chunk_id)
            if chunk is None:
                continue
            dense_score = dense_rank.get(chunk_id, (999, 0.0))[1]
            bm25_score = bm25_rank.get(chunk_id, (999, 0.0))[1]
            fused_score = 0.0
            if chunk_id in dense_rank:
                fused_score += 1.0 / (60 + dense_rank[chunk_id][0])
            if chunk_id in bm25_rank:
                fused_score += 1.0 / (60 + bm25_rank[chunk_id][0])
            fused.append(RetrievedChunk(chunk=chunk, dense_score=dense_score, bm25_score=bm25_score, fused_score=fused_score))

        fused.sort(key=lambda item: item.fused_score, reverse=True)
        rerank_candidates = fused[:candidate_limit]
        if not rerank_candidates:
            return []

        pairs = [(question, item.chunk.text) for item in rerank_candidates]
        rerank_scores = self.reranker.predict(pairs).tolist()
        reranked = [
            RetrievedChunk(
                chunk=item.chunk,
                dense_score=item.dense_score,
                bm25_score=item.bm25_score,
                fused_score=item.fused_score,
                rerank_score=float(score),
            )
            for item, score in zip(rerank_candidates, rerank_scores, strict=True)
        ]
        reranked.sort(key=lambda item: item.rerank_score, reverse=True)
        return reranked[:top_k]
