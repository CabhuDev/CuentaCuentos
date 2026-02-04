# Router para endpoints de críticas
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import database_sqlite as db
from models.schemas import CritiqueCreate, CritiqueResponse

router = APIRouter(prefix="/critiques", tags=["Critiques"])


@router.post(
    "",
    response_model=CritiqueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir una crítica a un cuento",
)
def add_critique_to_story(
    critique: CritiqueCreate, db_session: Session = Depends(db.get_db)
):
    """
    Añade una crítica a un cuento existente. 
    Esto es el resultado de la `Function C: SelfCritique`.
    """
    # Verificar que el cuento existe
    story = db_session.query(db.Story).filter(db.Story.id == critique.story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with id {critique.story_id} not found.",
        )

    db_critique = db.Critique(**critique.dict())
    db_session.add(db_critique)
    db_session.commit()
    db_session.refresh(db_critique)

    # TODO: Disparar la tarea de síntesis de aprendizaje si se cumple la condición
    # (ej. cada 10 críticas) (Function D)
    # synthesize_learning_task.delay()

    return db_critique