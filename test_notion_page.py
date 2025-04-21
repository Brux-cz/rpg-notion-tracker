import http.client
import json
import ssl

# API klíč
api_key = "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"

# ID stránky
page_id = "1dcbaf6cb5c180b8aeb5c8cee78379b1"

# Nastavení hlaviček pro API požadavek
headers = {
    "Authorization": f"Bearer {api_key}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Otevření souboru pro zápis
with open("notion_page_test.txt", "w", encoding="utf-8") as f:
    f.write("=== Test získání stránky z Notion API ===\n\n")
    
    try:
        # Vytvoření SSL kontextu
        context = ssl.create_default_context()
        
        # Vytvoření připojení
        conn = http.client.HTTPSConnection("api.notion.com", context=context)
        
        # Získání informací o stránce
        f.write("Získávání informací o stránce...\n")
        conn.request("GET", f"/v1/pages/{page_id}", headers=headers)
        
        # Získání odpovědi
        response = conn.getresponse()
        
        # Čtení odpovědi
        response_data = response.read().decode('utf-8')
        
        # Zápis statusu a odpovědi do souboru
        f.write(f"Status kód: {response.status}\n")
        f.write(f"Odpověď: {response_data}\n")
        
    except Exception as e:
        f.write(f"Neočekávaná chyba: {e}\n")

print("Test dokončen. Výsledky byly uloženy do souboru notion_page_test.txt")
