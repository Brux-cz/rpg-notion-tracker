import os
import requests
from dotenv import load_dotenv

# Načtení proměnných prostředí z .env souboru
load_dotenv()

# Získání API klíče z proměnných prostředí
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")

# Kontrola, zda je API klíč nastaven
if not NOTION_API_KEY:
    print("Chyba: NOTION_API_KEY není nastaven v souboru .env")
    exit(1)

# Nastavení hlaviček pro API požadavek
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# Testovací požadavek na Notion API
try:
    response = requests.get("https://api.notion.com/v1/users/me", headers=headers)
    
    # Kontrola odpovědi
    if response.status_code == 200:
        data = response.json()
        print(f"Připojení k Notion API je funkční!")
        print(f"Přihlášený uživatel: {data.get('name')}")
        print(f"ID uživatele: {data.get('id')}")
    else:
        print(f"Chyba při připojení k Notion API: {response.status_code}")
        print(response.json())
except Exception as e:
    print(f"Neočekávaná chyba: {e}")
