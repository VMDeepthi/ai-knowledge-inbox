import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Chunk
from ..schemas import QueryRequest, QueryResponse, SourceResponse
from ..services.ai import embed_texts, generate_answer
from ..services.retrieval import retrieve


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest, db: Session = Depends(get_db)):
    chunks = db.query(Chunk).options(joinedload(Chunk.item)).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="Your inbox is empty. Add a note or URL first.")
    try:
        query_vector = embed_texts([payload.question])[0]
        matches = retrieve(query_vector, chunks, payload.top_k)
        if not matches:
            raise HTTPException(status_code=404, detail="No relevant content was found.")
        contexts = [{"item_id": chunk.item_id, "chunk_id": chunk.id, "content": chunk.content}
                    for _, chunk in matches]
        answer = generate_answer(payload.question, contexts)
        sources = [SourceResponse(
            chunk_id=chunk.id, item_id=chunk.item_id, title=chunk.item.title,
            source_type=chunk.item.source_type, source_url=chunk.item.source_url,
            snippet=chunk.content[:350], score=round(score, 4)
        ) for score, chunk in matches]
        logger.info("query_completed sources=%s", len(sources))
        return QueryResponse(answer=answer, sources=sources)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("query_failed")
        raise HTTPException(status_code=502, detail=f"Question answering failed: {str(exc)}")
