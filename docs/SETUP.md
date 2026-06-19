# Setup

## Open in VS Code

Open this folder:

```text
C:\Users\HP\Documents\New project\enterprise-rag
```

You do not need to create files manually. They are already generated in this folder.

## Environment

Copy:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env.local
```

Edit `backend\.env` and set:

- `GEMINI_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY` for Qdrant Cloud

If you do not have Docker, use Qdrant Cloud and set:

```text
QDRANT_URL=https://your-cluster-url.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key
```

For local Qdrant with Docker Desktop installed, keep `QDRANT_URL=http://localhost:6333`.

## Run

### No-Docker Local Run

Use this path when Qdrant Cloud is configured in `backend\.env`.

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

### Docker Local Qdrant Run

Use this path only if Docker Desktop is installed.

```powershell
docker compose up -d qdrant
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```
