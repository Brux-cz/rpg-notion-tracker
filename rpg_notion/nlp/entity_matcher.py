"""
Modul pro fuzzy matching entit.
"""
import logging
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set, Tuple, Union

from rpg_notion.models.entities import BaseEntity, EntityType

logger = logging.getLogger(__name__)


class EntityMatcher:
    """
    Třída pro fuzzy matching entit.
    """

    def __init__(self, threshold: float = 0.7):
        """
        Inicializace matcheru entit.

        Args:
            threshold: Práh podobnosti pro fuzzy matching (0.0 - 1.0).
        """
        self.threshold = threshold

    def _normalize_text(self, text: str) -> str:
        """
        Normalizuje text pro porovnávání.

        Args:
            text: Text k normalizaci.

        Returns:
            Normalizovaný text.
        """
        # Převod na malá písmena
        text = text.lower()
        
        # Odstranění diakritiky
        text = self._remove_diacritics(text)
        
        # Odstranění interpunkce
        text = re.sub(r"[^\w\s]", "", text)
        
        # Odstranění nadbytečných mezer
        text = re.sub(r"\s+", " ", text).strip()
        
        return text

    def _remove_diacritics(self, text: str) -> str:
        """
        Odstraní diakritiku z textu.

        Args:
            text: Text, ze kterého se má odstranit diakritika.

        Returns:
            Text bez diakritiky.
        """
        # Mapování znaků s diakritikou na znaky bez diakritiky
        diacritics_map = {
            'á': 'a', 'č': 'c', 'ď': 'd', 'é': 'e', 'ě': 'e', 'í': 'i', 'ň': 'n',
            'ó': 'o', 'ř': 'r', 'š': 's', 'ť': 't', 'ú': 'u', 'ů': 'u', 'ý': 'y', 'ž': 'z',
            'Á': 'A', 'Č': 'C', 'Ď': 'D', 'É': 'E', 'Ě': 'E', 'Í': 'I', 'Ň': 'N',
            'Ó': 'O', 'Ř': 'R', 'Š': 'S', 'Ť': 'T', 'Ú': 'U', 'Ů': 'U', 'Ý': 'Y', 'Ž': 'Z'
        }
        
        # Nahrazení znaků s diakritikou
        for char, replacement in diacritics_map.items():
            text = text.replace(char, replacement)
        
        return text

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Vypočítá podobnost mezi dvěma texty.

        Args:
            text1: První text.
            text2: Druhý text.

        Returns:
            Podobnost mezi texty (0.0 - 1.0).
        """
        # Normalizace textů
        text1 = self._normalize_text(text1)
        text2 = self._normalize_text(text2)
        
        # Výpočet podobnosti pomocí SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()

    def find_matching_entity(self, entity_name: str, entities: List[BaseEntity]) -> Optional[BaseEntity]:
        """
        Najde entitu, která nejlépe odpovídá zadanému názvu.

        Args:
            entity_name: Název entity k vyhledání.
            entities: Seznam entit, ve kterých se má hledat.

        Returns:
            Nejlépe odpovídající entita nebo None, pokud žádná entita neodpovídá.
        """
        best_match = None
        best_similarity = 0.0
        
        for entity in entities:
            similarity = self._calculate_similarity(entity_name, entity.name)
            
            if similarity > best_similarity and similarity >= self.threshold:
                best_match = entity
                best_similarity = similarity
        
        return best_match

    def find_matching_entities(self, entity_name: str, entities: List[BaseEntity], max_results: int = 5) -> List[Tuple[BaseEntity, float]]:
        """
        Najde entity, které odpovídají zadanému názvu, seřazené podle podobnosti.

        Args:
            entity_name: Název entity k vyhledání.
            entities: Seznam entit, ve kterých se má hledat.
            max_results: Maximální počet výsledků.

        Returns:
            Seznam dvojic (entita, podobnost) seřazený podle podobnosti.
        """
        matches = []
        
        for entity in entities:
            similarity = self._calculate_similarity(entity_name, entity.name)
            
            if similarity >= self.threshold:
                matches.append((entity, similarity))
        
        # Seřazení podle podobnosti (sestupně)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Omezení počtu výsledků
        return matches[:max_results]

    def group_similar_entities(self, entities: List[BaseEntity]) -> List[List[BaseEntity]]:
        """
        Seskupí podobné entity.

        Args:
            entities: Seznam entit k seskupení.

        Returns:
            Seznam skupin podobných entit.
        """
        # Inicializace skupin
        groups = []
        
        # Procházení entit
        for entity in entities:
            # Hledání skupiny pro entitu
            found_group = False
            
            for group in groups:
                # Kontrola, zda entita patří do skupiny
                for group_entity in group:
                    similarity = self._calculate_similarity(entity.name, group_entity.name)
                    
                    if similarity >= self.threshold:
                        group.append(entity)
                        found_group = True
                        break
                
                if found_group:
                    break
            
            # Pokud entita nepatří do žádné skupiny, vytvoříme novou
            if not found_group:
                groups.append([entity])
        
        return groups

    def merge_entities(self, entities: List[BaseEntity]) -> BaseEntity:
        """
        Sloučí podobné entity do jedné.

        Args:
            entities: Seznam entit ke sloučení.

        Returns:
            Sloučená entita.
        """
        if not entities:
            raise ValueError("Seznam entit je prázdný.")
        
        # Použití první entity jako základu
        base_entity = entities[0]
        
        # Sloučení atributů z ostatních entit
        for entity in entities[1:]:
            # Sloučení tagů
            base_entity.tags = list(set(base_entity.tags + entity.tags))
            
            # Sloučení dalších atributů podle typu entity
            if hasattr(base_entity, "description") and hasattr(entity, "description"):
                if not getattr(base_entity, "description") and getattr(entity, "description"):
                    setattr(base_entity, "description", getattr(entity, "description"))
            
            if hasattr(base_entity, "history") and hasattr(entity, "history"):
                if getattr(entity, "history"):
                    if getattr(base_entity, "history"):
                        setattr(base_entity, "history", getattr(base_entity, "history") + "\n\n" + getattr(entity, "history"))
                    else:
                        setattr(base_entity, "history", getattr(entity, "history"))
        
        return base_entity
