Write-Host "Testuji pripojeni k Notion API..."

$headers = @{
    "Authorization" = "Bearer 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"
    "Notion-Version" = "2022-06-28"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.notion.com/v1/users/me" -Headers $headers -Method Get
    
    Write-Host "Pripojeni k Notion API je funkcni!"
    Write-Host "Prihlaseny uzivatel: $($response.name)"
    Write-Host "ID uzivatele: $($response.id)"
    
    Write-Host "`nKompletni odpoved:"
    $response | ConvertTo-Json -Depth 10
    
    # Ulozeni odpovedi do souboru
    $response | ConvertTo-Json -Depth 10 | Out-File -FilePath "notion_api_response.json" -Encoding utf8
    Write-Host "`nOdpoved ulozena do souboru notion_api_response.json"
}
catch {
    Write-Host "Chyba pri pripojeni k Notion API: $_"
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status kod: $statusCode"
        
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $responseBody = $reader.ReadToEnd()
        Write-Host "Odpoved: $responseBody"
    }
}

Write-Host "`nStisknete Enter pro ukonceni..."
$null = Read-Host
