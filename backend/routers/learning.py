# Router para sistema de aprendizaje evolutivo
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from models import database_sqlite as db
from services.gemini_service import gemini_service
from services.learning_service import learning_service

router = APIRouter(prefix="/learning", tags=["Learning"])


@router.post(
    "/synthesize",
    response_model=Dict[str, Any],
    summary="Sintetizar lecciones de las últimas N críticas"
)
async def synthesize_lessons(
    last_n_critiques: int = 5,
    db_session: Session = Depends(db.get_db)
):
    """
    Ejecuta síntesis de lecciones aprendidas desde las últimas N críticas.
    
    - **last_n_critiques**: Número de críticas recientes a analizar (default: 5)
    
    Proceso:
    1. Obtiene las últimas N críticas de la BD
    2. Usa Gemini para sintetizar patrones y lecciones
    3. Actualiza learning_history.json con nuevas lecciones
    4. Actualiza style_profile.json con ajustes de estilo
    5. Retorna resumen de la síntesis
    """
    try:
        # Verificar que Gemini esté configurado
        if not gemini_service.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio Gemini no configurado. Verifica GEMINI_API_KEY."
            )
        
        # 1. Obtener últimas N críticas
        critiques = db_session.query(db.Critique).order_by(
            db.Critique.timestamp.desc()
        ).limit(last_n_critiques).all()
        
        if not critiques:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay críticas disponibles para sintetizar"
            )
        
        if len(critiques) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Se necesitan al menos 3 críticas para síntesis significativa. Solo hay {len(critiques)}."
            )
        
        # 2. Preparar datos para Gemini
        critiques_data = []
        critique_ids = []
        
        for critique in critiques:
            critiques_data.append({
                'id': critique.id,
                'story_id': critique.story_id,
                'critique_text': critique.critique_text,
                'score': critique.score
            })
            critique_ids.append(critique.id)
        
        print(f"[synthesize_lessons] 🧠 Analizando {len(critiques_data)} críticas...")
        
        # 3. Generar síntesis con Gemini
        synthesis_result = await gemini_service.synthesize_lessons(critiques_data)
        
        if not synthesis_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generando síntesis con Gemini"
            )
        
        # 4. Guardar lecciones en learning_history.json
        history_saved = learning_service.add_lessons_to_history(
            synthesis_result,
            critique_ids
        )
        
        # 5. Actualizar style_profile.json
        profile_updated = learning_service.update_style_profile(synthesis_result)
        
        # 6. Preparar respuesta
        lessons_learned = synthesis_result.get('lessons_learned', [])
        
        return {
            "status": "success",
            "critiques_analyzed": len(critiques_data),
            "lessons_extracted": len(lessons_learned),
            "synthesis_summary": synthesis_result.get('synthesis_summary', ''),
            "lessons": lessons_learned,
            "style_adjustments": synthesis_result.get('style_adjustments', {}),
            "meta_insights": synthesis_result.get('meta_insights', {}),
            "history_updated": history_saved,
            "profile_updated": profile_updated,
            "message": f"✅ Síntesis completada: {len(lessons_learned)} lecciones aprendidas"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en síntesis: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=Dict[str, Any],
    summary="Obtener estadísticas del sistema de aprendizaje"
)
async def get_learning_statistics(db_session: Session = Depends(db.get_db)):
    """
    Retorna estadísticas sobre el estado del sistema de aprendizaje evolutivo.
    
    Incluye:
    - Total de lecciones aprendidas
    - Lecciones activas por categoría
    - Fecha de última síntesis
    - Áreas de enfoque actuales
    - Contadores de críticas y cuentos
    """
    try:
        # Estadísticas del servicio de aprendizaje
        stats = learning_service.get_synthesis_statistics()
        
        # Contadores de base de datos
        total_stories = db_session.query(db.Story).count()
        total_critiques = db_session.query(db.Critique).count()
        
        # Calcular críticas hasta próxima síntesis
        SYNTHESIS_THRESHOLD = 2  # Debe coincidir con stories.py
        critiques_until_next = SYNTHESIS_THRESHOLD - (total_critiques % SYNTHESIS_THRESHOLD)
        if critiques_until_next == SYNTHESIS_THRESHOLD:
            critiques_until_next = 0
        
        # Promedio de scores recientes
        recent_critiques = db_session.query(db.Critique).order_by(
            db.Critique.timestamp.desc()
        ).limit(10).all()
        
        avg_score = None
        if recent_critiques:
            scores = [c.score for c in recent_critiques if c.score is not None]
            if scores:
                avg_score = round(sum(scores) / len(scores), 2)
        
        # Calcular total de síntesis realizadas
        # Cada síntesis procesa SYNTHESIS_THRESHOLD críticas
        total_syntheses = total_critiques // SYNTHESIS_THRESHOLD
        
        return {
            **stats,
            "total_syntheses": total_syntheses,
            "total_critiques_analyzed": total_critiques,
            "critiques_until_next_synthesis": critiques_until_next,
            "database_stats": {
                "total_stories": total_stories,
                "total_critiques": total_critiques,
                "avg_score_last_10": avg_score
            }
        }
        
    except Exception as e:
        print(f"❌ Error en /learning/statistics: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@router.get(
    "/lessons",
    response_model=Dict[str, Any],
    summary="Listar lecciones aprendidas"
)
async def list_lessons(
    category: str = None,
    status_filter: str = "active"
):
    """
    Lista lecciones aprendidas, opcionalmente filtradas.
    
    - **category**: Filtrar por categoría (opcional)
    - **status_filter**: 'active', 'archived' o 'all' (default: 'active')
    """
    try:
        history = learning_service.load_learning_history()
        
        # Filtrar por status
        filtered = history
        if status_filter and status_filter != "all":
            filtered = [l for l in history if l.get('status') == status_filter]
        
        # Filtrar por categoría
        if category:
            filtered = [l for l in filtered if l.get('category') == category]
        
        return {
            "lessons": filtered,
            "total": len(filtered),
            "total_all": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando lecciones: {str(e)}"
        )


@router.get(
    "/history",
    response_model=Dict[str, Any],
    summary="Ver historial completo de aprendizaje"
)
async def get_learning_history():
    """
    Retorna el contenido completo de learning_history.json
    """
    try:
        history = learning_service.load_learning_history()
        return {
            "history": history,
            "total_lessons": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo historial: {str(e)}"
        )


@router.get(
    "/style-profile",
    response_model=Dict[str, Any],
    summary="Ver perfil de estilo actual"
)
async def get_style_profile():
    """
    Retorna el contenido completo de style_profile.json
    """
    try:
        profile = learning_service.load_style_profile()
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo perfil: {str(e)}"
        )
