# Router para endpoints de cuentos
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from models.database_sqlite import Story, Critique, get_db
from models.schemas import (
    StoryCreate,
    StoryResponse,
    StoryResponseWithPrompt,
    StoryPromptInput,
    StoryPromptResponse,
    StoryGenerateInput,
)
from services.prompt_service import prompt_service
from services.gemini_service import gemini_service

router = APIRouter(prefix="/stories", tags=["Stories"])


# Función auxiliar para crítica automática en background
async def auto_critique_story(story_id: str, story_content: str):
    """
    Genera automáticamente una crítica del cuento usando Gemini.
    Se ejecuta en background para no bloquear la respuesta al usuario.
    """
    try:
        print(f"[auto_critique_story] 🎯 Iniciando crítica automática para cuento {story_id}")
        
        # Generar crítica con Gemini
        critique_data = await gemini_service.generate_critique(story_content)
        
        if not critique_data:
            print(f"[auto_critique_story] ⚠️ No se pudo generar crítica para {story_id}")
            return
        
        # Extraer datos de la crítica
        evaluation = critique_data.get("evaluation", {})
        feedback = critique_data.get("feedback", {})
        
        overall_score = evaluation.get("overall_score", 5)
        actionable_lesson = feedback.get("actionable_lesson", "Sin lección específica")
        
        # Guardar en base de datos
        from models.database_sqlite import SessionLocal
        db_session = SessionLocal()
        
        try:
            db_critique = Critique(
                id=str(uuid.uuid4()),
                story_id=story_id,
                critique_text=str(critique_data),  # JSON completo como texto
                score=overall_score,
            )
            db_session.add(db_critique)
            db_session.commit()
            
            print(f"[auto_critique_story] ✅ Crítica guardada para {story_id} - Score: {overall_score}/10")
            
            # 🔄 BUCLE DE APRENDIZAJE: Cada N críticas, disparar síntesis automática
            critique_count = db_session.query(Critique).count()
            SYNTHESIS_THRESHOLD = 2  # Síntesis cada 2 críticas
            
            if critique_count % SYNTHESIS_THRESHOLD == 0:
                print(f"[auto_critique_story] 🧠 Umbral alcanzado ({critique_count} críticas) - Disparando síntesis de lecciones...")
                
                # Importar servicios necesarios
                from services.learning_service import learning_service
                
                # Obtener las últimas N críticas
                recent_critiques = db_session.query(Critique).order_by(
                    Critique.timestamp.desc()
                ).limit(SYNTHESIS_THRESHOLD).all()
                
                # Preparar datos para síntesis
                critiques_data = []
                critique_ids = []
                for c in recent_critiques:
                    critiques_data.append({
                        'id': c.id,
                        'story_id': c.story_id,
                        'critique_text': c.critique_text,
                        'score': c.score
                    })
                    critique_ids.append(c.id)
                
                # Generar síntesis
                synthesis_result = await gemini_service.synthesize_lessons(critiques_data)
                
                if synthesis_result:
                    # Guardar lecciones y actualizar perfil
                    learning_service.add_lessons_to_history(synthesis_result, critique_ids)
                    learning_service.update_style_profile(synthesis_result)
                    
                    lessons_count = len(synthesis_result.get('lessons_learned', []))
                    print(f"[auto_critique_story] ✅ Síntesis completada: {lessons_count} lecciones aprendidas")
                else:
                    print(f"[auto_critique_story] ⚠️ Síntesis falló - continuando...")
            
        finally:
            db_session.close()
            
    except Exception as e:
        import traceback
        print(f"[auto_critique_story] ❌ Error generando crítica: {e}")
        print(traceback.format_exc())


