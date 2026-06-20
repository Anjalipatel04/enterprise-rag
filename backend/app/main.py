from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .chunking import SemanticChunker
from .config import get_settings
from .dependencies import get_chunk_store, get_parser, get_rag_chain, get_retriever, get_vector_store
from .document_parser import SUPPORTED_EXTENSIONS
from .embeddings import embed_texts
from .guardrails import detect_prompt_injection, enforce_grounding, passes_similarity_threshold
from .schemas import ChatRequest, ChatResponse, Citation, HealthResponse, UploadResponse

settings = get_settings()
app = FastAPI(title="Enterprise Document QA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    get_vector_store().ensure_collection()

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    get_vector_store().ensure_collection()
    return HealthResponse(
        status="ok",
        qdrant_collection=settings.qdrant_collection,
        embedding_model=settings.embedding_model,
        reranker_model=settings.reranker_model,
    )


@app.post("/upload", response_model=list[UploadResponse])
async def upload(
    files: list[UploadFile] = File(...),
    chunk_size: int = Form(default=settings.default_chunk_size),
    chunk_overlap: int = Form(default=settings.default_chunk_overlap),
) -> list[UploadResponse]:

    if chunk_size < 200 or chunk_size > 3000:
        raise HTTPException(status_code=422, detail="chunk_size must be between 200 and 3000")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise HTTPException(
            status_code=422,
            detail="chunk_overlap must be non-negative and smaller than chunk_size",
        )

    parser = get_parser()
    store = get_chunk_store()
    vector_store = get_vector_store()

    responses: list[UploadResponse] = []

    for file in files:
        suffix = Path(file.filename or "").suffix.lower()

        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {suffix}",
            )

        content = await file.read()

        if len(content) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"{file.filename} exceeds {settings.max_upload_mb}MB",
            )

        document_id = str(uuid4())

        stored_path = settings.storage_dir / f"{document_id}{suffix}"
        stored_path.write_bytes(content)

        sections = parser.parse(stored_path)

        chunks = SemanticChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        ).chunk(
            sections=sections,
            filename=file.filename or stored_path.name,
            document_id=document_id,
        )

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail=f"No extractable content found in {file.filename}",
            )

        vectors = embed_texts([chunk.text for chunk in chunks])

        print("\n===== ALL GENERATED CHUNKS =====")

        for i, chunk in enumerate(chunks, start=1):
            print(f"\nCHUNK {i}")
            print(chunk.text[:800])

        print("\n===== END GENERATED CHUNKS =====")

        vector_store.upsert(chunks, vectors)
        store.upsert_chunks(chunks)

        responses.append(
            UploadResponse(
                document_id=document_id,
                filename=file.filename or stored_path.name,
                chunks_indexed=len(chunks),
            )
        )

    return responses

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if detect_prompt_injection(request.question):
        return ChatResponse(
            answer="I cannot follow instructions that attempt to override system behavior. Ask a question about the uploaded documents.",
            citations=[],
            grounded=True,
            refused=True,
        )

    threshold = request.similarity_threshold if request.similarity_threshold is not None else settings.similarity_threshold
    retrieved = get_retriever().retrieve(
    request.question,
    max(request.top_k, 10)
    )
    if not passes_similarity_threshold(retrieved, threshold):
        return ChatResponse(
            answer="I don't know based on the provided documents.",
            citations=[],
            grounded=True,
        )

    answer = get_rag_chain().answer(request.question, retrieved)
    grounded = enforce_grounding(answer, retrieved)
    if not grounded:
        answer = "I don't know based on the provided documents."

    citations = [
        Citation(
            document_id=item.chunk.document_id,
            filename=item.chunk.filename,
            chunk_id=item.chunk.id,
            page=item.chunk.page,
            heading=item.chunk.heading,
            score=item.rerank_score,
            text=item.chunk.text,
        )
        for item in retrieved
    ]
    return ChatResponse(answer=answer, citations=citations, grounded=grounded)
