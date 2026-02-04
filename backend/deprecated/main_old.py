import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import database as db
from pydantic import BaseModel, Field

STYLE_GUIDE_PATH = Path(__file__).with_name("style_guide.json")
CHARACTERS_PATH = Path(__file__).with_name("characters.json")


# --- Pydantic Models (API Data Contract) ---
# Definen la forma de los datos para las peticiones y respuestas de la API.


class StoryPromptInput(BaseModel):
    personaje: str
    personaje_id: Optional[str] = None
    rol_personaje: Optional[str] = None
    contexto_opcional: Optional[str] = None
    emocion_objetivo: Optional[str] = None
    lugar: Optional[str] = None
    objeto_significativo: Optional[str] = None
    personajes_secundarios: Optional[List[str]] = None


class StoryBase(BaseModel):
    title: str
    content: str


class StoryCreate(StoryBase):
    is_seed: bool = False
    prompt_inputs: Optional[StoryPromptInput] = None


class StoryResponse(StoryBase):
    id: uuid.UUID
    version: int
    is_seed: bool
    created_at: datetime

    class Config:
        orm_mode = True


class StoryResponseWithPrompt(StoryResponse):
    prompt_used: Optional[str] = None


class StoryPromptResponse(BaseModel):
    prompt: str


class CritiqueBase(BaseModel):
    score_coherence: int = Field(..., gt=0, le=10)
    score_style: int = Field(..., gt=0, le=10)
    strengths: List[str]
    weaknesses: List[str]
    improvement_advice: str


class CritiqueCreate(CritiqueBase):
    story_id: uuid.UUID


class CritiqueResponse(CritiqueBase):
    id: uuid.UUID
    story_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True


class CharacterDetail(BaseModel):
    id: str
    nombre: str
    estado: str
    rasgos_distintivos: Dict[str, Any]
    armario_coherente: Dict[str, Any]
    personalidad_narrativa: Dict[str, Any]
    reglas_ilustracion: Dict[str, Any]
    accesorios_frecuentes: Optional[List[Dict[str, Any]]] = None
    historico_apariciones: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class CharacterResponse(BaseModel):
    id: str
    nombre: str
    estado: str
    edad_aparente: Optional[str] = None
    prompt_base_ia: Optional[str] = None
    total_apariciones: Optional[int] = None


