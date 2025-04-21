#!/usr/bin/env python
"""
Skript pro testování připojení k Notion API.
"""
import argparse
import logging
import sys
from pathlib import Path

# Přidání nadřazeného adresáře do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv

from rpg_notion.api.notion_client import NotionClientWrapper
from rpg_notion.config.settings import NOTION_API_KEY

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def parse_args():
    """
    Parsování argumentů příkazové řádky.
    """
    parser = argparse.ArgumentParser(description="Test připojení k Notion API.")
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Cesta k souboru .env s konfigurací.",
    )
    return parser.parse_args()


def main():
    """
    Hlavní funkce skriptu.
    """
    args = parse_args()

    # Načtení proměnných prostředí
    load_dotenv(args.env_file)

    # Kontrola, zda je nastaven API klíč
    if not NOTION_API_KEY:
        logger.error("Notion API klíč není nastaven. Nastavte proměnnou prostředí NOTION_API_KEY.")
        sys.exit(1)

    try:
        # Inicializace klienta
        notion_client = NotionClientWrapper()
        
        # Test připojení - vyhledání stránek
        logger.info("Testuji připojení k Notion API...")
        results = notion_client.search(query="", filter={"value": "page", "property": "object"})
        
        # Výpis výsledků
        logger.info(f"Připojení k Notion API je funkční. Nalezeno {len(results)} stránek.")
        
        # Výpis prvních 5 stránek
        if results:
            logger.info("První stránky:")
            for i, page in enumerate(results[:5], 1):
                title = ""
                if page.get("properties", {}).get("title", {}).get("title"):
                    title = "".join(item.get("plain_text", "") for item in page["properties"]["title"]["title"])
                logger.info(f"  {i}. {title} (ID: {page.get('id')})")
        
    except Exception as e:
        logger.error(f"Chyba při připojení k Notion API: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
