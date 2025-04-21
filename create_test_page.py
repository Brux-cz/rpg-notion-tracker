import http.client
import json
import ssl
import time

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
with open("notion_create_test.txt", "w", encoding="utf-8") as f:
    f.write("=== Test vytvoření stránky v Notion API ===\n\n")
    
    try:
        # Vytvoření SSL kontextu
        context = ssl.create_default_context()
        
        # Vytvoření připojení
        conn = http.client.HTTPSConnection("api.notion.com", context=context)
        
        # Příprava dat pro vytvoření stránky
        page_data = {
            "parent": {"page_id": page_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": "Testovací stránka z Python skriptu"
                            }
                        }
                    ]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Toto je testovací stránka vytvořená pomocí Notion API."
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Test byl proveden: " + time.strftime("%d.%m.%Y %H:%M:%S")
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        # Převod dat na JSON
        page_data_json = json.dumps(page_data)
        
        # Zápis dat do souboru pro kontrolu
        f.write("Data pro vytvoření stránky:\n")
        f.write(page_data_json + "\n\n")
        
        # Odeslání požadavku
        f.write("Odesílám požadavek na vytvoření stránky...\n")
        conn.request("POST", "/v1/pages", body=page_data_json, headers=headers)
        
        # Získání odpovědi
        response = conn.getresponse()
        
        # Čtení odpovědi
        response_data = response.read().decode('utf-8')
        
        # Zápis statusu a odpovědi do souboru
        f.write(f"Status kód: {response.status}\n")
        f.write(f"Odpověď: {response_data}\n")
        
    except Exception as e:
        f.write(f"Neočekávaná chyba: {e}\n")

print("Test dokončen. Výsledky byly uloženy do souboru notion_create_test.txt")
