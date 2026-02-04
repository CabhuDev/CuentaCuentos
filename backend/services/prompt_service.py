# Servicio de generación de prompts
import json
from typing import List, Dict, Any
from config import STYLE_GUIDE_PATH
from models.schemas import StoryPromptInput
from services.character_service import character_service


class PromptService:
    def __init__(self):
        self._style_guide = None

    def load_style_guide(self) -> Dict[str, Any]:
        """Cargar guía de estilo desde archivo JSON"""
        if self._style_guide is None:
            if not STYLE_GUIDE_PATH.exists():
                self._style_guide = {}
            else:
                with STYLE_GUIDE_PATH.open("r", encoding="utf-8") as file:
                    self._style_guide = json.load(file)
        return self._style_guide

    def _format_list(self, items: List[str]) -> str:
        """Formatear lista para el prompt"""
        if not items:
            return "- (sin especificar)"
        return "\n".join(f"- {item}" for item in items)

    def build_story_prompt(self, prompt_inputs: StoryPromptInput) -> str:
        """Construir prompt para generación de cuentos"""
        style_guide = self.load_style_guide()
        guia = style_guide.get("guia_estilo_cuento", {})
        estructura = guia.get("estructura_narrativa", {})
        requisitos = guia.get("requisitos_minimos", {})
        recomendaciones = guia.get("recomendaciones", {})
        flex = guia.get("flexibilidad", {})

        # Resolver personaje si se proporciona ID
        character_detail = None
        if prompt_inputs.personaje_id:
            character_detail = character_service.get_character_by_id(prompt_inputs.personaje_id)
        elif prompt_inputs.personaje:
            character_detail = character_service.get_character_by_name(prompt_inputs.personaje)

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
            self._format_list(guia.get("tono", [])),
            "Valores clave:",
            self._format_list(guia.get("valores_clave", [])),
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
            self._format_list(user_lines),
            "IMPORTANTE: Mantén la coherencia visual y narrativa del personaje a lo largo del cuento.",
            "Entrega un texto único, cálido y coherente, evitando clichés explícitos.",
        ]

        return "\n".join(prompt_parts)

    def refresh_style_guide(self):
        """Forzar recarga de la guía de estilo"""
        self._style_guide = None


# Instancia singleton
prompt_service = PromptService()