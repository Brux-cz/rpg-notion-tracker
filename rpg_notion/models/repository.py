"""
Repozitář pro práci s entitami.
"""
import logging
from typing import Dict, List, Optional, Type, TypeVar, Union, cast

from rpg_notion.api.entity_manager import NotionEntityManager
from rpg_notion.api.notion_client import NotionClientWrapper
from rpg_notion.config.settings import NOTION_DATABASE_IDS
from rpg_notion.models.converters import NotionConverter
from rpg_notion.models.entities import (
    AdventureJournalEntry, BaseEntity, EntityType, Event, Faction, Item, Location, Monster, NPC, Quest
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseEntity)


class EntityRepository:
    """
    Repozitář pro práci s entitami.
    """

    def __init__(
        self, notion_client: Optional[NotionClientWrapper] = None, entity_manager: Optional[NotionEntityManager] = None
    ):
        """
        Inicializace repozitáře.

        Args:
            notion_client: Instance NotionClientWrapper. Pokud není zadána, vytvoří se nová.
            entity_manager: Instance NotionEntityManager. Pokud není zadána, vytvoří se nová.
        """
        self.client = notion_client or NotionClientWrapper()
        self.entity_manager = entity_manager or NotionEntityManager(self.client)
        self.database_ids = NOTION_DATABASE_IDS.copy()
        self.converter = NotionConverter()

    def _get_database_id_for_entity_type(self, entity_type: EntityType) -> str:
        """
        Získá ID databáze pro daný typ entity.

        Args:
            entity_type: Typ entity.

        Returns:
            ID databáze.

        Raises:
            ValueError: Pokud není nalezeno ID databáze pro daný typ entity.
        """
        if entity_type == EntityType.NPC:
            db_id = self.database_ids.get("npcs")
        elif entity_type == EntityType.LOCATION:
            db_id = self.database_ids.get("locations")
        elif entity_type == EntityType.MONSTER:
            db_id = self.database_ids.get("monsters")
        elif entity_type == EntityType.ITEM:
            db_id = self.database_ids.get("items")
        elif entity_type == EntityType.QUEST:
            db_id = self.database_ids.get("quests")
        elif entity_type == EntityType.FACTION:
            db_id = self.database_ids.get("factions")
        elif entity_type == EntityType.EVENT:
            db_id = self.database_ids.get("events")
        elif entity_type == EntityType.ADVENTURE_JOURNAL:
            db_id = self.database_ids.get("adventure_journal")
        else:
            raise ValueError(f"Neplatný typ entity: {entity_type}")

        if not db_id:
            raise ValueError(f"Nenalezeno ID databáze pro typ entity: {entity_type}")

        return db_id

    def find_by_name(self, entity_type: EntityType, name: str) -> Optional[BaseEntity]:
        """
        Najde entitu podle názvu.

        Args:
            entity_type: Typ entity.
            name: Název entity.

        Returns:
            Nalezená entita nebo None, pokud entita nebyla nalezena.
        """
        db_id = self._get_database_id_for_entity_type(entity_type)
        page = self.entity_manager.find_entity_by_name(db_id, name)
        
        if page:
            return self.converter.notion_to_entity(page, entity_type)
        return None

    def find_all(self, entity_type: EntityType) -> List[BaseEntity]:
        """
        Najde všechny entity daného typu.

        Args:
            entity_type: Typ entity.

        Returns:
            Seznam entit.
        """
        db_id = self._get_database_id_for_entity_type(entity_type)
        pages = self.client.query_database(db_id)
        
        return [self.converter.notion_to_entity(page, entity_type) for page in pages]

    def create_npc(self, npc: NPC) -> NPC:
        """
        Vytvoří novou NPC postavu.

        Args:
            npc: NPC postava.

        Returns:
            Vytvořená NPC postava.
        """
        page = self.entity_manager.create_npc(
            name=npc.name,
            description=npc.description,
            status=npc.status,
            occupation=npc.occupation,
            location_id=npc.location_id,
            related_npc_ids=npc.related_npc_ids,
            item_ids=npc.item_ids,
            history=npc.history,
            tags=npc.tags,
        )
        
        return cast(NPC, self.converter.notion_to_entity(page, EntityType.NPC))

    def create_location(self, location: Location) -> Location:
        """
        Vytvoří novou lokaci.

        Args:
            location: Lokace.

        Returns:
            Vytvořená lokace.
        """
        page = self.entity_manager.create_location(
            name=location.name,
            location_type=location.location_type,
            hierarchy=location.hierarchy,
            description=location.description,
            npc_ids=location.npc_ids,
            item_ids=location.item_ids,
            event_ids=location.event_ids,
            status=location.status,
            tags=location.tags,
        )
        
        return cast(Location, self.converter.notion_to_entity(page, EntityType.LOCATION))

    def create_monster(self, monster: Monster) -> Monster:
        """
        Vytvoří novou příšeru.

        Args:
            monster: Příšera.

        Returns:
            Vytvořená příšera.
        """
        page = self.entity_manager.create_monster(
            name=monster.name,
            description=monster.description,
            location_ids=monster.location_ids,
            status=monster.status,
            combat_history=monster.combat_history,
            weaknesses_strengths=monster.weaknesses_strengths,
            loot_ids=monster.loot_ids,
            tags=monster.tags,
        )
        
        return cast(Monster, self.converter.notion_to_entity(page, EntityType.MONSTER))

    def create_item(self, item: Item) -> Item:
        """
        Vytvoří nový předmět.

        Args:
            item: Předmět.

        Returns:
            Vytvořený předmět.
        """
        page = self.entity_manager.create_item(
            name=item.name,
            item_type=item.item_type,
            description=item.description,
            location_id=item.location_id,
            owner_id=item.owner_id,
            ownership_history=item.ownership_history,
            special_abilities=item.special_abilities,
            tags=item.tags,
        )
        
        return cast(Item, self.converter.notion_to_entity(page, EntityType.ITEM))

    def create_quest(self, quest: Quest) -> Quest:
        """
        Vytvoří nový quest.

        Args:
            quest: Quest.

        Returns:
            Vytvořený quest.
        """
        page = self.entity_manager.create_quest(
            name=quest.name,
            description=quest.description,
            giver_id=quest.giver_id,
            status=quest.status,
            rewards=quest.rewards,
            location_ids=quest.location_ids,
            npc_ids=quest.npc_ids,
            timeline=quest.timeline,
            tags=quest.tags,
        )
        
        return cast(Quest, self.converter.notion_to_entity(page, EntityType.QUEST))

    def create_faction(self, faction: Faction) -> Faction:
        """
        Vytvoří novou frakci.

        Args:
            faction: Frakce.

        Returns:
            Vytvořená frakce.
        """
        page = self.entity_manager.create_faction(
            name=faction.name,
            description=faction.description,
            member_ids=faction.member_ids,
            territory_ids=faction.territory_ids,
            faction_relations=faction.faction_relations,
            player_relation=faction.player_relation,
            event_ids=faction.event_ids,
            tags=faction.tags,
        )
        
        return cast(Faction, self.converter.notion_to_entity(page, EntityType.FACTION))

    def create_event(self, event: Event) -> Event:
        """
        Vytvoří novou událost.

        Args:
            event: Událost.

        Returns:
            Vytvořená událost.
        """
        page = self.entity_manager.create_event(
            name=event.name,
            date=event.date,
            description=event.description,
            location_id=event.location_id,
            npc_ids=event.npc_ids,
            consequences=event.consequences,
            tags=event.tags,
        )
        
        return cast(Event, self.converter.notion_to_entity(page, EntityType.EVENT))

    def create_adventure_journal_entry(self, entry: AdventureJournalEntry) -> AdventureJournalEntry:
        """
        Vytvoří nový záznam v deníku dobrodružství.

        Args:
            entry: Záznam v deníku dobrodružství.

        Returns:
            Vytvořený záznam v deníku dobrodružství.
        """
        page = self.entity_manager.create_adventure_journal_entry(
            title=entry.name,
            date=entry.date,
            summary=entry.summary,
            event_ids=entry.event_ids,
            npc_ids=entry.npc_ids,
            location_ids=entry.location_ids,
        )
        
        return cast(AdventureJournalEntry, self.converter.notion_to_entity(page, EntityType.ADVENTURE_JOURNAL))

    def update_entity_history(self, entity: BaseEntity, new_entry: str) -> BaseEntity:
        """
        Aktualizuje historii entity.

        Args:
            entity: Entita.
            new_entry: Nový záznam historie.

        Returns:
            Aktualizovaná entita.
        """
        if not entity.notion_page_id:
            raise ValueError("Entita nemá nastavené notion_page_id")
        
        history_property = ""
        if isinstance(entity, NPC):
            history_property = "Historie změn"
        elif isinstance(entity, Item):
            history_property = "Historie vlastnictví"
        else:
            raise ValueError(f"Aktualizace historie není podporována pro typ entity: {entity.type}")
        
        page = self.entity_manager.update_entity_history(
            page_id=entity.notion_page_id,
            history_property=history_property,
            new_entry=new_entry,
        )
        
        return self.converter.notion_to_entity(page, entity.type)
