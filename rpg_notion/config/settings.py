"""
Konfigurační nastavení aplikace.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Načtení proměnných prostředí z .env souboru
load_dotenv()

# Základní cesty
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"

# Notion API konfigurace
NOTION_API_KEY: Optional[str] = os.getenv("NOTION_API_KEY")
NOTION_VERSION: str = os.getenv("NOTION_VERSION", "2022-06-28")

# Konfigurace pro rate limiting
NOTION_RATE_LIMIT_DELAY: float = float(os.getenv("NOTION_RATE_LIMIT_DELAY", "0.5"))
NOTION_MAX_RETRIES: int = int(os.getenv("NOTION_MAX_RETRIES", "3"))

# ID databází v Notion (budou nastaveny později při vytváření)
NOTION_DATABASE_IDS = {
    "adventure_journal": os.getenv("NOTION_DB_ADVENTURE_JOURNAL"),
    "npcs": os.getenv("NOTION_DB_NPCS"),
    "locations": os.getenv("NOTION_DB_LOCATIONS"),
    "monsters": os.getenv("NOTION_DB_MONSTERS"),
    "items": os.getenv("NOTION_DB_ITEMS"),
    "quests": os.getenv("NOTION_DB_QUESTS"),
    "factions": os.getenv("NOTION_DB_FACTIONS"),
    "events": os.getenv("NOTION_DB_EVENTS"),
}

# NLP konfigurace
NLP_MODELS_DIR = DATA_DIR / "models"
SPACY_MODEL = os.getenv("SPACY_MODEL", "cs_core_news_lg")