@router.post(
    "/generate",
    response_model=StoryResponseWithPrompt,
    status_code=status.HTTP_201_CREATED,
    summary="Generar un cuento automáticamente",
)
async def generate_story(
    story_inputs: StoryGenerateInput, 
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(get_db)
):
    """
    Genera un cuento completo usando Gemini basado en los inputs del usuario.
    Además, dispara automáticamente una crítica en background para mejorar el sistema.
    """
    print(f"[generateStory] 🎯 Iniciando generación de cuento...")
    print(f"[generateStory] Datos del cuento:")
    print(f"  - theme: {story_inputs.theme}")
    print(f"  - character_names: {story_inputs.character_names}")
    print(f"  - moral_lesson: {story_inputs.moral_lesson}")
    print(f"  - target_age: {story_inputs.target_age}")
    print(f"  - length: {story_inputs.length}")
    
    if not gemini_service.is_configured():
        print(f"[generateStory] ❌ Gemini no configurado")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio Gemini no configurado. Verifica GEMINI_API_KEY."
        )
    
    try:
        # 1. Construir descripción del contexto
        print(f"[generateStory] 📝 Construyendo contexto...")
        context_parts = [f"Tema: {story_inputs.theme}"]
        
        # Agregar personajes si fueron seleccionados
        if story_inputs.character_names and len(story_inputs.character_names) > 0:
            characters_str = ", ".join(story_inputs.character_names)
            context_parts.append(f"Personajes: {characters_str}")
        
        # Agregar lección moral si existe
        if story_inputs.moral_lesson:
            context_parts.append(f"Lección moral: {story_inputs.moral_lesson}")
        
        # Agregar elementos especiales si existen
        if story_inputs.special_elements:
            context_parts.append(f"Elementos especiales: {story_inputs.special_elements}")
        
        context = " | ".join(context_parts)
        print(f"[generateStory] Contexto construido: {context}")
        
        # 2. Convertir formato moderno a formato de prompt legacy
        # Si no hay personajes, usar tema como base
        main_character = story_inputs.character_names[0] if story_inputs.character_names else "un personaje"
        print(f"[generateStory] Personaje principal: {main_character}")
        
        prompt_inputs = StoryPromptInput(
            personaje=main_character,
            contexto_opcional=context,
            emocion_objetivo=story_inputs.moral_lesson,
            personajes_secundarios=story_inputs.character_names[1:] if story_inputs.character_names and len(story_inputs.character_names) > 1 else None
        )
        
        # 2.5. Buscar cuentos similares con RAG
        print(f"[generateStory] 🔍 Buscando cuentos similares con RAG...")
        from services.rag_service import rag_service
        
        similar_stories = await rag_service.search_similar_stories(
            db=db_session,
            theme=story_inputs.theme,
            target_age=story_inputs.target_age,
            top_k=2,  # Máximo 2 ejemplos
            min_similarity=0.5,  # Similitud mínima 50%
            min_score=7.5  # Score mínimo 7.5/10
        )
        
        if similar_stories:
            print(f"[generateStory] ✅ RAG encontró {len(similar_stories)} ejemplos similares")
        else:
            print(f"[generateStory] ℹ️ RAG no encontró ejemplos suficientemente similares")
        
        print(f"[generateStory] 🔧 Generando prompt con prompt_service...")
        prompt = await prompt_service.build_story_prompt(
            prompt_inputs, 
            apply_lessons=True,
            similar_stories=similar_stories
        )
        print(f"[generateStory] ✅ Prompt generado ({len(prompt)} caracteres)")
        
        # Trackear lecciones aplicadas
        from services.learning_service import learning_service
        active_lessons = learning_service.get_active_lessons()
        applied_lesson_ids = [lesson['lesson_id'] for lesson in active_lessons]
        
        if applied_lesson_ids:
            print(f"[generateStory] 🎓 Aplicando {len(applied_lesson_ids)} lecciones al cuento")
        
        # 3. Generar cuento con Gemini
        print(f"[generateStory] 🤖 Enviando request a Gemini...")
        gemini_response = await gemini_service.generate_story(prompt)
        
        if not gemini_response:
            print(f"[generateStory] ❌ Gemini no retornó contenido o título válido")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generando el cuento con Gemini: No se pudo obtener título o contenido."
            )
        
        title = gemini_response.get("title", f"Cuento sobre {story_inputs.theme}")
        story_content = gemini_response.get("content")
        
        # Limpiar título de markdown o caracteres especiales (puede que Gemini aún los ponga)
        title = title.replace('#', '').replace('*', '').strip()
        if len(title) > 100:
            title = title[:97] + "..."
        
        print(f"[generateStory] ✅ Cuento generado ({len(story_content)} caracteres)")
        print(f"[generateStory] 📌 Título: {title}")
        
        # 5. Generar embedding
        print(f"[generateStory] 📊 Generando embedding...")
        embedding_vector = await gemini_service.generate_embedding(story_content)
        print(f"[generateStory] ✅ Embedding generado")
        
        # 6. Generar plantilla de ilustraciones
        print(f"[generateStory] 🎨 Generando plantilla de ilustraciones...")
        illustration_template = await gemini_service.generate_illustration_template(story_content, title)
        print(f"[generateStory] ✅ Plantilla de ilustraciones generada")
        
        # 7. Guardar en base de datos (SQLite usa embedding_json en lugar de embedding)
        print(f"[generateStory] 💾 Guardando en base de datos...")
        db_story = Story(
            title=title,
            content=story_content,
            is_seed=False,
            embedding_json=embedding_vector,  # SQLite usa JSON para el vector
            illustration_template=illustration_template,  # JSON con plantilla de ilustraciones
        )
        db_session.add(db_story)
        db_session.commit()
        db_session.refresh(db_story)
        
        print(f"[generateStory] ✅ Cuento guardado con ID: {db_story.id}")
        
        # Incrementar contador de aplicación de lecciones
        if applied_lesson_ids:
            learning_service.increment_lesson_application(applied_lesson_ids)
            print(f"[generateStory] 📊 Contador de aplicación actualizado para {len(applied_lesson_ids)} lecciones")
        
        # 8. Disparar crítica automática en background
        background_tasks.add_task(auto_critique_story, db_story.id, story_content)
        print(f"[generateStory] 📝 Crítica automática programada para cuento {db_story.id}")
        
        return StoryResponseWithPrompt(
            id=db_story.id,
            title=db_story.title,
            content=db_story.content,
            version=db_story.version,
            is_seed=db_story.is_seed,
            created_at=db_story.created_at,
            prompt_used=prompt,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[generateStory] ❌ Error completo: Error en la generación automática: {str(e)}")
        import traceback
        print(f"[generateStory] ❌ Stack trace:")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la generación automática: {str(e)}"
        )


