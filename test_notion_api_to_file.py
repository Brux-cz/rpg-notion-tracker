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

# Otevření souboru pro zápis
with open("notion_api_response_direct.txt", "w", encoding="utf-8") as f:
    f.write("Testuji připojení k Notion API...\n")
    
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
        
        # Zápis statusu a odpovědi do souboru
        f.write(f"Status kód: {response.status}\n")
        f.write(response_data)
        
    except Exception as e:
        f.write(f"Neočekávaná chyba: {e}\n")

print("Test dokončen. Výsledky byly uloženy do souboru notion_api_response_direct.txt")
