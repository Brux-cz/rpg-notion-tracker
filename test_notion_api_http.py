import http.client
import json
import ssl

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
    # Vytvoření SSL kontextu
    context = ssl.create_default_context()
    
    # Vytvoření připojení
    conn = http.client.HTTPSConnection("api.notion.com", context=context)
    
    # Odeslání požadavku
    conn.request("GET", "/v1/users/me", headers=headers)
    
    # Získání odpovědi
    response = conn.getresponse()
    
    # Čtení odpovědi
    response_data = response.read().decode('utf-8')
    
    # Výpis statusu
    print(f"Status kód: {response.status}")
    
    # Kontrola odpovědi
    if response.status == 200:
        data = json.loads(response_data)
        print("Připojení k Notion API je funkční!")
        print(f"Přihlášený uživatel: {data.get('name')}")
        print(f"ID uživatele: {data.get('id')}")
        print("\nKompletní odpověď:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Uložení odpovědi do souboru
        with open("notion_api_response_http.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\nOdpověď uložena do souboru notion_api_response_http.json")
    else:
        print(f"Chyba při připojení k Notion API: {response.status}")
        print(response_data)
except Exception as e:
    print(f"Neočekávaná chyba: {e}")

# Počkejme na vstup od uživatele, aby se okno nezavřelo
input("\nStiskněte Enter pro ukončení...")
