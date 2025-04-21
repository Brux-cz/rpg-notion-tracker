import urllib.request
import json

# API klíč
api_key = "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"

# Nastavení hlaviček pro API požadavek
headers = {
    "Authorization": f"Bearer {api_key}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

print("Testuji připojení k Notion API...")
try:
    # Vytvoření požadavku
    req = urllib.request.Request("https://api.notion.com/v1/users/me", headers=headers)
    
    # Odeslání požadavku
    with urllib.request.urlopen(req) as response:
        # Čtení odpovědi
        response_data = response.read().decode('utf-8')
        print(response_data)
except Exception as e:
    print(f"Neočekávaná chyba: {e}")

input("Stiskněte Enter pro ukončení...")
