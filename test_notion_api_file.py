import urllib.request
import json
import sys

# Přesměrování výstupu do souboru
sys.stdout = open("notion_api_test_output.txt", "w", encoding="utf-8")

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
        data = json.loads(response_data)
        
        # Výpis statusu
        print(f"Status kód: {response.status}")
        
        # Kontrola odpovědi
        if response.status == 200:
            print("Připojení k Notion API je funkční!")
            print(f"Přihlášený uživatel: {data.get('name')}")
            print(f"ID uživatele: {data.get('id')}")
            print("\nKompletní odpověď:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Uložení odpovědi do souboru
            with open("notion_api_response_file.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("\nOdpověď uložena do souboru notion_api_response_file.json")
        else:
            print(f"Chyba při připojení k Notion API: {response.status}")
            print(response_data)
except urllib.error.HTTPError as e:
    print(f"HTTP chyba: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Neočekávaná chyba: {e}")

# Zavření přesměrovaného výstupu
sys.stdout.close()

# Obnovení standardního výstupu
sys.stdout = sys.__stdout__

print("Test dokončen. Výsledky byly uloženy do souboru notion_api_test_output.txt")
