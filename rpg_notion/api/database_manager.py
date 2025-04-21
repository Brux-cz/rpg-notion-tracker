"""
Správce databází v Notion.
"""
import logging
from typing import Any, Dict, List, Optional

from rpg_notion.api.notion_client import NotionClientWrapper
from rpg_notion.config.settings import NOTION_DATABASE_IDS

logger = logging.getLogger(__name__)


class NotionDatabaseManager:
    """
    Třída pro správu databází v Notion.
    """

    def __init__(self, notion_client: Optional[NotionClientWrapper] = None):
        """
        Inicializace správce databází.

        Args:
            notion_client: Instance NotionClientWrapper. Pokud není zadána, vytvoří se nová.
        """
        self.client = notion_client or NotionClientWrapper()
        self.database_ids = NOTION_DATABASE_IDS.copy()

    def create_adventure_journal_db(self, parent_page_id: str) -> str:
        """
        Vytvoří databázi Deník dobrodružství v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            ID vytvořené databáze.
        """
        properties = {
            "Datum a čas": {
                "date": {}
            },
            "Název epizody": {
                "title": {}
            },
            "Shrnutí příběhu": {
                "rich_text": {}
            },
            "Klíčové události": {
                "relation": {
                    "database_id": self.database_ids.get("events", ""),
                    "single_property": False,
                }
            },
            "Zúčastněné postavy": {
                "relation": {
                    "database_id": self.database_ids.get("npcs", ""),
                    "single_property": False,
                }
            },
            "Navštívené lokace": {
                "relation": {
                    "database_id": self.database_ids.get("locations", ""),
                    "single_property": False,
                }
            }
        }

        response = self.client.create_database(
            parent_page_id=parent_page_id,
            title="Deník dobrodružství",
            properties=properties,
        )
        
        database_id = response["id"]
        self.database_ids["adventure_journal"] = database_id
        logger.info(f"Vytvořena databáze Deník dobrodružství s ID: {database_id}")
        return database_id

    def create_npcs_db(self, parent_page_id: str) -> str:
        """
        Vytvoří databázi NPC v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            ID vytvořené databáze.
        """
        properties = {
            "Jméno": {
                "title": {}
            },
            "Popis": {
                "rich_text": {}
            },
            "Stav": {
                "select": {
                    "options": [
                        {"name": "Živý", "color": "green"},
                        {"name": "Mrtvý", "color": "red"},
                        {"name": "Zraněný", "color": "orange"},
                        {"name": "Neznámý", "color": "gray"}
                    ]
                }
            },
            "Povolání/role": {
                "rich_text": {}
            },
            "Lokace": {
                "relation": {
                    "database_id": self.database_ids.get("locations", ""),
                    "single_property": True,
                }
            },
            "Vztahy": {
                "relation": {
                    "database_id": self.database_ids.get("npcs", ""),
                    "single_property": False,
                }
            },
            "Významné předměty": {
                "relation": {
                    "database_id": self.database_ids.get("items", ""),
                    "single_property": False,
                }
            },
            "Historie změn": {
                "rich_text": {}
            },
            "Tagy": {
                "multi_select": {
                    "options": [
                        {"name": "Spojenec", "color": "green"},
                        {"name": "Nepřítel", "color": "red"},
                        {"name": "Obchodník", "color": "blue"},
                        {"name": "Zadavatel questů", "color": "yellow"},
                        {"name": "Důležitý", "color": "purple"}
                    ]
                }
            }
        }

        response = self.client.create_database(
            parent_page_id=parent_page_id,
            title="NPC",
            properties=properties,
        )
        
        database_id = response["id"]
        self.database_ids["npcs"] = database_id
        logger.info(f"Vytvořena databáze NPC s ID: {database_id}")
        return database_id

    def create_locations_db(self, parent_page_id: str) -> str:
        """
        Vytvoří databázi Lokace v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            ID vytvořené databáze.
        """
        properties = {
            "Název": {
                "title": {}
            },
            "Typ": {
                "select": {
                    "options": [
                        {"name": "Město", "color": "blue"},
                        {"name": "Vesnice", "color": "green"},
                        {"name": "Dungeon", "color": "red"},
                        {"name": "Les", "color": "green"},
                        {"name": "Hora", "color": "brown"},
                        {"name": "Jeskyně", "color": "gray"},
                        {"name": "Hrad", "color": "purple"},
                        {"name": "Chrám", "color": "yellow"},
                        {"name": "Ruiny", "color": "orange"}
                    ]
                }
            },
            "Hierarchie": {
                "rich_text": {}
            },
            "Popis prostředí": {
                "rich_text": {}
            },
            "Obyvatelé": {
                "relation": {
                    "database_id": self.database_ids.get("npcs", ""),
                    "single_property": False,
                }
            },
            "Významné objekty": {
                "relation": {
                    "database_id": self.database_ids.get("items", ""),
                    "single_property": False,
                }
            },
            "Události": {
                "relation": {
                    "database_id": self.database_ids.get("events", ""),
                    "single_property": False,
                }
            },
            "Stav": {
                "select": {
                    "options": [
                        {"name": "Prosperující", "color": "green"},
                        {"name": "V úpadku", "color": "orange"},
                        {"name": "Zničené", "color": "red"},
                        {"name": "Opuštěné", "color": "gray"},
                        {"name": "Nebezpečné", "color": "red"},
                        {"name": "Bezpečné", "color": "green"}
                    ]
                }
            },
            "Tagy": {
                "multi_select": {
                    "options": [
                        {"name": "Obydlené", "color": "blue"},
                        {"name": "Nebezpečné", "color": "red"},
                        {"name": "Prozkoumané", "color": "green"},
                        {"name": "Neprozkoumané", "color": "gray"},
                        {"name": "Důležité", "color": "purple"}
                    ]
                }
            }
        }

        response = self.client.create_database(
            parent_page_id=parent_page_id,
            title="Lokace",
            properties=properties,
        )
        
        database_id = response["id"]
        self.database_ids["locations"] = database_id
        logger.info(f"Vytvořena databáze Lokace s ID: {database_id}")
        return database_id

    def create_monsters_db(self, parent_page_id: str) -> str:
        """
        Vytvoří databázi Příšery v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            ID vytvořené databáze.
        """
        properties = {
            "Název/typ": {
                "title": {}
            },
            "Popis a schopnosti": {
                "rich_text": {}
            },
            "Místo výskytu": {
                "relation": {
                    "database_id": self.database_ids.get("locations", ""),
                    "single_property": False,
                }
            },
            "Stav": {
                "select": {
                    "options": [
                        {"name": "Živá", "color": "green"},
                        {"name": "Mrtvá", "color": "red"},
                        {"name": "Zraněná", "color": "orange"},
                        {"name": "Neznámý", "color": "gray"}
                    ]
                }
            },
            "Průběh soubojů": {
                "rich_text": {}
            },
            "Slabiny a silné stránky": {
                "rich_text": {}
            },
            "Kořist": {
                "relation": {
                    "database_id": self.database_ids.get("items", ""),
                    "single_property": False,
                }
            },
            "Tagy": {
                "multi_select": {
                    "options": [
                        {"name": "Boss", "color": "red"},
                        {"name": "Běžná", "color": "gray"},
                        {"name": "Unikátní", "color": "purple"},
                        {"name": "Inteligentní", "color": "blue"},
                        {"name": "Nemrtvá", "color": "black"}
                    ]
                }
            }
        }

        response = self.client.create_database(
            parent_page_id=parent_page_id,
            title="Příšery",
            properties=properties,
        )
        
        database_id = response["id"]
        self.database_ids["monsters"] = database_id
        logger.info(f"Vytvořena databáze Příšery s ID: {database_id}")
        return database_id

    def create_items_db(self, parent_page_id: str) -> str:
        """
        Vytvoří databázi Předměty v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            ID vytvořené databáze.
        """
        properties = {
            "Název": {
                "title": {}
            },
            "Typ": {
                "select": {
                    "options": [
                        {"name": "Zbraň", "color": "red"},
                        {"name": "Brnění", "color": "gray"},
                        {"name": "Artefakt", "color": "purple"},
                        {"name": "Lektvar", "color": "blue"},
                        {"name": "Svitek", "color": "yellow"},
                        {"name": "Běžný předmět", "color": "brown"},
                        {"name": "Klíč", "color": "orange"}
                    ]
                }
            },
            "Popis a vlastnosti": {
                "rich_text": {}
            },
            "Místo nalezení": {
                "relation": {
                    "database_id": self.database_ids.get("locations", ""),
                    "single_property": True,
                }
            },
            "Současný vlastník": {
                "relation": {
                    "database_id": self.database_ids.get("npcs", ""),
                    "single_property": True,
                }
            },
            "Historie vlastnictví": {
                "rich_text": {}
            },
            "Speciální schopnosti": {
                "rich_text": {}
            },
            "Tagy": {
                "multi_select": {
                    "options": [
                        {"name": "Běžný", "color": "gray"},
                        {"name": "Vzácný", "color": "blue"},
                        {"name": "Epický", "color": "purple"},
                        {"name": "Legendární", "color": "yellow"},
                        {"name": "Prokletý", "color": "red"},
                        {"name": "Questový", "color": "orange"}
                    ]
                }
            }
        }

        response = self.client.create_database(
            parent_page_id=parent_page_id,
            title="Předměty",
            properties=properties,
        )
        
        database_id = response["id"]
        self.database_ids["items"] = database_id
        logger.info(f"Vytvořena databáze Předměty s ID: {database_id}")
        return database_id

    def create_quests_db(self, parent_page_id: str) -> str:
        """
        Vytvoří databázi Questy v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            ID vytvořené databáze.
        """
        properties = {
            "Název": {
                "title": {}
            },
            "Popis a cíle": {
                "rich_text": {}
            },
            "Zadavatel": {
                "relation": {
                    "database_id": self.database_ids.get("npcs", ""),
                    "single_property": True,
                }
            },
            "Stav": {
                "select": {
                    "options": [
                        {"name": "Aktivní", "color": "blue"},
                        {"name": "Dokončený", "color": "green"},
                        {"name": "Selhaný", "color": "red"},
                        {"name": "Pozastavený", "color": "orange"}
                    ]
                }
            },
            "Odměny": {
                "rich_text": {}
            },
            "Související lokace": {
                "relation": {
                    "database_id": self.database_ids.get("locations", ""),
                    "single_property": False,
                }
            },
            "Související NPC": {
                "relation": {
                    "database_id": self.database_ids.get("npcs", ""),
                    "single_property": False,
                }
            },
            "Časová linie": {
                "rich_text": {}
            },
            "Tagy": {
                "multi_select": {
                    "options": [
                        {"name": "Hlavní", "color": "red"},
                        {"name": "Vedlejší", "color": "blue"},
                        {"name": "Frakční", "color": "purple"},
                        {"name": "Časově omezený", "color": "orange"},
                        {"name": "Průzkumný", "color": "green"}
                    ]
                }
            }
        }

        response = self.client.create_database(
            parent_page_id=parent_page_id,
            title="Questy",
            properties=properties,
        )
        
        database_id = response["id"]
        self.database_ids["quests"] = database_id
        logger.info(f"Vytvořena databáze Questy s ID: {database_id}")
        return database_id

    def create_factions_db(self, parent_page_id: str) -> str:
        """
        Vytvoří databázi Frakce v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            ID vytvořené databáze.
        """
        properties = {
            "Název": {
                "title": {}
            },
            "Popis a cíle": {
                "rich_text": {}
            },
            "Členové": {
                "relation": {
                    "database_id": self.database_ids.get("npcs", ""),
                    "single_property": False,
                }
            },
            "Území": {
                "relation": {
                    "database_id": self.database_ids.get("locations", ""),
                    "single_property": False,
                }
            },
            "Vztahy s jinými frakcemi": {
                "rich_text": {}
            },
            "Vztah k hráči": {
                "number": {
                    "format": "number"
                }
            },
            "Významné události": {
                "relation": {
                    "database_id": self.database_ids.get("events", ""),
                    "single_property": False,
                }
            },
            "Tagy": {
                "multi_select": {
                    "options": [
                        {"name": "Přátelská", "color": "green"},
                        {"name": "Nepřátelská", "color": "red"},
                        {"name": "Neutrální", "color": "gray"},
                        {"name": "Obchodní", "color": "blue"},
                        {"name": "Vojenská", "color": "orange"},
                        {"name": "Náboženská", "color": "purple"}
                    ]
                }
            }
        }

        response = self.client.create_database(
            parent_page_id=parent_page_id,
            title="Frakce",
            properties=properties,
        )
        
        database_id = response["id"]
        self.database_ids["factions"] = database_id
        logger.info(f"Vytvořena databáze Frakce s ID: {database_id}")
        return database_id

    def create_events_db(self, parent_page_id: str) -> str:
        """
        Vytvoří databázi Události v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            ID vytvořené databáze.
        """
        properties = {
            "Název": {
                "title": {}
            },
            "Datum a čas": {
                "date": {}
            },
            "Popis": {
                "rich_text": {}
            },
            "Místo": {
                "relation": {
                    "database_id": self.database_ids.get("locations", ""),
                    "single_property": True,
                }
            },
            "Zúčastněné postavy": {
                "relation": {
                    "database_id": self.database_ids.get("npcs", ""),
                    "single_property": False,
                }
            },
            "Důsledky": {
                "rich_text": {}
            },
            "Tagy": {
                "multi_select": {
                    "options": [
                        {"name": "Souboj", "color": "red"},
                        {"name": "Dialog", "color": "blue"},
                        {"name": "Objev", "color": "green"},
                        {"name": "Quest", "color": "yellow"},
                        {"name": "Důležitá", "color": "purple"},
                        {"name": "Vedlejší", "color": "gray"}
                    ]
                }
            }
        }

        response = self.client.create_database(
            parent_page_id=parent_page_id,
            title="Události",
            properties=properties,
        )
        
        database_id = response["id"]
        self.database_ids["events"] = database_id
        logger.info(f"Vytvořena databáze Události s ID: {database_id}")
        return database_id

    def create_all_databases(self, parent_page_id: str) -> Dict[str, str]:
        """
        Vytvoří všechny databáze v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.

        Returns:
            Slovník s ID všech vytvořených databází.
        """
        # Nejprve vytvoříme databáze, které nemají závislosti
        self.create_events_db(parent_page_id)
        self.create_npcs_db(parent_page_id)
        self.create_locations_db(parent_page_id)
        self.create_items_db(parent_page_id)
        
        # Poté vytvoříme databáze, které mají závislosti
        self.create_monsters_db(parent_page_id)
        self.create_quests_db(parent_page_id)
        self.create_factions_db(parent_page_id)
        self.create_adventure_journal_db(parent_page_id)
        
        # Aktualizujeme relace v databázích, které byly vytvořeny před jejich závislostmi
        self._update_database_relations()
        
        return self.database_ids

    def _update_database_relations(self) -> None:
        """
        Aktualizuje relace v databázích, které byly vytvořeny před jejich závislostmi.
        """
        # Aktualizace relací v databázi NPC
        if self.database_ids.get("npcs") and self.database_ids.get("locations"):
            properties = {
                "Lokace": {
                    "relation": {
                        "database_id": self.database_ids["locations"],
                        "single_property": True,
                    }
                }
            }
            self.client.update_database(
                database_id=self.database_ids["npcs"],
                properties=properties,
            )
            logger.info("Aktualizovány relace v databázi NPC")
        
        # Aktualizace relací v databázi Události
        if self.database_ids.get("events") and self.database_ids.get("locations"):
            properties = {
                "Místo": {
                    "relation": {
                        "database_id": self.database_ids["locations"],
                        "single_property": True,
                    }
                }
            }
            self.client.update_database(
                database_id=self.database_ids["events"],
                properties=properties,
            )
            logger.info("Aktualizovány relace v databázi Události")
