# Servicio de aprendizaje evolutivo
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class LearningService:
    """Servicio para gestionar el bucle de aprendizaje evolutivo"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.learning_history_file = self.data_dir / "learning_history.json"
        self.style_profile_file = self.data_dir / "style_profile.json"
    
    def load_learning_history(self) -> List[Dict]:
        """Carga el historial de lecciones aprendidas"""
        try:
            if self.learning_history_file.exists():
                with open(self.learning_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error cargando learning_history.json: {e}")
            return []
    
    def save_learning_history(self, history: List[Dict]) -> bool:
        """Guarda el historial de lecciones"""
        try:
            with open(self.learning_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            print(f"✅ Learning history guardado: {len(history)} lecciones")
            return True
        except Exception as e:
            print(f"❌ Error guardando learning_history.json: {e}")
            return False
    
    def load_style_profile(self) -> Dict:
        """Carga el perfil de estilo actual"""
        try:
            if self.style_profile_file.exists():
                with open(self.style_profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error cargando style_profile.json: {e}")
            return {}
    
    def save_style_profile(self, profile: Dict) -> bool:
        """Guarda el perfil de estilo actualizado"""
        try:
            with open(self.style_profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            print(f"✅ Style profile actualizado")
            return True
        except Exception as e:
            print(f"❌ Error guardando style_profile.json: {e}")
            return False
    
    def add_lessons_to_history(self, synthesis_data: Dict, critique_ids: List[str]) -> bool:
        """
        Añade nuevas lecciones al historial desde una síntesis de Gemini
        
        Args:
            synthesis_data: Resultado de gemini_service.synthesize_lessons()
            critique_ids: IDs de las críticas que se usaron para la síntesis
        """
        try:
            history = self.load_learning_history()
            next_id = max([lesson.get('lesson_id', 0) for lesson in history], default=0) + 1
            
            lessons_learned = synthesis_data.get('lessons_learned', [])
            today = datetime.utcnow().strftime('%Y-%m-%d')
            
            for lesson_data in lessons_learned:
                new_lesson = {
                    "lesson_id": next_id,
                    "origin_critique_ids": critique_ids,
                    "insight": lesson_data.get('insight', ''),
                    "category": lesson_data.get('category', 'general'),
                    "priority": lesson_data.get('priority', 'medium'),
                    "actionable_guidance": lesson_data.get('actionable_guidance', ''),
                    "supporting_evidence": lesson_data.get('supporting_evidence', ''),
                    "applied_count": 0,
                    "effectiveness_score": None,
                    "status": "active",
                    "synthesized_at": today
                }
                history.append(new_lesson)
                next_id += 1
            
            return self.save_learning_history(history)
            
        except Exception as e:
            print(f"❌ Error añadiendo lecciones al historial: {e}")
            return False
    
    def update_style_profile(self, synthesis_data: Dict) -> bool:
        """
        Actualiza el perfil de estilo con insights de la síntesis
        
        Args:
            synthesis_data: Resultado de gemini_service.synthesize_lessons()
        """
        try:
            profile = self.load_style_profile()
            
            if not profile:
                print("⚠️ No se pudo cargar style_profile.json")
                return False
            
            # Actualizar métricas de evolución
            history = self.load_learning_history()
            active_lessons = [l for l in history if l.get('status') == 'active']
            
            if 'evolution_metrics' not in profile:
                profile['evolution_metrics'] = {}
            
            profile['evolution_metrics'].update({
                'last_synthesis': datetime.utcnow().strftime('%Y-%m-%d'),
                'lessons_active': len(active_lessons),
                'total_lessons_learned': len(history)
            })
            
            # Actualizar focos de aprendizaje
            style_adjustments = synthesis_data.get('style_adjustments', {})
            suggested_focus = style_adjustments.get('suggested_focus', '')
            
            if suggested_focus:
                if 'active_learning_focus' not in profile:
                    profile['active_learning_focus'] = []
                
                # Añadir nuevo foco si no existe
                if suggested_focus not in profile['active_learning_focus']:
                    profile['active_learning_focus'].insert(0, suggested_focus)
                    # Mantener solo los 3 focos más recientes
                    profile['active_learning_focus'] = profile['active_learning_focus'][:3]
            
            # Actualizar áreas a mejorar si existen
            areas_to_improve = style_adjustments.get('areas_to_improve', [])
            if areas_to_improve and 'stylistic_markers' in profile:
                profile['stylistic_markers']['current_improvement_areas'] = areas_to_improve[:3]
            
            return self.save_style_profile(profile)
            
        except Exception as e:
            print(f"❌ Error actualizando style_profile: {e}")
            return False
    
    def get_active_lessons(self, category: Optional[str] = None) -> List[Dict]:
        """
        Obtiene lecciones activas, opcionalmente filtradas por categoría
        
        Args:
            category: Categoría para filtrar (opcional)
        """
        history = self.load_learning_history()
        active = [l for l in history if l.get('status') == 'active']
        
        if category:
            active = [l for l in active if l.get('category') == category]
        
        return active
    
    def get_synthesis_statistics(self) -> Dict:
        """Obtiene estadísticas del sistema de aprendizaje"""
        history = self.load_learning_history()
        profile = self.load_style_profile()
        
        active_lessons = [l for l in history if l.get('status') == 'active']
        categories = {}
        
        for lesson in active_lessons:
            cat = lesson.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_lessons": len(history),
            "active_lessons": len(active_lessons),
            "lessons_by_category": categories,
            "last_synthesis": profile.get('evolution_metrics', {}).get('last_synthesis', 'never'),
            "current_focus_areas": profile.get('active_learning_focus', [])
        }


# Instancia singleton
learning_service = LearningService()