def load_style_guide() -> dict:
    if not STYLE_GUIDE_PATH.exists():
        return {}
    with STYLE_GUIDE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_characters() -> List[Dict[str, Any]]:
    if not CHARACTERS_PATH.exists():
        return []
    with CHARACTERS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_character_by_id(character_id: str, characters: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for char in characters:
        if char.get("id") == character_id:
            return char
    return None


def get_character_by_name(name: str, characters: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for char in characters:
        if char.get("nombre", "").lower() == name.lower():
            return char
    return None


def _format_list(items: List[str]) -> str:
    if not items:
        return "- (sin especificar)"
    return "\n".join(f"- {item}" for item in items)


def build_prompt(style_guide: dict, prompt_inputs: StoryPromptInput, characters: List[Dict[str, Any]] = None) -> str:
    if characters is None:
        characters = []
    
    guia = style_guide.get("guia_estilo_cuento", {})
    estructura = guia.get("estructura_narrativa", {})
    requisitos = guia.get("requisitos_minimos", {})
    recomendaciones = guia.get("recomendaciones", {})
    flex = guia.get("flexibilidad", {})

    # Resolver personaje si se proporciona ID
    character_detail = None
    if prompt_inputs.personaje_id:
        character_detail = get_character_by_id(prompt_inputs.personaje_id, characters)
    elif prompt_inputs.personaje:
        character_detail = get_character_by_name(prompt_inputs.personaje, characters)

    user_lines = [f"Personaje principal: {prompt_inputs.personaje}"]
    if character_detail:
        rasgos = character_detail.get("rasgos_distintivos", {})
        personalidad = character_detail.get("personalidad_narrativa", {})
        user_lines.append(f"  Descripción visual: {rasgos.get('cabello', '')}, {rasgos.get('ojos', '')}, {rasgos.get('edad_aparente', '')}")
        if personalidad.get("arquetipos"):
            user_lines.append(f"  Arquetipos: {', '.join(personalidad.get('arquetipos', []))}")
        if personalidad.get("motivaciones"):
            user_lines.append(f"  Motivaciones: {', '.join(personalidad.get('motivaciones', []))}")
    
    if prompt_inputs.rol_personaje:
        user_lines.append(f"Rol: {prompt_inputs.rol_personaje}")
    
    if prompt_inputs.personajes_secundarios:
        user_lines.append(f"Personajes secundarios: {', '.join(prompt_inputs.personajes_secundarios)}")
    
    if prompt_inputs.contexto_opcional:
        user_lines.append(f"Contexto opcional: {prompt_inputs.contexto_opcional}")
    if prompt_inputs.emocion_objetivo:
        user_lines.append(f"Emoción objetivo: {prompt_inputs.emocion_objetivo}")
    if prompt_inputs.lugar:
        user_lines.append(f"Lugar: {prompt_inputs.lugar}")
    if prompt_inputs.objeto_significativo:
        user_lines.append(f"Objeto significativo: {prompt_inputs.objeto_significativo}")

    prompt_parts = [
        "Escribe un cuento infantil siguiendo esta guía:",
        f"Colección: {guia.get('coleccion', 'Sin especificar')}",
        f"Audiencia objetivo: {guia.get('audiencia_objetivo', 'Sin especificar')}",
        "Tono:",
        _format_list(guia.get("tono", [])),
        "Valores clave:",
        _format_list(guia.get("valores_clave", [])),
        "Estructura narrativa:",
        f"- Título: {estructura.get('titulo', 'Sin especificar')}",
        f"- Inicio: {estructura.get('inicio', 'Sin especificar')}",
        f"- Desarrollo: {estructura.get('desarrollo', 'Sin especificar')}",
        f"- Clímax: {estructura.get('climax', 'Sin especificar')}",
        f"- Resolución: {estructura.get('resolucion', 'Sin especificar')}",
        f"- Cierre opcional: {estructura.get('cierre_opcional', 'Sin especificar')}",
        "Requisitos mínimos:",
        f"- Onomatopeya: {requisitos.get('onomatopeya', 'Sin especificar')}",
        f"- Ausencia de villanos: {requisitos.get('ausencia_de_villanos', 'Sin especificar')}",
        f"- Lenguaje claro: {requisitos.get('lenguaje_claro', 'Sin especificar')}",
        "Recomendaciones:",
        f"- Longitud: {recomendaciones.get('longitud_texto', 'Sin especificar')}",
        f"- Párrafos: {recomendaciones.get('parrafos', 'Sin especificar')}",
        f"- Lenguaje sensorial: {recomendaciones.get('lenguaje_sensorial', 'Sin especificar')}",
        f"- Diálogos: {recomendaciones.get('dialogos', 'Sin especificar')}",
        f"- Ritmo: {recomendaciones.get('ritmo', 'Sin especificar')}",
        "Flexibilidad sugerida:",
        f"- Variación temática: {', '.join(flex.get('variacion_tematica', [])) or 'Sin especificar'}",
        f"- Variación de escenarios: {', '.join(flex.get('variacion_escenarios', [])) or 'Sin especificar'}",
        f"- Elementos opcionales: {', '.join(flex.get('elementos_opcionales', [])) or 'Sin especificar'}",
        "Inputs del usuario:",
        _format_list(user_lines),
        "IMPORTANTE: Mantén la coherencia visual y narrativa del personaje a lo largo del cuento.",
        "Entrega un texto único, cálido y coherente, evitando clichés explícitos.",
    ]

    return "\n".join(prompt_parts)


# --- FastAPI Application ---
app = FastAPI(
    title="CuentaCuentos AI Engine",
    description="API para la generación y mejora evolutiva de cuentos infantiles.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    # Una forma de asegurarse de que las tablas estén creadas al iniciar.
    # En un entorno de producción, se usarían migraciones (ej. Alembic).
    # db.create_tables() # Comentado para evitar ejecuciones accidentales
    app.state.style_guide = load_style_guide()
    app.state.characters = load_characters()


# --- API Endpoints ---


@app.post(
    "/stories/prompt",
    response_model=StoryPromptResponse,
    status_code=status.HTTP_200_OK,
    tags=["Stories"],
    summary="Generar un prompt de cuento",
)
def generate_story_prompt(prompt_inputs: StoryPromptInput):
    """
    Genera un prompt basado en la guía de estilo, el input del usuario y datos del personaje.
    """
    style_guide = getattr(app.state, "style_guide", {})
    characters = getattr(app.state, "characters", [])
    
    if not style_guide:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La guía de estilo no está disponible.",
        )

    prompt = build_prompt(style_guide, prompt_inputs, characters)
    return StoryPromptResponse(prompt=prompt)


@app.get(
    "/characters",
    response_model=List[CharacterResponse],
    tags=["Characters"],
    summary="Listar todos los personajes",
)
def list_characters():
    """
    Obtiene la lista de todos los personajes registrados.
    """
    characters = getattr(app.state, "characters", [])
    return [
        CharacterResponse(
            id=char.get("id", ""),
            nombre=char.get("nombre", ""),
            estado=char.get("estado", "activo"),
            edad_aparente=char.get("rasgos_distintivos", {}).get("edad_aparente"),
            prompt_base_ia=char.get("reglas_ilustracion", {}).get("prompt_base_ia"),
            total_apariciones=char.get("metadata", {}).get("total_apariciones", 0),
        )
        for char in characters
    ]


@app.get(
    "/characters/{character_id}",
    response_model=CharacterDetail,
    tags=["Characters"],
    summary="Obtener detalles de un personaje",
)
def get_character(character_id: str):
    """
    Obtiene los detalles completos de un personaje específico.
    """
    characters = getattr(app.state, "characters", [])
    character = get_character_by_id(character_id, characters)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personaje con id '{character_id}' no encontrado.",
        )
    
    return CharacterDetail(**character)


@app.post(
    "/stories",
    response_model=StoryResponseWithPrompt,
    status_code=status.HTTP_201_CREATED,
    tags=["Stories"],
    summary="Crear un nuevo cuento",
)
def create_story(story: StoryCreate, db_session: Session = Depends(db.get_db)):
    """
    Crea un nuevo cuento en la base de datos.

    - **title**: Título del cuento.
    - **content**: Contenido completo del cuento.
    - **is_seed**: Marcar como `True` si es uno de los 60 cuentos originales.
    - **prompt_inputs**: Opcional. Datos del usuario para generar un prompt.
    """
    prompt_used = None
    if story.prompt_inputs:
        style_guide = getattr(app.state, "style_guide", {})
        characters = getattr(app.state, "characters", [])
        if style_guide:
            prompt_used = build_prompt(style_guide, story.prompt_inputs, characters)

    # Lógica para generar el embedding aquí (Function A y B de tu plan)
    # Por ahora, lo dejamos como None.
    db_story = db.Story(
        title=story.title,
        content=story.content,
        is_seed=story.is_seed,
        embedding=None,
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


@app.get(
    "/stories",
    response_model=List[StoryResponse],
    tags=["Stories"],
    summary="Obtener una lista de cuentos",
)
def get_stories(
    is_seed: Optional[bool] = None,
    limit: int = 100,
    db_session: Session = Depends(db.get_db),
):
    """
    Obtiene una lista de todos los cuentos, con opción de filtrar por 'seed'.
    """
    query = db_session.query(db.Story)
    if is_seed is not None:
        query = query.filter(db.Story.is_seed == is_seed)
    stories = query.limit(limit).all()
    return stories


@app.get(
    "/stories/{story_id}",
    response_model=StoryResponse,
    tags=["Stories"],
    summary="Obtener un cuento por su ID",
)
def get_story(story_id: uuid.UUID, db_session: Session = Depends(db.get_db)):
    """
    Obtiene los detalles de un cuento específico por su ID.
    """
    story = db_session.query(db.Story).filter(db.Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story not found"
        )
    return story


@app.post(
    "/critiques",
    response_model=CritiqueResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Critiques"],
    summary="Añadir una crítica a un cuento",
)
def add_critique_to_story(
    critique: CritiqueCreate, db_session: Session = Depends(db.get_db)
):
    """
    Añade una crítica a un cuento existente. Esto es el resultado de la
    `Function C: SelfCritique`.
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
