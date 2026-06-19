# Enterprise Document QA System

Production-ready RAG system with a Next.js 15 frontend, FastAPI backend, Docling document parsing, Qdrant hybrid retrieval, reranking, Gemini generation, and RAGAS evaluation.

## Structure

```text
enterprise-rag/
  frontend/
  backend/
  evaluation/
  docs/
  docker-compose.yml
```

## Local Development

1. Copy environment files:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env.local
```

2. Configure Qdrant.

Recommended if you do not have Docker: create a free Qdrant Cloud cluster and set these in `backend\.env`:

```powershell
QDRANT_URL=https://your-cluster-url.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key
```

Optional local Docker path, only if Docker Desktop is installed:

```powershell
docker compose up -d qdrant
```

3. Backend:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Deployment

### Railway Backend

1. Create a Railway project from `backend/`.
2. Set environment variables from `backend/.env.example`.
3. Add a Qdrant Cloud cluster and set `QDRANT_URL` and `QDRANT_API_KEY`.
4. Set `GEMINI_API_KEY`.
5. Railway will use `backend/Dockerfile` and `backend/railway.json`.

You do not need Docker installed locally for Railway deployment. Railway builds the Docker image in the cloud.

### Vercel Frontend

1. Create a Vercel project from `frontend/`.
2. Set `NEXT_PUBLIC_API_BASE_URL` to the Railway backend URL.
3. Vercel will use `frontend/vercel.json`.

## Evaluation

Create a JSONL dataset:

```json
{"question":"What is the renewal term?","answer":"The contract renews annually.","contexts":["..."],"ground_truth":"The contract renews annually."}
```

Run:

```powershell
cd evaluation
pip install -r requirements.txt
python evaluate.py --dataset sample_eval.jsonl --backend-url http://localhost:8000 --out results.json
```
