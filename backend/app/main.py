import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from .routers import ingestion, query

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Knowledge Inbox", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ingestion.router, tags=["Knowledge"])
app.include_router(query.router, tags=["RAG"])

@app.get("/health")
def health():
    return {"status": "ok"}
