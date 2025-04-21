@echo off
echo Testuji pripojeni k Notion API...
curl -X GET "https://api.notion.com/v1/users/me" -H "Authorization: Bearer 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" -H "Notion-Version: 2022-06-28" > notion_api_response.txt
echo Odpoved ulozena do souboru notion_api_response.txt
pause
