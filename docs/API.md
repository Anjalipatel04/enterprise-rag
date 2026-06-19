# API

## `GET /health`

Returns service, model, and vector-store health.

## `POST /upload`

Multipart form-data:

- `files`: one or more PDF, DOCX, or PPTX files.
- `chunk_size`: optional integer.
- `chunk_overlap`: optional integer.

Returns document ids and indexed chunk counts.

## `POST /chat`

JSON body:

```json
{
  "question": "What does the policy say about refunds?",
  "top_k": 5,
  "similarity_threshold": 0.35
}
```

Returns a grounded answer and citations.
