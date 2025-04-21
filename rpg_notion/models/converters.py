"""
Konvertory mezi datovými modely a Notion záznamy.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from rpg_notion.models.entities import (
    AdventureJournalEntry, BaseEntity, EntityType, Event, Faction, Item, Location, Monster, NPC, Quest
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseEntity)


class NotionConverter:
    """
    Třída pro konverzi mezi datovými modely a Notion záznamy.
    """

    @staticmethod
    def _extract_title(properties: Dict[str, Any], property_name: str = "title") -> str:
        """
        Extrahuje název z vlastností Notion.

        Args:
            properties: Vlastnosti Notion.
            property_name: Název vlastnosti s názvem.

        Returns:
            Extrahovaný název.
        """
        title_property = properties.get(property_name, {})
        if not title_property:
            return ""
        
        title = title_property.get("title", [])
        if not title:
            return ""
        
        return "".join(item.get("plain_text", "") for item in title)

    @staticmethod
    def _extract_rich_text(properties: Dict[str, Any], property_name: str) -> str:
        """
        Extrahuje text z vlastností Notion.

        Args:
            properties: Vlastnosti Notion.
            property_name: Název vlastnosti s textem.

        Returns:
            Extrahovaný text.
        """
        text_property = properties.get(property_name, {})
        if not text_property:
            return ""
        
        rich_text = text_property.get("rich_text", [])
        if not rich_text:
            return ""
        
        return "".join(item.get("plain_text", "") for item in rich_text)

    @staticmethod
    def _extract_select(properties: Dict[str, Any], property_name: str) -> str:
        """
        Extrahuje vybranou možnost z vlastností Notion.

        Args:
            properties: Vlastnosti Notion.
            property_name: Název vlastnosti s výběrem.

        Returns:
            Extrahovaná vybraná možnost.
        """
        select_property = properties.get(property_name, {})
        if not select_property:
            return ""
        
        select = select_property.get("select", {})
        if not select:
            return ""
        
        return select.get("name", "")

    @staticmethod
    def _extract_multi_select(properties: Dict[str, Any], property_name: str) -> List[str]:
        """
        Extrahuje vybrané možnosti z vlastností Notion.

        Args:
            properties: Vlastnosti Notion.
            property_name: Název vlastnosti s více výběry.

        Returns:
            Seznam extrahovaných vybraných možností.
        """
        multi_select_property = properties.get(property_name, {})
        if not multi_select_property:
            return []
        
        multi_select = multi_select_property.get("multi_select", [])
        if not multi_select:
            return []
        
        return [item.get("name", "") for item in multi_select]

    @staticmethod
    def _extract_relation(properties: Dict[str, Any], property_name: str) -> List[str]:
        """
        Extrahuje ID propojených stránek z vlastností Notion.

        Args:
            properties: Vlastnosti Notion.
            property_name: Název vlastnosti s relací.

        Returns:
            Seznam ID propojených stránek.
        """
        relation_property = properties.get(property_name, {})
        if not relation_property:
            return []
        
        relation = relation_property.get("relation", [])
        if not relation:
            return []
        
        return [item.get("id", "") for item in relation]

    @staticmethod
    def _extract_date(properties: Dict[str, Any], property_name: str) -> Optional[datetime]:
        """
        Extrahuje datum z vlastností Notion.

        Args:
            properties: Vlastnosti Notion.
            property_name: Název vlastnosti s datem.

        Returns:
            Extrahované datum nebo None, pokud datum není nastaveno.
        """
        date_property = properties.get(property_name, {})
        if not date_property:
            return None
        
        date = date_property.get("date", {})
        if not date:
            return None
        
        start = date.get("start")
        if not start:
            return None
        
        try:
            return datetime.fromisoformat(start)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _extract_number(properties: Dict[str, Any], property_name: str) -> int:
        """
        Extrahuje číslo z vlastností Notion.

        Args:
            properties: Vlastnosti Notion.
            property_name: Název vlastnosti s číslem.

        Returns:
            Extrahované číslo.
        """
        number_property = properties.get(property_name, {})
        if not number_property:
            return 0
        
        number = number_property.get("number")
        if number is None:
            return 0
        
        return int(number)

    @classmethod
    def notion_to_npc(cls, page: Dict[str, Any]) -> NPC:
        """
        Konvertuje Notion stránku na NPC.

        Args:
            page: Notion stránka.

        Returns:
            NPC objekt.
        """
        properties = page.get("properties", {})
        
        return NPC(
            id=page.get("id"),
            name=cls._extract_title(properties, "Jméno"),
            description=cls._extract_rich_text(properties, "Popis"),
            status=cls._extract_select(properties, "Stav"),
            occupation=cls._extract_rich_text(properties, "Povolání/role"),
            location_id=cls._extract_relation(properties, "Lokace")[0] if cls._extract_relation(properties, "Lokace") else None,
            related_npc_ids=cls._extract_relation(properties, "Vztahy"),
            item_ids=cls._extract_relation(properties, "Významné předměty"),
            history=cls._extract_rich_text(properties, "Historie změn"),
            tags=cls._extract_multi_select(properties, "Tagy"),
            notion_page_id=page.get("id"),
            created_at=datetime.fromisoformat(page.get("created_time")) if page.get("created_time") else None,
            updated_at=datetime.fromisoformat(page.get("last_edited_time")) if page.get("last_edited_time") else None,
        )

    @classmethod
    def notion_to_location(cls, page: Dict[str, Any]) -> Location:
        """
        Konvertuje Notion stránku na lokaci.

        Args:
            page: Notion stránka.

        Returns:
            Location objekt.
        """
        properties = page.get("properties", {})
        
        return Location(
            id=page.get("id"),
            name=cls._extract_title(properties, "Název"),
            location_type=cls._extract_select(properties, "Typ"),
            hierarchy=cls._extract_rich_text(properties, "Hierarchie"),
            description=cls._extract_rich_text(properties, "Popis prostředí"),
            npc_ids=cls._extract_relation(properties, "Obyvatelé"),
            item_ids=cls._extract_relation(properties, "Významné objekty"),
            event_ids=cls._extract_relation(properties, "Události"),
            status=cls._extract_select(properties, "Stav"),
            tags=cls._extract_multi_select(properties, "Tagy"),
            notion_page_id=page.get("id"),
            created_at=datetime.fromisoformat(page.get("created_time")) if page.get("created_time") else None,
            updated_at=datetime.fromisoformat(page.get("last_edited_time")) if page.get("last_edited_time") else None,
        )

    @classmethod
    def notion_to_monster(cls, page: Dict[str, Any]) -> Monster:
        """
        Konvertuje Notion stránku na příšeru.

        Args:
            page: Notion stránka.

        Returns:
            Monster objekt.
        """
        properties = page.get("properties", {})
        
        return Monster(
            id=page.get("id"),
            name=cls._extract_title(properties, "Název/typ"),
            description=cls._extract_rich_text(properties, "Popis a schopnosti"),
            location_ids=cls._extract_relation(properties, "Místo výskytu"),
            status=cls._extract_select(properties, "Stav"),
            combat_history=cls._extract_rich_text(properties, "Průběh soubojů"),
            weaknesses_strengths=cls._extract_rich_text(properties, "Slabiny a silné stránky"),
            loot_ids=cls._extract_relation(properties, "Kořist"),
            tags=cls._extract_multi_select(properties, "Tagy"),
            notion_page_id=page.get("id"),
            created_at=datetime.fromisoformat(page.get("created_time")) if page.get("created_time") else None,
            updated_at=datetime.fromisoformat(page.get("last_edited_time")) if page.get("last_edited_time") else None,
        )

    @classmethod
    def notion_to_item(cls, page: Dict[str, Any]) -> Item:
        """
        Konvertuje Notion stránku na předmět.

        Args:
            page: Notion stránka.

        Returns:
            Item objekt.
        """
        properties = page.get("properties", {})
        
        return Item(
            id=page.get("id"),
            name=cls._extract_title(properties, "Název"),
            item_type=cls._extract_select(properties, "Typ"),
            description=cls._extract_rich_text(properties, "Popis a vlastnosti"),
            location_id=cls._extract_relation(properties, "Místo nalezení")[0] if cls._extract_relation(properties, "Místo nalezení") else None,
            owner_id=cls._extract_relation(properties, "Současný vlastník")[0] if cls._extract_relation(properties, "Současný vlastník") else None,
            ownership_history=cls._extract_rich_text(properties, "Historie vlastnictví"),
            special_abilities=cls._extract_rich_text(properties, "Speciální schopnosti"),
            tags=cls._extract_multi_select(properties, "Tagy"),
            notion_page_id=page.get("id"),
            created_at=datetime.fromisoformat(page.get("created_time")) if page.get("created_time") else None,
            updated_at=datetime.fromisoformat(page.get("last_edited_time")) if page.get("last_edited_time") else None,
        )

    @classmethod
    def notion_to_quest(cls, page: Dict[str, Any]) -> Quest:
        """
        Konvertuje Notion stránku na quest.

        Args:
            page: Notion stránka.

        Returns:
            Quest objekt.
        """
        properties = page.get("properties", {})
        
        return Quest(
            id=page.get("id"),
            name=cls._extract_title(properties, "Název"),
            description=cls._extract_rich_text(properties, "Popis a cíle"),
            giver_id=cls._extract_relation(properties, "Zadavatel")[0] if cls._extract_relation(properties, "Zadavatel") else None,
            status=cls._extract_select(properties, "Stav"),
            rewards=cls._extract_rich_text(properties, "Odměny"),
            location_ids=cls._extract_relation(properties, "Související lokace"),
            npc_ids=cls._extract_relation(properties, "Související NPC"),
            timeline=cls._extract_rich_text(properties, "Časová linie"),
            tags=cls._extract_multi_select(properties, "Tagy"),
            notion_page_id=page.get("id"),
            created_at=datetime.fromisoformat(page.get("created_time")) if page.get("created_time") else None,
            updated_at=datetime.fromisoformat(page.get("last_edited_time")) if page.get("last_edited_time") else None,
        )

    @classmethod
    def notion_to_faction(cls, page: Dict[str, Any]) -> Faction:
        """
        Konvertuje Notion stránku na frakci.

        Args:
            page: Notion stránka.

        Returns:
            Faction objekt.
        """
        properties = page.get("properties", {})
        
        return Faction(
            id=page.get("id"),
            name=cls._extract_title(properties, "Název"),
            description=cls._extract_rich_text(properties, "Popis a cíle"),
            member_ids=cls._extract_relation(properties, "Členové"),
            territory_ids=cls._extract_relation(properties, "Území"),
            faction_relations=cls._extract_rich_text(properties, "Vztahy s jinými frakcemi"),
            player_relation=cls._extract_number(properties, "Vztah k hráči"),
            event_ids=cls._extract_relation(properties, "Významné události"),
            tags=cls._extract_multi_select(properties, "Tagy"),
            notion_page_id=page.get("id"),
            created_at=datetime.fromisoformat(page.get("created_time")) if page.get("created_time") else None,
            updated_at=datetime.fromisoformat(page.get("last_edited_time")) if page.get("last_edited_time") else None,
        )

    @classmethod
    def notion_to_event(cls, page: Dict[str, Any]) -> Event:
        """
        Konvertuje Notion stránku na událost.

        Args:
            page: Notion stránka.

        Returns:
            Event objekt.
        """
        properties = page.get("properties", {})
        
        return Event(
            id=page.get("id"),
            name=cls._extract_title(properties, "Název"),
            date=cls._extract_date(properties, "Datum a čas"),
            description=cls._extract_rich_text(properties, "Popis"),
            location_id=cls._extract_relation(properties, "Místo")[0] if cls._extract_relation(properties, "Místo") else None,
            npc_ids=cls._extract_relation(properties, "Zúčastněné postavy"),
            consequences=cls._extract_rich_text(properties, "Důsledky"),
            tags=cls._extract_multi_select(properties, "Tagy"),
            notion_page_id=page.get("id"),
            created_at=datetime.fromisoformat(page.get("created_time")) if page.get("created_time") else None,
            updated_at=datetime.fromisoformat(page.get("last_edited_time")) if page.get("last_edited_time") else None,
        )

    @classmethod
    def notion_to_adventure_journal_entry(cls, page: Dict[str, Any]) -> AdventureJournalEntry:
        """
        Konvertuje Notion stránku na záznam v deníku dobrodružství.

        Args:
            page: Notion stránka.

        Returns:
            AdventureJournalEntry objekt.
        """
        properties = page.get("properties", {})
        
        return AdventureJournalEntry(
            id=page.get("id"),
            name=cls._extract_title(properties, "Název epizody"),
            date=cls._extract_date(properties, "Datum a čas"),
            summary=cls._extract_rich_text(properties, "Shrnutí příběhu"),
            event_ids=cls._extract_relation(properties, "Klíčové události"),
            npc_ids=cls._extract_relation(properties, "Zúčastněné postavy"),
            location_ids=cls._extract_relation(properties, "Navštívené lokace"),
            notion_page_id=page.get("id"),
            created_at=datetime.fromisoformat(page.get("created_time")) if page.get("created_time") else None,
            updated_at=datetime.fromisoformat(page.get("last_edited_time")) if page.get("last_edited_time") else None,
        )

    @classmethod
    def notion_to_entity(cls, page: Dict[str, Any], entity_type: EntityType) -> BaseEntity:
        """
        Konvertuje Notion stránku na entitu podle typu.

        Args:
            page: Notion stránka.
            entity_type: Typ entity.

        Returns:
            Entita odpovídajícího typu.

        Raises:
            ValueError: Pokud je zadán neplatný typ entity.
        """
        if entity_type == EntityType.NPC:
            return cls.notion_to_npc(page)
        elif entity_type == EntityType.LOCATION:
            return cls.notion_to_location(page)
        elif entity_type == EntityType.MONSTER:
            return cls.notion_to_monster(page)
        elif entity_type == EntityType.ITEM:
            return cls.notion_to_item(page)
        elif entity_type == EntityType.QUEST:
            return cls.notion_to_quest(page)
        elif entity_type == EntityType.FACTION:
            return cls.notion_to_faction(page)
        elif entity_type == EntityType.EVENT:
            return cls.notion_to_event(page)
        elif entity_type == EntityType.ADVENTURE_JOURNAL:
            return cls.notion_to_adventure_journal_entry(page)
        else:
            raise ValueError(f"Neplatný typ entity: {entity_type}")
