#!/usr/bin/env python
"""
Skript pro inicializaci databází v Notion.
"""
import argparse
import logging
import os
import sys
from pathlib import Path

# Přidání nadřazeného adresáře do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv

from rpg_notion.api.database_manager import NotionDatabaseManager
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
    parser = argparse.ArgumentParser(description="Inicializace databází v Notion.")
    parser.add_argument(
        "--parent-page-id",
        type=str,
        required=True,
        help="ID rodičovské stránky v Notion, kde budou vytvořeny databáze.",
    )
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
        
        # Inicializace správce databází
        db_manager = NotionDatabaseManager(notion_client)
        
        # Vytvoření všech databází
        logger.info(f"Vytvářím databáze v rodičovské stránce {args.parent_page_id}...")
        database_ids = db_manager.create_all_databases(args.parent_page_id)
        
        # Výpis ID databází
        logger.info("Databáze byly úspěšně vytvořeny:")
        for name, db_id in database_ids.items():
            logger.info(f"  {name}: {db_id}")
        
        # Uložení ID databází do .env souboru
        env_path = Path(args.env_file)
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                env_content = f.read()
            
            # Aktualizace ID databází v .env souboru
            for name, db_id in database_ids.items():
                env_var_name = f"NOTION_DB_{name.upper()}"
                if db_id:
                    if f"{env_var_name}=" in env_content:
                        env_content = env_content.replace(
                            f"{env_var_name}=", f"{env_var_name}={db_id}"
                        )
                    else:
                        env_content += f"\n{env_var_name}={db_id}"
            
            # Zápis aktualizovaného obsahu do .env souboru
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(env_content)
            
            logger.info(f"ID databází byla uložena do souboru {args.env_file}")
        
    except Exception as e:
        logger.error(f"Chyba při inicializaci databází: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
