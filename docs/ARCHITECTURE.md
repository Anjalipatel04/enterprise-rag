# Architecture

Documents are parsed by Docling into markdown-like structured text. The backend preserves headings, tables, and list formatting in chunk metadata, creates semantic chunks, embeds chunks using `BAAI/bge-small-en-v1.5`, indexes dense vectors in Qdrant HNSW, and stores BM25-ready text locally in SQLite.

Queries run through prompt-injection detection, dense Qdrant search, local BM25 search, reciprocal-rank fusion, cross-encoder reranking, similarity threshold validation, and Gemini answer generation. Grounded-answer enforcement rejects unsupported answers.
