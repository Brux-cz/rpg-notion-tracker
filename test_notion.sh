#!/bin/bash

# Přímé nastavení API klíče
API_KEY="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"

# Nastavení hlaviček pro API požadavek
echo "Testuji připojení k Notion API..."
curl -s -X GET "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json"

echo -e "\nStiskněte Enter pro ukončení..."
read
