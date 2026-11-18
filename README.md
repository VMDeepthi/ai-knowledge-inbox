# AI Knowledge Inbox

A minimal full-stack RAG application: save notes or URLs, search their meaning, and ask questions with cited source snippets.

## Stack
- Frontend: React + Vite
- Backend: Python + FastAPI
- Persistence: SQLite
- Embeddings + answers: Google Gemini API
- Vector search: lightweight cosine similarity over vectors stored in SQLite (keeps setup simple)

## Requirements
- Python 3.10+
- Node.js 18+
- Google Gemini API key

## Run the backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env and add GEMINI_API_KEY
uvicorn app.main:app --reload
```
Backend: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

## Run the frontend
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:5173

## API
- `POST /ingest` — ingest `{ "type": "text", "content": "..." }` or `{ "type": "url", "content": "https://..." }`
- `GET /items` — list saved items
- `POST /query` — ask `{ "question": "...", "top_k": 4 }`
- `GET /health` — health check

## RAG design
1. URL content is fetched server-side and parsed with BeautifulSoup.
2. Text is split into overlapping character chunks (about 1,000 characters, 150 overlap).
3. Google Gemini embedding model generates vector embeddings for the text chunks.
4. Item metadata, raw text, chunks and vectors are stored in SQLite.
5. Query embedding is compared with stored vectors using cosine similarity.
6. The top matching chunks are sent to the Google Gemini generative model as context.
7. The model is instructed to answer using the retrieved context and cite source IDs. The API returns relevant snippets and source metadata separately.

## Tradeoffs and production improvements
- SQLite + in-process cosine search is intentionally small and suitable for a single-user demo. At larger scale, move to pgvector, Qdrant, Pinecone or another vector store.
- Current ingestion is synchronous. For production, put URL extraction and embedding generation on a durable queue (Celery/RQ/Arq), expose ingestion status, retries and dead-letter handling.
- Add authentication, per-user isolation, rate limiting, request size limits, SSRF protection for URL fetching, malware/content scanning, secrets management and retention controls.
- Add structured logs, metrics, tracing, database migrations, pagination, deduplication and automated tests.
- URL fetching should be hardened in production: validate DNS/IP destinations and redirects to prevent SSRF. This demo blocks obvious private/local hostnames and IPs but is not a complete SSRF defense.

## Notes
The application requires a Gemini API key for ingestion and question answering..
