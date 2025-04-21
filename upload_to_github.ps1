# PowerShell skript pro nahrání projektu na GitHub

# Nastavení proměnných
$sourceDir = "c:\Users\user\Documents\augment-projects\ai bot"
$repoDir = "c:\Users\user\Documents\github-repos\rpg-notion-tracker"
$repoUrl = "https://github.com/VASE_UZIVATELSKE_JMENO/rpg-notion-tracker.git"

# Vytvoření cílového adresáře, pokud neexistuje
if (-not (Test-Path $repoDir)) {
    New-Item -ItemType Directory -Path $repoDir -Force
}

# Kopírování souborů
Write-Host "Kopíruji soubory z $sourceDir do $repoDir..."
robocopy $sourceDir $repoDir /E /XD .git

# Přejít do adresáře repozitáře
Set-Location $repoDir

# Inicializace Git repozitáře
Write-Host "Inicializuji Git repozitář..."
git init

# Přidání všech souborů do Gitu
Write-Host "Přidávám soubory do Gitu..."
git add .

# Vytvoření prvního commitu
Write-Host "Vytvářím první commit..."
git commit -m "Počáteční commit - implementace Fáze 1-3"

# Nastavení vzdáleného repozitáře
Write-Host "Nastavuji vzdálený repozitář..."
git remote add origin $repoUrl

# Nahrání na GitHub
Write-Host "Nahrávám na GitHub..."
git push -u origin master

Write-Host "Hotovo! Projekt byl nahrán na GitHub."
Write-Host "URL repozitáře: $repoUrl"

# Počkejte na stisknutí klávesy
Write-Host "Stiskněte libovolnou klávesu pro ukončení..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
