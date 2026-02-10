# Servicio de generación de prompts
import json
from typing import List, Dict, Any, Optional
from config import STYLE_GUIDE_PATH
from models.schemas import StoryPromptInput
from services.character_service import character_service


class PromptService:
    def __init__(self):
        self._style_guide = None
        self._learning_service = None

    def _get_learning_service(self):
        """Lazy load del learning service para evitar imports circulares"""
        if self._learning_service is None:
            from services.learning_service import learning_service
            self._learning_service = learning_service
        return self._learning_service

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

    def _build_lessons_section(self) -> List[str]:
        """
        Construye sección con lecciones activas del sistema de aprendizaje.
        Retorna lista de strings para incluir en el prompt.
        """
        try:
            learning_service = self._get_learning_service()
            active_lessons = learning_service.get_active_lessons()
            
            if not active_lessons:
                print("[prompt_service] No hay lecciones activas para aplicar")
                return []
            
            print(f"[prompt_service] 🎓 Aplicando {len(active_lessons)} lecciones activas al prompt")
            
            lessons_section = [
                "",
                "=== LECCIONES APRENDIDAS PARA APLICAR ===",
                "El sistema ha aprendido lo siguiente de cuentos anteriores. APLICA estas lecciones:"
            ]
            
            # Agrupar lecciones por categoría
            by_category = {}
            for lesson in active_lessons:
                category = lesson.get('category', 'general')
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(lesson)
            
            # Formatear cada categoría
            for category, lessons in by_category.items():
                lessons_section.append(f"\n📌 {category.upper().replace('_', ' ')}:")
                for lesson in lessons:
                    insight = lesson.get('insight', '')
                    guidance = lesson.get('actionable_guidance', '')
                    
                    if insight:
                        lessons_section.append(f"  • {insight}")
                    if guidance:
                        lessons_section.append(f"    → Acción: {guidance}")
            
            lessons_section.append("\n=== FIN DE LECCIONES ===")
            lessons_section.append("")
            
            return lessons_section
            
        except Exception as e:
            print(f"[prompt_service] ⚠️ Error cargando lecciones: {e}")
            return []
    
    def _build_examples_section(self, similar_stories: List[Dict[str, Any]]) -> List[str]:
        """
        Construye sección con ejemplos de cuentos similares exitosos (RAG).
        
        Args:
            similar_stories: Lista de cuentos similares del RAG service
            
        Returns:
            Lista de strings para incluir en el prompt
        """
        if not similar_stories:
            return []
        
        print(f"[prompt_service] 📚 Añadiendo {len(similar_stories)} ejemplos exitosos al prompt")
        
        examples_section = [
            "",
            "=== EJEMPLOS DE CUENTOS EXITOSOS SIMILARES ===",
            "Estos son fragmentos de tus cuentos anteriores sobre temas similares que obtuvieron buenos scores.",
            "Aprende de ellos pero NO copies. Usa las mismas técnicas con tu propio estilo:"
        ]
        
        for example in similar_stories:
            examples_section.append(f"\n📖 Ejemplo #{example['rank']} - Score: {example['score']}/10 (Similitud: {int(example['similarity']*100)}%)")
            examples_section.append(f"Título: {example['title']}")
            
            # Fragmento del cuento
            examples_section.append(f"Fragmento:")
            examples_section.append(f'"{example["fragment"]}"')
            
            # Técnicas que funcionaron
            if example.get('techniques'):
                examples_section.append(f"✅ Lo que funcionó bien:")
                for technique in example['techniques']:
                    examples_section.append(f"   - {technique}")
        
        examples_section.append("\n=== FIN DE EJEMPLOS ===")
        examples_section.append("")
        
        return examples_section

    async def build_story_prompt(
        self, 
        prompt_inputs: StoryPromptInput, 
        apply_lessons: bool = True,
        similar_stories: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Construir prompt para generación de cuentos
        
        Args:
            prompt_inputs: Datos del usuario para el cuento
            apply_lessons: Si es True, incluye lecciones activas en el prompt
            similar_stories: Lista de cuentos similares del RAG (opcional)
        """
        print(f"[prompt_service] Construyendo prompt (apply_lessons={apply_lessons}, RAG={similar_stories is not None})...")
        
        style_guide = self.load_style_guide()
        guia = style_guide.get("guia_estilo_cuento", {})
        estructura = guia.get("estructura_narrativa", {})
        requisitos = guia.get("requisitos_minimos", {})
        recomendaciones = guia.get("recomendaciones", {})
        flex = guia.get("flexibilidad", {})
        evocacion = guia.get("evocacion_emocional", {})
        refinamiento = guia.get("refinamiento_literario", {})
        nivel_edad = guia.get("nivel_complejidad", {})

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
            "",
            "⚠️ IMPORTANTE - VARIACIÓN ESTRUCTURAL:",
            "NO uses SIEMPRE la misma estructura. Este cuento debe tener una estructura diferente a los anteriores.",
            "Opciones de estructura disponibles:",
        ]
        
        # Añadir estructuras alternativas
        estructuras_alt = estructura.get("estructuras_alternativas", [])
        if estructuras_alt:
            for i, est in enumerate(estructuras_alt, 1):
                prompt_parts.append(f"{i}. {est.get('nombre', 'Sin nombre')}: {est.get('patron', '')}")
                prompt_parts.append(f"   Cierre: {est.get('cierre', '')}")
        
        prompt_parts.extend([
            "",
            "Variaciones de cierre recomendadas (NO usar pregunta al lector en TODOS los cuentos):",
        ])
        
        # Añadir opciones de cierre
        cierres = estructura.get("variaciones_de_cierre", [])
        for cierre in cierres[:5]:  # Primeras 5 opciones
            prompt_parts.append(f"  • {cierre}")
        
        prompt_parts.extend([
            "",
            "VARIACIÓN DE PÁRRAFOS:",
            "- NO hagas todos los párrafos del mismo tamaño",
            "- Alterna entre párrafos cortos (1-2 frases) y más largos (4-5 frases)",
            "- Usa párrafos muy cortos para momentos de impacto o cambio",
            "",
            "ELEMENTOS A EVITAR:",
        ])
        
        elementos_evitar = estructura.get("elementos_a_evitar", [])
        for elemento in elementos_evitar:
            prompt_parts.append(f"  ❌ {elemento}")
        
        prompt_parts.extend([
            "",
            "Requisitos mínimos:",
            f"- Onomatopeya: {requisitos.get('onomatopeya', 'Sin especificar')}",
            f"- Ausencia de villanos: {requisitos.get('ausencia_de_villanos', 'Sin especificar')}",
            f"- Lenguaje claro: {requisitos.get('lenguaje_claro', 'Sin especificar')}",
            f"- Evocación sensorial: {requisitos.get('evocacion_sensorial', 'Sin especificar')}",
            f"- Tríada rítmica: {requisitos.get('triada_ritmica', 'Sin especificar')}",
            f"- SHOW DON'T TELL: {requisitos.get('show_dont_tell', 'Sin especificar')}",
            "",
            "🎭 EVOCACIÓN EMOCIONAL - REGLA DE ORO:",
            f"❌ MAL: {evocacion.get('mal_ejemplo', 'Sin especificar')}",
            f"✅ BIEN: {evocacion.get('buen_ejemplo', 'Sin especificar')}",
            "Cuando el personaje sienta una emoción, NO la nombres. Descríbela con acciones físicas:",
        ])
        
        # Añadir ejemplos de emociones
        emociones = evocacion.get("emociones_comunes", {})
        if emociones:
            for emocion, acciones in list(emociones.items())[:4]:  # Primeras 4
                prompt_parts.append(f"  • {emocion.capitalize()}: {acciones}")
        
        prompt_parts.extend([
            "",
            "✨ REFINAMIENTO LITERARIO (el 'toque de maestro'):",
            "",
            "1. USO DE TRÍADAS (la regla del tres - ritmo mágico):",
        ])
        
        triadas = refinamiento.get("uso_de_triadas", {})
        if triadas and triadas.get("ejemplos"):
            for ejemplo in triadas.get("ejemplos", [])[:2]:
                prompt_parts.append(f"   • {ejemplo}")
        
        prompt_parts.extend([
            "",
            "2. TEXTURAS Y TEMPERATURAS (el niño debe SENTIR el cuento):",
            "   Incluir AL MENOS una referencia táctil:",
        ])
        
        texturas = refinamiento.get("texturas_y_temperaturas", {})
        if texturas and texturas.get("vocabulario"):
            for vocab in texturas.get("vocabulario", [])[:2]:
                prompt_parts.append(f"   • {vocab}")
        
        prompt_parts.extend([
            "",
            "3. DINAMISMO VISUAL (acciones que el niño pueda IMITAR):",
            "   Describir movimientos físicos que el niño pueda hacer mientras escucha:",
        ])
        
        dinamismo = refinamiento.get("dinamismo_visual", {})
        if dinamismo and dinamismo.get("verbos_dinamicos"):
            for verbo in dinamismo.get("verbos_dinamicos", [])[:4]:
                prompt_parts.append(f"   • {verbo}")
        
        prompt_parts.extend([
            "",
            "4. CADENCIA MUSICAL:",
            "   Las frases deben tener ritmo de CANCIÓN DE CUNA, incluso sin rima explícita.",
        ])
        
        cadencia = refinamiento.get("cadencia_musical", {})
        if cadencia and cadencia.get("tecnicas"):
            for tecnica in cadencia.get("tecnicas", [])[:3]:
                prompt_parts.append(f"   • {tecnica}")
        
        if cadencia.get("ejemplo_ritmo"):
            prompt_parts.append(f"   Ejemplo: {cadencia.get('ejemplo_ritmo')}")
        
        prompt_parts.extend([
            "",
            "5. SILENCIO Y ESPACIO:",
            "   MENOS ES MÁS. Deja espacio para la ilustración y la imaginación del niño.",
            "   No describir TODO. Confía en la inteligencia del niño.",
            "",
            "📏 NIVEL DE COMPLEJIDAD SEGÚN EDAD:",
        ])
        
        # Añadir guía de complejidad si hay edad especificada
        if nivel_edad:
            prompt_parts.append(f"   Importante: {nivel_edad.get('importante', '')}")
            for edad_rango in ["2-3_años", "4-5_años", "5-6_años"]:
                edad_info = nivel_edad.get(edad_rango, {})
                if edad_info:
                    prompt_parts.append(f"   {edad_rango.replace('_', ' ')}: {edad_info.get('ejemplo', '')}")
        
        prompt_parts.extend([
            "",
            "Recomendaciones:",
            f"- Longitud: {recomendaciones.get('longitud_texto', 'Sin especificar')}",
            f"- Párrafos: {recomendaciones.get('parrafos', 'Sin especificar')}",
            f"- Lenguaje sensorial: {recomendaciones.get('lenguaje_sensorial', 'Sin especificar')}",
            f"- Diálogos: {recomendaciones.get('dialogos', 'Sin especificar')}",
            f"- Ritmo: {recomendaciones.get('ritmo', 'Sin especificar')}",
            f"- Test voz alta: {recomendaciones.get('test_voz_alta', 'Si no suena bien al leer en voz alta, reescribir')}",
            "Flexibilidad sugerida:",
            f"- Variación temática: {', '.join(flex.get('variacion_tematica', [])) or 'Sin especificar'}",
            f"- Variación de escenarios: {', '.join(flex.get('variacion_escenarios', [])) or 'Sin especificar'}",
            f"- Elementos opcionales: {', '.join(flex.get('elementos_opcionales', [])) or 'Sin especificar'}",
            "Inputs del usuario:",
            self._format_list(user_lines),
        ])

        # Añadir ejemplos de RAG si están disponibles
        if similar_stories:
            examples_section = self._build_examples_section(similar_stories)
            if examples_section:
                prompt_parts.extend(examples_section)
        
        # Añadir lecciones aprendidas si está habilitado
        if apply_lessons:
            lessons_section = self._build_lessons_section()
            if lessons_section:
                prompt_parts.extend(lessons_section)
        
        # Añadir NOTA CRÍTICA DE OFICIO (máxima prominencia)
        nota_critica = guia.get("nota_critica_de_oficio", {})
        if nota_critica:
            prompt_parts.extend([
                "",
                "=" * 80,
                "🔥 REGLA IRROMPIBLE DE LITERATURA INFANTIL DE CALIDAD:",
                "=" * 80,
                f"{nota_critica.get('titulo', '')}",
                "",
                f"PRINCIPIO: {nota_critica.get('principio', '')}",
                f"POR QUÉ ES VITAL: {nota_critica.get('porque_es_vital', '')}",
                "",
                "EJEMPLOS CRÍTICOS - Aprende la diferencia:",
            ])
            
            ejemplos = nota_critica.get("ejemplos_criticos", {})
            for emocion, ejemplo in list(ejemplos.items())[:3]:  # Primeros 3 ejemplos
                prompt_parts.append(f"  {emocion.upper()}:")
                prompt_parts.append(f"    {ejemplo.get('nominacion_mal', '')}")
                prompt_parts.append(f"    {ejemplo.get('evocacion_bien', '')}")
            
            prompt_parts.extend([
                "",
                "⚠️ REGLA IRROMPIBLE:",
                f"{nota_critica.get('regla_irrompible', '')}",
                "=" * 80,
                ""
            ])
        
        prompt_parts.extend([
            "",
            "⭐ INSTRUCCIÓN CLAVE:",
            "Elige UNA de las estructuras alternativas listadas arriba.",
            "NO repitas el patrón: inseguridad → problema → característica especial → moraleja + pregunta.",
            "VARÍA la longitud de los párrafos para crear ritmo narrativo.",
            "Usa cierres diversos: NO termines SIEMPRE con pregunta directa al lector.",
            "IMPORTANTE: Mantén la coherencia visual y narrativa del personaje a lo largo del cuento.",
            "Entrega un texto único, cálido y coherente, evitando clichés explícitos.",
        ])

        final_prompt = "\n".join(prompt_parts)
        
        # Añadir instrucción final para el formato de salida JSON
        final_prompt += """

⭐ FORMATO DE SALIDA REQUERIDO:
Entrega tu respuesta EXCLUSIVAMENTE en formato JSON, con dos claves:
{
  "title": "El título del cuento",
  "content": "El contenido completo del cuento aquí, estructurado con párrafos y saltos de línea."
}
Asegúrate de que el contenido del cuento sea una cadena de texto larga y coherente.
NO incluyas ningún texto o comentario fuera del objeto JSON.
"""
        print(f"[prompt_service] ✅ Prompt construido ({len(final_prompt)} caracteres)")
        
        return final_prompt

    def refresh_style_guide(self):
        """Forzar recarga de la guía de estilo"""
        self._style_guide = None


# Instancia singleton
prompt_service = PromptService()