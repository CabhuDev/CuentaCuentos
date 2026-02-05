# Router para testing y debugging de RAG
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from models.database_sqlite import get_db
from services.rag_service import rag_service
from pydantic import BaseModel


router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGSearchResponse(BaseModel):
    """Respuesta de búsqueda RAG"""
    query_theme: str
    total_found: int
    examples: List[dict]
    cache_hit: bool


@router.get("/search", response_model=RAGSearchResponse)
async def search_similar_stories(
    theme: str = Query(..., description="Tema para buscar cuentos similares"),
    target_age: Optional[int] = Query(None, ge=2, le=10, description="Edad objetivo (opcional)"),
    top_k: int = Query(2, ge=1, le=5, description="Número de ejemplos a retornar"),
    min_similarity: float = Query(0.5, ge=0.0, le=1.0, description="Similitud mínima (0-1)"),
    min_score: float = Query(7.0, ge=0.0, le=10.0, description="Score mínimo de crítica"),
    db: Session = Depends(get_db)
):
    """
    Busca cuentos similares a un tema usando RAG.
    Útil para testing y debugging del sistema RAG.
    
    Ejemplo:
    ```
    GET /rag/search?theme=hermanos&target_age=4&top_k=2
    ```
    """
    # Verificar si está en cache
    theme_key = theme.lower().strip()
    cache_hit = theme_key in rag_service._embedding_cache
    
    # Buscar cuentos similares
    similar_stories = await rag_service.search_similar_stories(
        db=db,
        theme=theme,
        target_age=target_age,
        top_k=top_k,
        min_similarity=min_similarity,
        min_score=min_score
    )
    
    return RAGSearchResponse(
        query_theme=theme,
        total_found=len(similar_stories),
        examples=similar_stories,
        cache_hit=cache_hit
    )


@router.get("/cache/status")
async def get_cache_status():
    """
    Muestra el estado actual del cache de embeddings.
    """
    cache = rag_service._embedding_cache
    
    return {
        "cache_size": len(cache),
        "cached_themes": list(cache.keys()),
        "total_embeddings": sum(1 for _ in cache.values())
    }


@router.delete("/cache/clear")
async def clear_cache():
    """
    Limpia el cache de embeddings (útil para testing).
    """
    cache_size = len(rag_service._embedding_cache)
    rag_service._embedding_cache.clear()
    
    return {
        "message": "Cache limpiado",
        "embeddings_removed": cache_size
    }


@router.get("/stats")
async def get_rag_stats(db: Session = Depends(get_db)):
    """
    Estadísticas del sistema RAG.
    """
    from models.database_sqlite import Story
    
    # Contar cuentos con embeddings
    total_stories = db.query(Story).count()
    stories_with_embeddings = db.query(Story).filter(
        Story.embedding_json.isnot(None)
    ).count()
    
    return {
        "total_stories": total_stories,
        "stories_with_embeddings": stories_with_embeddings,
        "coverage_percentage": round((stories_with_embeddings / total_stories * 100) if total_stories > 0 else 0, 1),
        "cache_size": len(rag_service._embedding_cache),
        "ready_for_rag": stories_with_embeddings >= 2
    }
