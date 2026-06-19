import re
from uuid import NAMESPACE_URL, uuid4, uuid5

from .models import Chunk, ParsedSection


class SemanticChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, sections: list[ParsedSection], filename: str, document_id: str | None = None) -> list[Chunk]:
        doc_id = document_id or str(uuid4())
        chunks: list[Chunk] = []
        for section in sections:
            for text in self._split_section(section.text):
                point_id = str(uuid5(NAMESPACE_URL, f"{doc_id}:{len(chunks)}:{text}"))
                chunks.append(
                    Chunk(
                        id=point_id,
                        document_id=doc_id,
                        filename=filename,
                        text=text,
                        heading=section.heading,
                        page=section.page,
                    )
                )
        return chunks

    def _split_section(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            candidate = f"{current} {sentence}".strip()
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = sentence

            while len(current) > self.chunk_size:
                chunks.append(current[: self.chunk_size])
                current = current[self.chunk_size - self.chunk_overlap :]

        if current:
            chunks.append(current)

        if self.chunk_overlap <= 0 or len(chunks) < 2:
            return chunks

        overlapped: list[str] = [chunks[0]]
        for idx in range(1, len(chunks)):
            prefix = chunks[idx - 1][-self.chunk_overlap :]
            overlapped.append(f"{prefix}\n{chunks[idx]}")
        return overlapped