@router.post(
    "/prompt",
    response_model=StoryPromptResponse,
    status_code=status.HTTP_200_OK,
    summary="Generar un prompt de cuento",
)
def generate_story_prompt(prompt_inputs: StoryPromptInput):
    """Genera un prompt basado en la guía de estilo, el input del usuario y datos del personaje."""
    try:
        prompt = prompt_service.build_story_prompt(prompt_inputs)
        return StoryPromptResponse(prompt=prompt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando el prompt: {str(e)}",
        )


@router.post(
    "",
    response_model=StoryResponseWithPrompt,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo cuento",
)
def create_story(story: StoryCreate, db_session: Session = Depends(get_db)):
    """
    Crea un nuevo cuento en la base de datos.

    - **title**: Título del cuento.
    - **content**: Contenido completo del cuento.
    - **is_seed**: Marcar como `True` si es uno de los 60 cuentos originales.
    - **prompt_inputs**: Opcional. Datos del usuario para generar un prompt.
    """
    prompt_used = None
    if story.prompt_inputs:
        try:
            prompt_used = prompt_service.build_story_prompt(story.prompt_inputs)
        except Exception:
            # Si falla la generación del prompt, continuamos sin él
            pass

    # TODO: Lógica para generar el embedding aquí (Function A y B de tu plan)
    db_story = Story(
        title=story.title,
        content=story.content,
        is_seed=story.is_seed,
        embedding_json=None,  # SQLite usa JSON para el vector
    )
    db_session.add(db_story)
    db_session.commit()
    db_session.refresh(db_story)

    # TODO: Disparar la tarea asíncrona de autocrítica (Function C)
    # self_critique_task.delay(db_story.id)

    return StoryResponseWithPrompt(
        id=db_story.id,
        title=db_story.title,
        content=db_story.content,
        version=db_story.version,
        is_seed=db_story.is_seed,
        created_at=db_story.created_at,
        prompt_used=prompt_used,
    )


@router.get(
    "",
    response_model=List[StoryResponse],
    summary="Obtener una lista de cuentos",
)
def get_stories(
    is_seed: Optional[bool] = None,
    limit: int = 100,
    db_session: Session = Depends(get_db),
):
    """Obtiene una lista de todos los cuentos, con opción de filtrar por 'seed'."""
    query = db_session.query(Story)
    if is_seed is not None:
        query = query.filter(Story.is_seed == is_seed)
    stories = query.limit(limit).all()
    return stories


@router.get(
    "/{story_id}",
    response_model=StoryResponse,
    summary="Obtener un cuento por su ID",
)
def get_story(story_id: uuid.UUID, db_session: Session = Depends(get_db)):
    """Obtiene los detalles de un cuento específico por su ID."""
    story = db_session.query(Story).filter(Story.id == str(story_id)).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story not found"
        )
    return story


@router.get(
    "/{story_id}/critiques",
    summary="Obtener críticas de un cuento",
)
def get_story_critiques(story_id: str, db_session: Session = Depends(get_db)):
    """
    Obtiene todas las críticas generadas automáticamente para un cuento específico.
    Útil para ver cómo el sistema evaluó el cuento y qué lecciones aprendió.
    """
    # Verificar que el cuento existe
    story = db_session.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with id {story_id} not found",
        )
    
    # Obtener todas las críticas del cuento
    critiques = db_session.query(Critique).filter(
        Critique.story_id == story_id
    ).order_by(Critique.timestamp.desc()).all()
    
    return {
        "story_id": story_id,
        "story_title": story.title,
        "critique_count": len(critiques),
        "critiques": [
            {
                "id": c.id,
                "score": c.score,
                "critique_text": c.critique_text,
                "timestamp": c.timestamp,
            }
            for c in critiques
        ]
    }