"""
Konfigurace pro pytest.
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Načtení proměnných prostředí z .env souboru
load_dotenv()

# Nastavení testovacího prostředí
os.environ["TESTING"] = "True"
