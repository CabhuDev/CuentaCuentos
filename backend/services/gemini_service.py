# Servicio de integración con Gemini (usando nuevo SDK google-genai)
from google import genai
from typing import Optional, Dict, Any
from config import GEMINI_API_KEY


class GeminiService:
    def __init__(self):
        if GEMINI_API_KEY:
            # El nuevo SDK usa Client() que toma la API key de GEMINI_API_KEY env var
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self._configured = True
        else:
            self._configured = False

    def is_configured(self) -> bool:
        """Verifica si Gemini está configurado correctamente"""
        return self._configured

    async def generate_story(self, prompt: str) -> Optional[str]:
        """Genera un cuento usando Gemini 2.5 Flash"""
        if not self._configured:
            raise ValueError("Gemini API no está configurada. Verifica GEMINI_API_KEY.")
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generando cuento: {e}")
            return None

    async def generate_critique(self, story_content: str) -> Optional[Dict[str, Any]]:
        """Genera una crítica del cuento usando Gemini 2.5 Flash"""
        if not self._configured:
            raise ValueError("Gemini API no está configurada. Verifica GEMINI_API_KEY.")
        
        critique_prompt = f"""
        Analiza este cuento infantil y proporciona una crítica estructurada en formato JSON:

        CUENTO A ANALIZAR:
        {story_content}

        Proporciona tu respuesta en este formato JSON exacto:
        {{
            "evaluation": {{
                "score_coherence": [1-10],
                "score_pacing": [1-10], 
                "score_age_appropriateness": [1-10],
                "overall_score": [promedio de las anteriores]
            }},
            "feedback": {{
                "strengths": ["fortaleza 1", "fortaleza 2", ...],
                "areas_for_improvement": ["área de mejora 1", "área de mejora 2", ...],
                "actionable_lesson": "Lección específica y accionable para el próximo cuento"
            }}
        }}
        
        Evalúa considerando que es para niños de 2-6 años, debe tener coherencia narrativa, buen ritmo, y seguir los principios de "Cuentos para Crecer".
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=critique_prompt
            )
            
            # Limpiar respuesta (puede venir con markdown ```json...```)
            import json
            import re
            
            response_text = response.text.strip()
            print(f"[gemini_service] 📝 Respuesta cruda de Gemini: {response_text[:200]}...")
            
            # Remover bloques de markdown si existen
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            
            # Parsear JSON
            critique_data = json.loads(response_text)
            print(f"[gemini_service] ✅ JSON parseado correctamente")
            return critique_data
            
        except json.JSONDecodeError as e:
            print(f"Error parseando JSON de crítica: {e}")
            print(f"Respuesta recibida: {response.text[:500]}")
            return None
        except Exception as e:
            print(f"Error generando crítica: {e}")
            return None

    async def generate_illustration_template(self, story_content: str, story_title: str) -> Optional[Dict[str, Any]]:
        """Genera plantilla JSON para ilustraciones basada en el cuento"""
        if not self._configured:
            raise ValueError("Gemini API no está configurada. Verifica GEMINI_API_KEY.")
        
        template_prompt = f"""
        Genera una plantilla JSON para crear ilustraciones de este cuento infantil.

        TÍTULO: {story_title}
        CUENTO:
        {story_content}

        Crea un JSON con esta estructura exacta:
        {{
            "cuento_metadata": {{
                "titulo": "{story_title}",
                "formato": "Página Única (Canva Ready)",
                "estilo_visual": "Minimalismo infantil, trazo suave, estilo editorial premiado",
                "configuracion_color": {{
                    "fondo_canva": "#F8F9FA",
                    "primario_personaje": "[color hex basado en personaje principal]",
                    "secundario_detalles": "#2A4759",
                    "terciario_naturaleza": "#3B8C88"
                }}
            }},
            "composicion_diseno": {{
                "ilustraciones_superiores": {{
                    "tipo": "Cabecera / Trio de iconos decorativos",
                    "estilo": "Tres elementos individuales, diseño plano, colores de la paleta",
                    "iconos": [
                        {{
                            "elemento": "Icono 1: [elemento clave del cuento]",
                            "prompt_ia": "Minimalist children's book icon, [descripción detallada], soft digital style, isolated on white background, flat design --no shadows"
                        }},
                        {{
                            "elemento": "Icono 2: [segundo elemento]",
                            "prompt_ia": "Minimalist children's book icon, [descripción], isolated on white background, flat design"
                        }},
                        {{
                            "elemento": "Icono 3: [tercer elemento]",
                            "prompt_ia": "Minimalist children's book icon, [descripción], isolated on white background, flat design"
                        }}
                    ]
                }},
                "ilustracion_principal": {{
                    "tipo": "Escena de acción central/inferior",
                    "descripcion": "[Descripción de la escena principal del cuento]",
                    "instruccion_ia": "Main children's book illustration, [descripción detallada de personajes y acción], warm expression, isolated on white background, high quality watercolor texture --no background"
                }},
                "paleta_tipografica_sugerida": {{
                    "titulos": "[color para títulos]",
                    "cuerpo_texto": "#2A4759",
                    "destacados": "#3B8C88"
                }}
            }}
        }}

        IMPORTANTE: 
        - Los prompts de IA deben ser EN INGLÉS y muy descriptivos
        - Incluye detalles de color usando la paleta definida
        - Los iconos deben representar 3 elementos clave del cuento
        - La ilustración principal debe capturar el momento culminante
        - Usa el estilo "minimalist children's book" en todos los prompts
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=template_prompt
            )
            
            import json
            import re
            
            response_text = response.text.strip()
            print(f"[gemini_service] 🎨 Generando plantilla de ilustraciones...")
            
            # Remover bloques de markdown si existen
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            
            template_data = json.loads(response_text)
            print(f"[gemini_service] ✅ Plantilla de ilustraciones generada")
            return template_data
            
        except json.JSONDecodeError as e:
            print(f"Error parseando JSON de plantilla: {e}")
            print(f"Respuesta recibida: {response.text[:500]}")
            return None
        except Exception as e:
            print(f"Error generando plantilla de ilustraciones: {e}")
            return None

    async def generate_embedding(self, text: str) -> Optional[list]:
        """Genera embedding de un texto"""
        if not self._configured:
            raise ValueError("Gemini API no está configurada. Verifica GEMINI_API_KEY.")
        
        try:
            # Nuevo SDK usa el método embed_content desde el cliente
            # IMPORTANTE: El parámetro es 'contents' (plural), no 'content'
            result = self.client.models.embed_content(
                model="models/text-embedding-004",
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Error generando embedding: {e}")
            return None


# Instancia singleton
gemini_service = GeminiService()