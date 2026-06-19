from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from .config import Settings
from .embeddings import embedding_dimension
from .models import Chunk


class QdrantVectorStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None, timeout=30)

    def ensure_collection(self) -> None:
        existing = {collection.name for collection in self.client.get_collections().collections}
        if self.settings.qdrant_collection in existing:
            return
        self.client.create_collection(
            collection_name=self.settings.qdrant_collection,
            vectors_config=qm.VectorParams(size=embedding_dimension(), distance=qm.Distance.COSINE),
            hnsw_config=qm.HnswConfigDiff(m=16, ef_construct=100, full_scan_threshold=10000),
            optimizers_config=qm.OptimizersConfigDiff(default_segment_number=2),
        )
        self.client.create_payload_index(
            collection_name=self.settings.qdrant_collection,
            field_name="document_id",
            field_schema=qm.PayloadSchemaType.KEYWORD,
        )

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        self.ensure_collection()
        points = [
            qm.PointStruct(
                id=chunk.id,
                vector=vector,
                payload={
                    "document_id": chunk.document_id,
                    "filename": chunk.filename,
                    "text": chunk.text,
                    "heading": chunk.heading,
                    "page": chunk.page,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert(collection_name=self.settings.qdrant_collection, points=points, wait=True)

    def search(self, vector: list[float], limit: int) -> list[tuple[str, float]]:
        self.ensure_collection()
        results = self.client.search(
            collection_name=self.settings.qdrant_collection,
            query_vector=vector,
            limit=limit,
            with_payload=False,
            score_threshold=None,
            search_params=qm.SearchParams(hnsw_ef=128, exact=False),
        )
        return [(str(result.id), float(result.score)) for result in results]
