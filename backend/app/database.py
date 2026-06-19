import sqlite3
from pathlib import Path

from .models import Chunk


class ChunkStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                  id TEXT PRIMARY KEY,
                  document_id TEXT NOT NULL,
                  filename TEXT NOT NULL,
                  text TEXT NOT NULL,
                  heading TEXT,
                  page INTEGER
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id)")

    def upsert_chunks(self, chunks: list[Chunk]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO chunks(id, document_id, filename, text, heading, page)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  document_id=excluded.document_id,
                  filename=excluded.filename,
                  text=excluded.text,
                  heading=excluded.heading,
                  page=excluded.page
                """,
                [(c.id, c.document_id, c.filename, c.text, c.heading, c.page) for c in chunks],
            )

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,)).fetchone()
        return self._row_to_chunk(row) if row else None

    def all_chunks(self) -> list[Chunk]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM chunks").fetchall()
        return [self._row_to_chunk(row) for row in rows]

    @staticmethod
    def _row_to_chunk(row: sqlite3.Row) -> Chunk:
        return Chunk(
            id=row["id"],
            document_id=row["document_id"],
            filename=row["filename"],
            text=row["text"],
            heading=row["heading"],
            page=row["page"],
        )
