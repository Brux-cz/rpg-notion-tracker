# PowerShell skript pro nahrání projektu na GitHub

Write-Host "===== Nahrávání projektu na GitHub ====="
Write-Host ""

# 1. Inicializace Git repozitáře
Write-Host "1. Inicializuji Git repozitář..."
git init

# 2. Přidání všech souborů do Gitu
Write-Host "2. Přidávám soubory do Gitu..."
git add .

# 3. Vytvoření prvního commitu
Write-Host "3. Vytvářím první commit..."
git commit -m "Počáteční commit - implementace Fáze 1-3"

# 4. Nastavení vzdáleného repozitáře
Write-Host "4. Nastavuji vzdálený repozitář..."
git remote add origin https://github.com/Brux-cz/rpg-notion-tracker.git

# 5. Nastavení hlavní větve na 'main'
Write-Host "5. Nastavuji hlavní větev na 'main'..."
git branch -M main

# 6. Nahrání na GitHub
Write-Host "6. Nahrávám na GitHub..."
git push -u origin main

Write-Host ""
Write-Host "===== Hotovo! ====="
Write-Host "Zkontrolujte svůj GitHub repozitář: https://github.com/Brux-cz/rpg-notion-tracker"
Write-Host ""

# Pauza na konci
Write-Host "Stiskněte libovolnou klávesu pro ukončení..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
