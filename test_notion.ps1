# Použití přímého API klíče
$apiKey = "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"

# Nastavení hlaviček pro API požadavek
$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Notion-Version" = "2022-06-28"
    "Content-Type" = "application/json"
}

# Testovací požadavek na Notion API
Write-Output "Testuji připojení k Notion API..."
try {
    $response = Invoke-RestMethod -Uri "https://api.notion.com/v1/users/me" -Headers $headers -Method Get

    # Výpis výsledků
    Write-Output "Připojení k Notion API je funkční!"
    Write-Output "Přihlášený uživatel: $($response.name)"
    Write-Output "ID uživatele: $($response.id)"
    $response | ConvertTo-Json
} catch {
    Write-Output "Chyba při připojení k Notion API: $_"
}

# Počkejme na vstup od uživatele, aby se okno nezavřelo
Write-Output "`nStiskněte Enter pro ukončení..."
$null = Read-Host