import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Item, Chunk
from ..schemas import IngestRequest, IngestResponse, ItemResponse
from ..services.chunking import split_into_chunks
from ..services.ai import embed_texts
from ..services.url_fetcher import fetch_page

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ingest", response_model=IngestResponse, status_code=201)
def ingest(payload: IngestRequest, db: Session = Depends(get_db)):
    source_url = None
    title = "Text note"
    raw_content = payload.content
    try:
        if payload.type == "url":
            source_url = payload.content
            title, raw_content = fetch_page(source_url)
        chunks = split_into_chunks(raw_content)
        if not chunks:
            raise HTTPException(status_code=422, detail="No readable content found.")
        vectors = embed_texts(chunks)
        item = Item(source_type=payload.type, source_url=source_url, title=title, raw_content=raw_content)
        db.add(item)
        db.flush()
        db.add_all([Chunk(item_id=item.id, content=chunk, embedding=vector) for chunk, vector in zip(chunks, vectors)])
        db.commit()
        db.refresh(item)
        logger.info("content_ingested item_id=%s source_type=%s chunks=%s", item.id, payload.type, len(chunks))
        return IngestResponse(id=item.id, title=item.title, source_type=item.source_type,
                              chunk_count=len(chunks), message="Content saved and indexed.")
    except HTTPException:
        db.rollback()
        raise
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        db.rollback()
        logger.exception("ingestion_failed")
        raise HTTPException(status_code=502, detail=f"Ingestion failed: {str(exc)}")

@router.get("/items", response_model=list[ItemResponse])
def list_items(db: Session = Depends(get_db)):
    items = db.query(Item).order_by(Item.created_at.desc()).all()
    return [ItemResponse(
        id=item.id, title=item.title, source_type=item.source_type, source_url=item.source_url,
        created_at=item.created_at.isoformat(), preview=item.raw_content[:180]
    ) for item in items]
