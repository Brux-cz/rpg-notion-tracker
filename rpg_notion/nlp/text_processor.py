"""
Hlavní modul pro zpracování textu.
"""
import logging
from typing import Dict, List, Optional, Set, Tuple, Union

from rpg_notion.models.entities import (
    AdventureJournalEntry, BaseEntity, EntityType, Event, Faction, Item, Location, Monster, NPC, Quest
)
from rpg_notion.models.repository import EntityRepository
from rpg_notion.nlp.attribute_extractor import AttributeExtractor
from rpg_notion.nlp.categorizer import EntityCategorizer
from rpg_notion.nlp.entity_matcher import EntityMatcher
from rpg_notion.nlp.ner import EntityExtractor

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Hlavní třída pro zpracování textu.
    """

    def __init__(
        self,
        entity_repository: Optional[EntityRepository] = None,
        entity_extractor: Optional[EntityExtractor] = None,
        attribute_extractor: Optional[AttributeExtractor] = None,
        entity_categorizer: Optional[EntityCategorizer] = None,
        entity_matcher: Optional[EntityMatcher] = None,
    ):
        """
        Inicializace procesoru textu.

        Args:
            entity_repository: Repozitář entit.
            entity_extractor: Extraktor entit.
            attribute_extractor: Extraktor atributů.
            entity_categorizer: Kategorizátor entit.
            entity_matcher: Matcher entit.
        """
        self.entity_repository = entity_repository or EntityRepository()
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.attribute_extractor = attribute_extractor or AttributeExtractor()
        self.entity_categorizer = entity_categorizer or EntityCategorizer()
        self.entity_matcher = entity_matcher or EntityMatcher()

    def process_text(self, text: str) -> Dict[str, List[BaseEntity]]:
        """
        Zpracuje text a extrahuje z něj entity.

        Args:
            text: Text k zpracování.

        Returns:
            Slovník s extrahovanými entitami podle typu.
        """
        # Extrakce entit z textu
        extracted_entities = self.entity_extractor.extract_entities(text)
        
        # Inicializace slovníku pro výsledné entity
        result_entities = {
            EntityType.NPC.value: [],
            EntityType.LOCATION.value: [],
            EntityType.MONSTER.value: [],
            EntityType.ITEM.value: [],
            EntityType.QUEST.value: [],
            EntityType.FACTION.value: [],
            EntityType.EVENT.value: [],
        }
        
        # Zpracování NPC
        for entity_data in extracted_entities[EntityType.NPC.value]:
            entity_name = entity_data["text"]
            
            # Hledání existující entity v repozitáři
            existing_entity = self.entity_repository.find_by_name(EntityType.NPC, entity_name)
            
            if existing_entity:
                # Aktualizace existující entity
                self._update_npc(existing_entity, text, entity_name)
                result_entities[EntityType.NPC.value].append(existing_entity)
            else:
                # Vytvoření nové entity
                new_entity = self._create_npc(text, entity_name)
                result_entities[EntityType.NPC.value].append(new_entity)
        
        # Zpracování lokací
        for entity_data in extracted_entities[EntityType.LOCATION.value]:
            entity_name = entity_data["text"]
            
            # Hledání existující entity v repozitáři
            existing_entity = self.entity_repository.find_by_name(EntityType.LOCATION, entity_name)
            
            if existing_entity:
                # Aktualizace existující entity
                self._update_location(existing_entity, text, entity_name)
                result_entities[EntityType.LOCATION.value].append(existing_entity)
            else:
                # Vytvoření nové entity
                new_entity = self._create_location(text, entity_name)
                result_entities[EntityType.LOCATION.value].append(new_entity)
        
        # Zpracování příšer
        for entity_data in extracted_entities[EntityType.MONSTER.value]:
            entity_name = entity_data["text"]
            
            # Hledání existující entity v repozitáři
            existing_entity = self.entity_repository.find_by_name(EntityType.MONSTER, entity_name)
            
            if existing_entity:
                # Aktualizace existující entity
                self._update_monster(existing_entity, text, entity_name)
                result_entities[EntityType.MONSTER.value].append(existing_entity)
            else:
                # Vytvoření nové entity
                new_entity = self._create_monster(text, entity_name)
                result_entities[EntityType.MONSTER.value].append(new_entity)
        
        # Zpracování předmětů
        for entity_data in extracted_entities[EntityType.ITEM.value]:
            entity_name = entity_data["text"]
            
            # Hledání existující entity v repozitáři
            existing_entity = self.entity_repository.find_by_name(EntityType.ITEM, entity_name)
            
            if existing_entity:
                # Aktualizace existující entity
                self._update_item(existing_entity, text, entity_name)
                result_entities[EntityType.ITEM.value].append(existing_entity)
            else:
                # Vytvoření nové entity
                new_entity = self._create_item(text, entity_name)
                result_entities[EntityType.ITEM.value].append(new_entity)
        
        # Extrakce vztahů mezi entitami
        relationships = self.entity_extractor.extract_relationships(text)
        
        # Zpracování vztahů
        for relationship in relationships:
            subject_type = relationship["subject_type"]
            object_type = relationship["object_type"]
            
            # Mapování typů entit ze spaCy na naše typy
            entity_type_mapping = {
                "PERSON": EntityType.NPC,
                "LOCATION": EntityType.LOCATION,
                "GPE": EntityType.LOCATION,
                "FAC": EntityType.LOCATION,
                "MONSTER": EntityType.MONSTER,
                "ITEM": EntityType.ITEM,
                "ORG": EntityType.FACTION,
                "EVENT": EntityType.EVENT,
            }
            
            subject_entity_type = entity_type_mapping.get(subject_type)
            object_entity_type = entity_type_mapping.get(object_type)
            
            if subject_entity_type and object_entity_type:
                # Hledání entit v repozitáři
                subject_entity = self.entity_repository.find_by_name(subject_entity_type, relationship["subject"])
                object_entity = self.entity_repository.find_by_name(object_entity_type, relationship["object"])
                
                # Pokud entity existují, vytvoříme vztah
                if subject_entity and object_entity:
                    self._create_relationship(subject_entity, object_entity, relationship["predicate"])
        
        return result_entities

    def _create_npc(self, text: str, npc_name: str) -> NPC:
        """
        Vytvoří novou NPC postavu.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            npc_name: Jméno NPC.

        Returns:
            Vytvořená NPC postava.
        """
        # Extrakce atributů
        attributes = self.attribute_extractor.extract_npc_attributes(text, npc_name)
        
        # Kategorizace a tagování
        tags = self.entity_categorizer.categorize_npc(text, npc_name)
        
        # Vytvoření NPC
        npc = NPC(
            name=npc_name,
            description=attributes["description"],
            status=attributes["status"],
            occupation=attributes["occupation"],
            history=attributes["history"],
            tags=tags,
        )
        
        # Uložení NPC do repozitáře
        return self.entity_repository.create_npc(npc)

    def _update_npc(self, npc: NPC, text: str, npc_name: str) -> None:
        """
        Aktualizuje existující NPC postavu.

        Args:
            npc: NPC postava k aktualizaci.
            text: Text, ze kterého se mají extrahovat atributy.
            npc_name: Jméno NPC.
        """
        # Extrakce atributů
        attributes = self.attribute_extractor.extract_npc_attributes(text, npc_name)
        
        # Kategorizace a tagování
        tags = self.entity_categorizer.categorize_npc(text, npc_name)
        
        # Aktualizace NPC
        if attributes["description"] and not npc.description:
            npc.description = attributes["description"]
        
        if attributes["status"] != "Živý" or npc.status != attributes["status"]:
            # Aktualizace stavu pouze pokud se změnil nebo není výchozí
            npc.status = attributes["status"]
        
        if attributes["occupation"] and not npc.occupation:
            npc.occupation = attributes["occupation"]
        
        if attributes["history"]:
            if npc.history:
                npc.history += "\n\n" + attributes["history"]
            else:
                npc.history = attributes["history"]
        
        # Aktualizace tagů
        npc.tags = list(set(npc.tags + tags))
        
        # Extrakce změn stavu
        state_changes = self.entity_extractor.extract_state_changes(text, npc_name)
        
        # Aktualizace historie na základě změn stavu
        for state_change in state_changes:
            if npc.history:
                npc.history += f"\n\n[Změna stavu] {state_change['sentence']}"
            else:
                npc.history = f"[Změna stavu] {state_change['sentence']}"

    def _create_location(self, text: str, location_name: str) -> Location:
        """
        Vytvoří novou lokaci.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            location_name: Název lokace.

        Returns:
            Vytvořená lokace.
        """
        # Extrakce atributů
        attributes = self.attribute_extractor.extract_location_attributes(text, location_name)
        
        # Kategorizace a tagování
        tags = self.entity_categorizer.categorize_location(text, location_name)
        
        # Vytvoření lokace
        location = Location(
            name=location_name,
            location_type=attributes["location_type"] or "Město",  # Výchozí hodnota
            hierarchy=attributes["hierarchy"],
            description=attributes["description"],
            status=attributes["status"],
            tags=tags,
        )
        
        # Uložení lokace do repozitáře
        return self.entity_repository.create_location(location)

    def _update_location(self, location: Location, text: str, location_name: str) -> None:
        """
        Aktualizuje existující lokaci.

        Args:
            location: Lokace k aktualizaci.
            text: Text, ze kterého se mají extrahovat atributy.
            location_name: Název lokace.
        """
        # Extrakce atributů
        attributes = self.attribute_extractor.extract_location_attributes(text, location_name)
        
        # Kategorizace a tagování
        tags = self.entity_categorizer.categorize_location(text, location_name)
        
        # Aktualizace lokace
        if attributes["location_type"] and not location.location_type:
            location.location_type = attributes["location_type"]
        
        if attributes["hierarchy"] and not location.hierarchy:
            location.hierarchy = attributes["hierarchy"]
        
        if attributes["description"] and not location.description:
            location.description = attributes["description"]
        
        if attributes["status"] != "Bezpečné" or location.status != attributes["status"]:
            # Aktualizace stavu pouze pokud se změnil nebo není výchozí
            location.status = attributes["status"]
        
        # Aktualizace tagů
        location.tags = list(set(location.tags + tags))

    def _create_monster(self, text: str, monster_name: str) -> Monster:
        """
        Vytvoří novou příšeru.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            monster_name: Název příšery.

        Returns:
            Vytvořená příšera.
        """
        # Extrakce atributů
        attributes = self.attribute_extractor.extract_monster_attributes(text, monster_name)
        
        # Kategorizace a tagování
        tags = self.entity_categorizer.categorize_monster(text, monster_name)
        
        # Vytvoření příšery
        monster = Monster(
            name=monster_name,
            description=attributes["description"],
            status=attributes["status"],
            combat_history=attributes["combat_history"],
            weaknesses_strengths=attributes["weaknesses_strengths"],
            tags=tags,
        )
        
        # Uložení příšery do repozitáře
        return self.entity_repository.create_monster(monster)

    def _update_monster(self, monster: Monster, text: str, monster_name: str) -> None:
        """
        Aktualizuje existující příšeru.

        Args:
            monster: Příšera k aktualizaci.
            text: Text, ze kterého se mají extrahovat atributy.
            monster_name: Název příšery.
        """
        # Extrakce atributů
        attributes = self.attribute_extractor.extract_monster_attributes(text, monster_name)
        
        # Kategorizace a tagování
        tags = self.entity_categorizer.categorize_monster(text, monster_name)
        
        # Aktualizace příšery
        if attributes["description"] and not monster.description:
            monster.description = attributes["description"]
        
        if attributes["status"] != "Živá" or monster.status != attributes["status"]:
            # Aktualizace stavu pouze pokud se změnil nebo není výchozí
            monster.status = attributes["status"]
        
        if attributes["combat_history"]:
            if monster.combat_history:
                monster.combat_history += "\n\n" + attributes["combat_history"]
            else:
                monster.combat_history = attributes["combat_history"]
        
        if attributes["weaknesses_strengths"] and not monster.weaknesses_strengths:
            monster.weaknesses_strengths = attributes["weaknesses_strengths"]
        
        # Aktualizace tagů
        monster.tags = list(set(monster.tags + tags))
        
        # Extrakce změn stavu
        state_changes = self.entity_extractor.extract_state_changes(text, monster_name)
        
        # Aktualizace historie soubojů na základě změn stavu
        for state_change in state_changes:
            if monster.combat_history:
                monster.combat_history += f"\n\n[Změna stavu] {state_change['sentence']}"
            else:
                monster.combat_history = f"[Změna stavu] {state_change['sentence']}"

    def _create_item(self, text: str, item_name: str) -> Item:
        """
        Vytvoří nový předmět.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            item_name: Název předmětu.

        Returns:
            Vytvořený předmět.
        """
        # Extrakce atributů
        attributes = self.attribute_extractor.extract_item_attributes(text, item_name)
        
        # Kategorizace a tagování
        tags = self.entity_categorizer.categorize_item(text, item_name)
        
        # Vytvoření předmětu
        item = Item(
            name=item_name,
            item_type=attributes["item_type"] or "Běžný předmět",  # Výchozí hodnota
            description=attributes["description"],
            ownership_history=attributes["ownership_history"],
            special_abilities=attributes["special_abilities"],
            tags=tags,
        )
        
        # Uložení předmětu do repozitáře
        return self.entity_repository.create_item(item)

    def _update_item(self, item: Item, text: str, item_name: str) -> None:
        """
        Aktualizuje existující předmět.

        Args:
            item: Předmět k aktualizaci.
            text: Text, ze kterého se mají extrahovat atributy.
            item_name: Název předmětu.
        """
        # Extrakce atributů
        attributes = self.attribute_extractor.extract_item_attributes(text, item_name)
        
        # Kategorizace a tagování
        tags = self.entity_categorizer.categorize_item(text, item_name)
        
        # Aktualizace předmětu
        if attributes["item_type"] and not item.item_type:
            item.item_type = attributes["item_type"]
        
        if attributes["description"] and not item.description:
            item.description = attributes["description"]
        
        if attributes["ownership_history"]:
            if item.ownership_history:
                item.ownership_history += "\n\n" + attributes["ownership_history"]
            else:
                item.ownership_history = attributes["ownership_history"]
        
        if attributes["special_abilities"] and not item.special_abilities:
            item.special_abilities = attributes["special_abilities"]
        
        # Aktualizace tagů
        item.tags = list(set(item.tags + tags))

    def _create_relationship(self, subject_entity: BaseEntity, object_entity: BaseEntity, predicate: str) -> None:
        """
        Vytvoří vztah mezi entitami.

        Args:
            subject_entity: Subjekt vztahu.
            object_entity: Objekt vztahu.
            predicate: Predikát vztahu.
        """
        # Implementace vytvoření vztahu podle typu entit
        if isinstance(subject_entity, NPC) and isinstance(object_entity, NPC):
            # Vztah mezi NPC
            if subject_entity.related_npc_ids is None:
                subject_entity.related_npc_ids = []
            
            if object_entity.id and object_entity.id not in subject_entity.related_npc_ids:
                subject_entity.related_npc_ids.append(object_entity.id)
        
        elif isinstance(subject_entity, NPC) and isinstance(object_entity, Location):
            # Vztah NPC-lokace
            subject_entity.location_id = object_entity.id
        
        elif isinstance(subject_entity, NPC) and isinstance(object_entity, Item):
            # Vztah NPC-předmět
            if subject_entity.item_ids is None:
                subject_entity.item_ids = []
            
            if object_entity.id and object_entity.id not in subject_entity.item_ids:
                subject_entity.item_ids.append(object_entity.id)
                
            # Aktualizace vlastníka předmětu
            object_entity.owner_id = subject_entity.id
        
        elif isinstance(subject_entity, Location) and isinstance(object_entity, NPC):
            # Vztah lokace-NPC
            if subject_entity.npc_ids is None:
                subject_entity.npc_ids = []
            
            if object_entity.id and object_entity.id not in subject_entity.npc_ids:
                subject_entity.npc_ids.append(object_entity.id)
                
            # Aktualizace lokace NPC
            object_entity.location_id = subject_entity.id
        
        elif isinstance(subject_entity, Location) and isinstance(object_entity, Item):
            # Vztah lokace-předmět
            if subject_entity.item_ids is None:
                subject_entity.item_ids = []
            
            if object_entity.id and object_entity.id not in subject_entity.item_ids:
                subject_entity.item_ids.append(object_entity.id)
                
            # Aktualizace lokace předmětu
            object_entity.location_id = subject_entity.id
