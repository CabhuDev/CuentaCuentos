# Servicios de gestión de caracteres
import json
from typing import List, Dict, Any, Optional
from config import CHARACTERS_PATH


class CharacterService:
    def __init__(self):
        self._characters = None

    def load_characters(self) -> List[Dict[str, Any]]:
        """Cargar personajes desde archivo JSON"""
        if self._characters is None:
            if not CHARACTERS_PATH.exists():
                self._characters = []
            else:
                with CHARACTERS_PATH.open("r", encoding="utf-8") as file:
                    self._characters = json.load(file)
        return self._characters

    def get_character_by_id(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Obtener personaje por ID"""
        characters = self.load_characters()
        for char in characters:
            if char.get("id") == character_id:
                return char
        return None

    def get_character_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtener personaje por nombre"""
        characters = self.load_characters()
        for char in characters:
            if char.get("nombre", "").lower() == name.lower():
                return char
        return None

    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Obtener todos los personajes"""
        return self.load_characters()

    def refresh_characters(self):
        """Forzar recarga de personajes"""
        self._characters = None


# Instancia singleton
character_service = CharacterService()