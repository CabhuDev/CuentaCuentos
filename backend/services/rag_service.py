# Servicio RAG (Retrieval-Augmented Generation)
# Búsqueda semántica de cuentos similares para mejorar generación

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.database_sqlite import Story, Critique
from services.gemini_service import GeminiService
import math


class RAGService:
    """
    Servicio de Retrieval-Augmented Generation.
    Busca cuentos similares exitosos para usar como ejemplos en la generación.
    """
    
    def __init__(self):
        self._embedding_cache = {}  # Cache de embeddings de temas
        self._gemini_service = None
    
    def _get_gemini_service(self):
        """Lazy loading de GeminiService"""
        if self._gemini_service is None:
            self._gemini_service = GeminiService()
        return self._gemini_service
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcula similitud coseno entre dos vectores.
        Retorna valor entre 0 (totalmente diferente) y 1 (idéntico).
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        # Producto punto
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def get_theme_embedding(self, theme: str) -> Optional[List[float]]:
        """
        Obtiene embedding de un tema, usando cache si está disponible.
        """
        # Normalizar tema para cache
        theme_key = theme.lower().strip()
        
        # Buscar en cache
        if theme_key in self._embedding_cache:
            print(f"[RAG] ✅ Embedding en cache: '{theme_key}'")
            return self._embedding_cache[theme_key]
        
        # Generar nuevo embedding
        print(f"[RAG] 🔄 Generando embedding para: '{theme_key}'")
        gemini = self._get_gemini_service()
        embedding = await gemini.generate_embedding(theme)
        
        if embedding:
            self._embedding_cache[theme_key] = embedding
            print(f"[RAG] ✅ Embedding cacheado: '{theme_key}'")
        
        return embedding
    
    async def search_similar_stories(
        self,
        db: Session,
        theme: str,
        target_age: Optional[int] = None,
        top_k: int = 2,
        min_similarity: float = 0.5,
        min_score: float = 7.0
    ) -> List[Dict[str, Any]]:
        """
        Busca cuentos similares al tema con buen score de crítica.
        
        Args:
            db: Sesión de base de datos
            theme: Tema del cuento a generar
            target_age: Edad objetivo (opcional, para pre-filtrado)
            top_k: Número máximo de ejemplos a retornar
            min_similarity: Similitud mínima (0-1)
            min_score: Score mínimo de crítica
            
        Returns:
            Lista de cuentos similares con metadata
        """
        print(f"[RAG] 🔍 Buscando cuentos similares a: '{theme}'")
        
        # 1. Generar embedding del tema
        theme_embedding = await self.get_theme_embedding(theme)
        if not theme_embedding:
            print("[RAG] ⚠️ No se pudo generar embedding del tema")
            return []
        
        # 2. Pre-filtrado por metadatos (SQL, muy rápido)
        query = db.query(Story).filter(
            Story.embedding_json.isnot(None),
            Story.content.isnot(None)
        )
        
        # Filtrar por edad si se especifica (±1 año de tolerancia)
        if target_age:
            # SQLite no tiene target_age en Story, pero podemos agregarlo después
            # Por ahora, omitimos este filtro
            pass
        
        candidates = query.all()
        print(f"[RAG] 📊 Candidatos pre-filtrados: {len(candidates)} cuentos")
        
        if not candidates:
            print("[RAG] ⚠️ No hay cuentos con embeddings en la BD")
            return []
        
        # 3. Calcular similitudes
        similarities = []
        for story in candidates:
            try:
                # Parsear embedding JSON
                story_embedding = story.embedding_json
                if isinstance(story_embedding, str):
                    story_embedding = json.loads(story_embedding)
                
                # Calcular similitud
                similarity = self.cosine_similarity(theme_embedding, story_embedding)
                
                # Obtener score de crítica (si existe)
                critique = db.query(Critique).filter(
                    Critique.story_id == story.id
                ).order_by(Critique.timestamp.desc()).first()
                
                critique_score = critique.score if critique else 0.0
                
                # Aplicar filtros
                if similarity >= min_similarity and critique_score >= min_score:
                    similarities.append({
                        'story': story,
                        'similarity': similarity,
                        'score': critique_score,
                        'critique': critique
                    })
            
            except Exception as e:
                print(f"[RAG] ⚠️ Error procesando cuento {story.id}: {e}")
                continue
        
        print(f"[RAG] ✅ Encontrados {len(similarities)} cuentos que cumplen criterios")
        
        # 4. Ordenar por similitud (descendente) y tomar top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_stories = similarities[:top_k]
        
        # 5. Formatear resultado
        results = []
        for idx, item in enumerate(top_stories, 1):
            story = item['story']
            
            # Crear fragmento (primeros 250 caracteres)
            fragment = story.content[:250] + "..." if len(story.content) > 250 else story.content
            
            # Extraer técnicas de la crítica si existe
            techniques = []
            if item['critique'] and item['critique'].critique_text:
                try:
                    # El critique_text contiene el JSON completo como string
                    critique_data = json.loads(item['critique'].critique_text)
                    
                    # Extraer fortalezas del feedback
                    feedback = critique_data.get('feedback', {})
                    strengths = feedback.get('strengths', [])
                    techniques = strengths[:3]  # Top 3 fortalezas
                except (json.JSONDecodeError, AttributeError, KeyError) as e:
                    # Si falla el parsing, continuar sin técnicas
                    pass
            
            results.append({
                'story_id': story.id,
                'title': story.title or 'Sin título',
                'fragment': fragment,
                'similarity': round(item['similarity'], 3),
                'score': round(item['score'], 1),
                'techniques': techniques,
                'rank': idx
            })
        
        print(f"[RAG] 🎯 Retornando top {len(results)} ejemplos")
        for result in results:
            print(f"[RAG]   #{result['rank']}: '{result['title']}' - "
                  f"Similitud: {result['similarity']} - Score: {result['score']}/10")
        
        return results


# Instancia global (singleton)
rag_service = RAGService()
