import http.client
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
    
    # Výpis statusu a odpovědi
    print(f"Status kód: {response.status}")
    print(response_data)
    
except Exception as e:
    print(f"Neočekávaná chyba: {e}")

input("Stiskněte Enter pro ukončení...")
