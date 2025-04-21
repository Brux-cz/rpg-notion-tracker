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
with open("notion_practical_test.txt", "w", encoding="utf-8") as f:
    f.write("=== Test připojení k Notion API v praxi ===\n\n")

    try:
        # Vytvoření SSL kontextu
        context = ssl.create_default_context()

        # Vytvoření připojení
        conn = http.client.HTTPSConnection("api.notion.com", context=context)

        # 1. Získání informací o stránce
        f.write("1. Získávání informací o stránce...\n")
        conn.request("GET", f"/v1/pages/{page_id}", headers=headers)

        # Získání odpovědi
        response = conn.getresponse()

        # Čtení odpovědi
        response_data = response.read().decode('utf-8')

        # Zápis statusu a odpovědi do souboru
        f.write(f"Status kód: {response.status}\n")

        if response.status == 200:
            f.write("Stránka byla úspěšně nalezena!\n")
            data = json.loads(response_data)
            f.write(f"Název stránky: {data.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Bez názvu')}\n")
            f.write(f"ID stránky: {data.get('id')}\n")
            f.write(f"URL stránky: {data.get('url')}\n\n")
        else:
            f.write(f"Chyba při získávání stránky: {response_data}\n\n")

        # 2. Vytvoření testovací stránky
        f.write("2. Vytváření testovací stránky...\n")

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

        # Odeslání požadavku
        conn.request("POST", "/v1/pages", body=page_data_json, headers=headers)

        # Získání odpovědi
        response = conn.getresponse()

        # Čtení odpovědi
        response_data = response.read().decode('utf-8')

        # Zápis statusu a odpovědi do souboru
        f.write(f"Status kód: {response.status}\n")

        if response.status == 200:
            f.write("Stránka byla úspěšně vytvořena!\n")
            data = json.loads(response_data)
            f.write(f"ID nové stránky: {data.get('id')}\n")
            f.write(f"URL nové stránky: {data.get('url')}\n\n")
        else:
            f.write(f"Chyba při vytváření stránky: {response_data}\n\n")

    except Exception as e:
        f.write(f"Neočekávaná chyba: {e}\n")

print("Test dokončen. Výsledky byly uloženy do souboru notion_practical_test.txt")
