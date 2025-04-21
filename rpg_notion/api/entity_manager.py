"""
Správce entit v Notion.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rpg_notion.api.notion_client import NotionClientWrapper
from rpg_notion.config.settings import NOTION_DATABASE_IDS

logger = logging.getLogger(__name__)


class NotionEntityManager:
    """
    Třída pro správu entit v Notion.
    """

    def __init__(self, notion_client: Optional[NotionClientWrapper] = None):
        """
        Inicializace správce entit.

        Args:
            notion_client: Instance NotionClientWrapper. Pokud není zadána, vytvoří se nová.
        """
        self.client = notion_client or NotionClientWrapper()
        self.database_ids = NOTION_DATABASE_IDS.copy()

    def _create_title_property(self, title: str) -> Dict[str, Any]:
        """
        Vytvoří vlastnost title pro Notion.

        Args:
            title: Název entity.

        Returns:
            Vlastnost title pro Notion.
        """
        return {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title,
                    },
                }
            ]
        }

    def _create_rich_text_property(self, text: str) -> Dict[str, Any]:
        """
        Vytvoří vlastnost rich_text pro Notion.

        Args:
            text: Text vlastnosti.

        Returns:
            Vlastnost rich_text pro Notion.
        """
        return {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": text,
                    },
                }
            ]
        }

    def _create_select_property(self, option: str) -> Dict[str, Any]:
        """
        Vytvoří vlastnost select pro Notion.

        Args:
            option: Vybraná možnost.

        Returns:
            Vlastnost select pro Notion.
        """
        return {
            "select": {
                "name": option,
            }
        }

    def _create_multi_select_property(self, options: List[str]) -> Dict[str, Any]:
        """
        Vytvoří vlastnost multi_select pro Notion.

        Args:
            options: Seznam vybraných možností.

        Returns:
            Vlastnost multi_select pro Notion.
        """
        return {
            "multi_select": [
                {
                    "name": option,
                }
                for option in options
            ]
        }

    def _create_relation_property(self, page_ids: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Vytvoří vlastnost relation pro Notion.

        Args:
            page_ids: ID stránky nebo seznam ID stránek.

        Returns:
            Vlastnost relation pro Notion.
        """
        if isinstance(page_ids, str):
            page_ids = [page_ids]

        return {
            "relation": [
                {
                    "id": page_id,
                }
                for page_id in page_ids
            ]
        }

    def _create_date_property(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Vytvoří vlastnost date pro Notion.

        Args:
            date: Datum a čas. Pokud není zadáno, použije se aktuální datum a čas.

        Returns:
            Vlastnost date pro Notion.
        """
        if date is None:
            date = datetime.now()

        return {
            "date": {
                "start": date.isoformat(),
            }
        }

    def _create_number_property(self, number: Union[int, float]) -> Dict[str, Any]:
        """
        Vytvoří vlastnost number pro Notion.

        Args:
            number: Číslo.

        Returns:
            Vlastnost number pro Notion.
        """
        return {
            "number": number
        }

    def find_entity_by_name(self, database_id: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Najde entitu v databázi podle názvu.

        Args:
            database_id: ID databáze.
            name: Název entity.

        Returns:
            Nalezená entita nebo None, pokud entita nebyla nalezena.
        """
        filter_params = {
            "property": "title",
            "title": {
                "equals": name,
            }
        }

        results = self.client.query_database(
            database_id=database_id,
            filter=filter_params,
        )

        if results:
            return results[0]
        return None

    def find_entity_by_property(
        self, database_id: str, property_name: str, property_value: Any, property_type: str = "rich_text"
    ) -> Optional[Dict[str, Any]]:
        """
        Najde entitu v databázi podle hodnoty vlastnosti.

        Args:
            database_id: ID databáze.
            property_name: Název vlastnosti.
            property_value: Hodnota vlastnosti.
            property_type: Typ vlastnosti (rich_text, select, multi_select, relation, date, number).

        Returns:
            Nalezená entita nebo None, pokud entita nebyla nalezena.
        """
        filter_params = {
            "property": property_name,
        }

        if property_type == "rich_text":
            filter_params["rich_text"] = {
                "equals": property_value,
            }
        elif property_type == "select":
            filter_params["select"] = {
                "equals": property_value,
            }
        elif property_type == "multi_select":
            filter_params["multi_select"] = {
                "contains": property_value,
            }
        elif property_type == "relation":
            filter_params["relation"] = {
                "contains": property_value,
            }
        elif property_type == "date":
            filter_params["date"] = {
                "equals": property_value.isoformat() if isinstance(property_value, datetime) else property_value,
            }
        elif property_type == "number":
            filter_params["number"] = {
                "equals": property_value,
            }
        else:
            raise ValueError(f"Nepodporovaný typ vlastnosti: {property_type}")

        results = self.client.query_database(
            database_id=database_id,
            filter=filter_params,
        )

        if results:
            return results[0]
        return None

    def create_npc(
        self,
        name: str,
        description: str,
        status: str = "Živý",
        occupation: str = "",
        location_id: Optional[str] = None,
        related_npc_ids: Optional[List[str]] = None,
        item_ids: Optional[List[str]] = None,
        history: str = "",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vytvoří novou NPC postavu v Notion.

        Args:
            name: Jméno NPC.
            description: Popis NPC.
            status: Stav NPC (Živý, Mrtvý, Zraněný, Neznámý).
            occupation: Povolání nebo role NPC.
            location_id: ID lokace, kde se NPC nachází.
            related_npc_ids: Seznam ID souvisejících NPC.
            item_ids: Seznam ID předmětů, které NPC vlastní.
            history: Historie změn NPC.
            tags: Seznam tagů pro NPC.

        Returns:
            Vytvořená NPC postava.
        """
        properties = {
            "Jméno": self._create_title_property(name),
            "Popis": self._create_rich_text_property(description),
            "Stav": self._create_select_property(status),
        }

        if occupation:
            properties["Povolání/role"] = self._create_rich_text_property(occupation)

        if location_id:
            properties["Lokace"] = self._create_relation_property(location_id)

        if related_npc_ids:
            properties["Vztahy"] = self._create_relation_property(related_npc_ids)

        if item_ids:
            properties["Významné předměty"] = self._create_relation_property(item_ids)

        if history:
            properties["Historie změn"] = self._create_rich_text_property(history)

        if tags:
            properties["Tagy"] = self._create_multi_select_property(tags)

        return self.client.create_page(
            parent_id=self.database_ids["npcs"],
            properties=properties,
        )

    def create_location(
        self,
        name: str,
        location_type: str,
        hierarchy: str = "",
        description: str = "",
        npc_ids: Optional[List[str]] = None,
        item_ids: Optional[List[str]] = None,
        event_ids: Optional[List[str]] = None,
        status: str = "Bezpečné",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vytvoří novou lokaci v Notion.

        Args:
            name: Název lokace.
            location_type: Typ lokace (Město, Vesnice, Dungeon, Les, ...).
            hierarchy: Hierarchická kategorizace lokace.
            description: Popis prostředí lokace.
            npc_ids: Seznam ID NPC, které obývají lokaci.
            item_ids: Seznam ID předmětů, které se nacházejí v lokaci.
            event_ids: Seznam ID událostí, které se odehrály v lokaci.
            status: Stav lokace (Prosperující, V úpadku, Zničené, ...).
            tags: Seznam tagů pro lokaci.

        Returns:
            Vytvořená lokace.
        """
        properties = {
            "Název": self._create_title_property(name),
            "Typ": self._create_select_property(location_type),
            "Stav": self._create_select_property(status),
        }

        if hierarchy:
            properties["Hierarchie"] = self._create_rich_text_property(hierarchy)

        if description:
            properties["Popis prostředí"] = self._create_rich_text_property(description)

        if npc_ids:
            properties["Obyvatelé"] = self._create_relation_property(npc_ids)

        if item_ids:
            properties["Významné objekty"] = self._create_relation_property(item_ids)

        if event_ids:
            properties["Události"] = self._create_relation_property(event_ids)

        if tags:
            properties["Tagy"] = self._create_multi_select_property(tags)

        return self.client.create_page(
            parent_id=self.database_ids["locations"],
            properties=properties,
        )

    def create_monster(
        self,
        name: str,
        description: str = "",
        location_ids: Optional[List[str]] = None,
        status: str = "Živá",
        combat_history: str = "",
        weaknesses_strengths: str = "",
        loot_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vytvoří novou příšeru v Notion.

        Args:
            name: Název/typ příšery.
            description: Popis a schopnosti příšery.
            location_ids: Seznam ID lokací, kde se příšera vyskytuje.
            status: Stav příšery (Živá, Mrtvá, Zraněná, Neznámý).
            combat_history: Průběh soubojů s příšerou.
            weaknesses_strengths: Slabiny a silné stránky příšery.
            loot_ids: Seznam ID předmětů, které příšera může dropnout.
            tags: Seznam tagů pro příšeru.

        Returns:
            Vytvořená příšera.
        """
        properties = {
            "Název/typ": self._create_title_property(name),
            "Stav": self._create_select_property(status),
        }

        if description:
            properties["Popis a schopnosti"] = self._create_rich_text_property(description)

        if location_ids:
            properties["Místo výskytu"] = self._create_relation_property(location_ids)

        if combat_history:
            properties["Průběh soubojů"] = self._create_rich_text_property(combat_history)

        if weaknesses_strengths:
            properties["Slabiny a silné stránky"] = self._create_rich_text_property(weaknesses_strengths)

        if loot_ids:
            properties["Kořist"] = self._create_relation_property(loot_ids)

        if tags:
            properties["Tagy"] = self._create_multi_select_property(tags)

        return self.client.create_page(
            parent_id=self.database_ids["monsters"],
            properties=properties,
        )

    def create_item(
        self,
        name: str,
        item_type: str,
        description: str = "",
        location_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        ownership_history: str = "",
        special_abilities: str = "",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vytvoří nový předmět v Notion.

        Args:
            name: Název předmětu.
            item_type: Typ předmětu (Zbraň, Brnění, Artefakt, ...).
            description: Popis a vlastnosti předmětu.
            location_id: ID lokace, kde byl předmět nalezen.
            owner_id: ID současného vlastníka předmětu.
            ownership_history: Historie vlastnictví předmětu.
            special_abilities: Speciální schopnosti předmětu.
            tags: Seznam tagů pro předmět.

        Returns:
            Vytvořený předmět.
        """
        properties = {
            "Název": self._create_title_property(name),
            "Typ": self._create_select_property(item_type),
        }

        if description:
            properties["Popis a vlastnosti"] = self._create_rich_text_property(description)

        if location_id:
            properties["Místo nalezení"] = self._create_relation_property(location_id)

        if owner_id:
            properties["Současný vlastník"] = self._create_relation_property(owner_id)

        if ownership_history:
            properties["Historie vlastnictví"] = self._create_rich_text_property(ownership_history)

        if special_abilities:
            properties["Speciální schopnosti"] = self._create_rich_text_property(special_abilities)

        if tags:
            properties["Tagy"] = self._create_multi_select_property(tags)

        return self.client.create_page(
            parent_id=self.database_ids["items"],
            properties=properties,
        )

    def create_quest(
        self,
        name: str,
        description: str = "",
        giver_id: Optional[str] = None,
        status: str = "Aktivní",
        rewards: str = "",
        location_ids: Optional[List[str]] = None,
        npc_ids: Optional[List[str]] = None,
        timeline: str = "",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vytvoří nový quest v Notion.

        Args:
            name: Název questu.
            description: Popis a cíle questu.
            giver_id: ID zadavatele questu.
            status: Stav questu (Aktivní, Dokončený, Selhaný, Pozastavený).
            rewards: Odměny za dokončení questu.
            location_ids: Seznam ID lokací souvisejících s questem.
            npc_ids: Seznam ID NPC souvisejících s questem.
            timeline: Časová linie questu.
            tags: Seznam tagů pro quest.

        Returns:
            Vytvořený quest.
        """
        properties = {
            "Název": self._create_title_property(name),
            "Stav": self._create_select_property(status),
        }

        if description:
            properties["Popis a cíle"] = self._create_rich_text_property(description)

        if giver_id:
            properties["Zadavatel"] = self._create_relation_property(giver_id)

        if rewards:
            properties["Odměny"] = self._create_rich_text_property(rewards)

        if location_ids:
            properties["Související lokace"] = self._create_relation_property(location_ids)

        if npc_ids:
            properties["Související NPC"] = self._create_relation_property(npc_ids)

        if timeline:
            properties["Časová linie"] = self._create_rich_text_property(timeline)

        if tags:
            properties["Tagy"] = self._create_multi_select_property(tags)

        return self.client.create_page(
            parent_id=self.database_ids["quests"],
            properties=properties,
        )

    def create_faction(
        self,
        name: str,
        description: str = "",
        member_ids: Optional[List[str]] = None,
        territory_ids: Optional[List[str]] = None,
        faction_relations: str = "",
        player_relation: int = 0,
        event_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vytvoří novou frakci v Notion.

        Args:
            name: Název frakce.
            description: Popis a cíle frakce.
            member_ids: Seznam ID členů frakce.
            territory_ids: Seznam ID území frakce.
            faction_relations: Vztahy s jinými frakcemi.
            player_relation: Vztah k hráči (číselné skóre).
            event_ids: Seznam ID významných událostí frakce.
            tags: Seznam tagů pro frakci.

        Returns:
            Vytvořená frakce.
        """
        properties = {
            "Název": self._create_title_property(name),
            "Vztah k hráči": self._create_number_property(player_relation),
        }

        if description:
            properties["Popis a cíle"] = self._create_rich_text_property(description)

        if member_ids:
            properties["Členové"] = self._create_relation_property(member_ids)

        if territory_ids:
            properties["Území"] = self._create_relation_property(territory_ids)

        if faction_relations:
            properties["Vztahy s jinými frakcemi"] = self._create_rich_text_property(faction_relations)

        if event_ids:
            properties["Významné události"] = self._create_relation_property(event_ids)

        if tags:
            properties["Tagy"] = self._create_multi_select_property(tags)

        return self.client.create_page(
            parent_id=self.database_ids["factions"],
            properties=properties,
        )

    def create_event(
        self,
        name: str,
        date: Optional[datetime] = None,
        description: str = "",
        location_id: Optional[str] = None,
        npc_ids: Optional[List[str]] = None,
        consequences: str = "",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vytvoří novou událost v Notion.

        Args:
            name: Název události.
            date: Datum a čas události.
            description: Popis události.
            location_id: ID místa události.
            npc_ids: Seznam ID zúčastněných postav.
            consequences: Důsledky události.
            tags: Seznam tagů pro událost.

        Returns:
            Vytvořená událost.
        """
        properties = {
            "Název": self._create_title_property(name),
            "Datum a čas": self._create_date_property(date),
        }

        if description:
            properties["Popis"] = self._create_rich_text_property(description)

        if location_id:
            properties["Místo"] = self._create_relation_property(location_id)

        if npc_ids:
            properties["Zúčastněné postavy"] = self._create_relation_property(npc_ids)

        if consequences:
            properties["Důsledky"] = self._create_rich_text_property(consequences)

        if tags:
            properties["Tagy"] = self._create_multi_select_property(tags)

        return self.client.create_page(
            parent_id=self.database_ids["events"],
            properties=properties,
        )

    def create_adventure_journal_entry(
        self,
        title: str,
        date: Optional[datetime] = None,
        summary: str = "",
        event_ids: Optional[List[str]] = None,
        npc_ids: Optional[List[str]] = None,
        location_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Vytvoří nový záznam v deníku dobrodružství v Notion.

        Args:
            title: Název epizody.
            date: Datum a čas herní session.
            summary: Shrnutí příběhu.
            event_ids: Seznam ID klíčových událostí.
            npc_ids: Seznam ID zúčastněných postav.
            location_ids: Seznam ID navštívených lokací.

        Returns:
            Vytvořený záznam v deníku dobrodružství.
        """
        properties = {
            "Název epizody": self._create_title_property(title),
            "Datum a čas": self._create_date_property(date),
        }

        if summary:
            properties["Shrnutí příběhu"] = self._create_rich_text_property(summary)

        if event_ids:
            properties["Klíčové události"] = self._create_relation_property(event_ids)

        if npc_ids:
            properties["Zúčastněné postavy"] = self._create_relation_property(npc_ids)

        if location_ids:
            properties["Navštívené lokace"] = self._create_relation_property(location_ids)

        return self.client.create_page(
            parent_id=self.database_ids["adventure_journal"],
            properties=properties,
        )

    def update_entity(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktualizuje entitu v Notion.

        Args:
            page_id: ID stránky entity.
            properties: Nové vlastnosti entity.

        Returns:
            Aktualizovaná entita.
        """
        return self.client.update_page(
            page_id=page_id,
            properties=properties,
        )

    def update_entity_history(self, page_id: str, history_property: str, new_entry: str) -> Dict[str, Any]:
        """
        Aktualizuje historii entity v Notion.

        Args:
            page_id: ID stránky entity.
            history_property: Název vlastnosti historie.
            new_entry: Nový záznam historie.

        Returns:
            Aktualizovaná entita.
        """
        # Nejprve získáme aktuální stránku
        page = self.client.get_page(page_id)
        
        # Získáme aktuální historii
        current_history = ""
        if page.get("properties", {}).get(history_property, {}).get("rich_text"):
            for text_item in page["properties"][history_property]["rich_text"]:
                if text_item.get("type") == "text":
                    current_history += text_item.get("text", {}).get("content", "")
        
        # Přidáme nový záznam s časovým razítkem
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_history = f"{current_history}\n\n[{timestamp}] {new_entry}" if current_history else f"[{timestamp}] {new_entry}"
        
        # Aktualizujeme stránku
        properties = {
            history_property: self._create_rich_text_property(updated_history)
        }
        
        return self.client.update_page(
            page_id=page_id,
            properties=properties,
        )
