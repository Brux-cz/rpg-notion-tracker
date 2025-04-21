# PowerShell skript pro kontrolu stavu Git repozitáře

# Nastavení proměnných
$projectDir = "c:\Users\user\Documents\augment-projects\ai bot"
$outputFile = "c:\Users\user\Documents\git_status.txt"

# Přejít do adresáře projektu
Set-Location $projectDir

# Vytvořit výstupní soubor
"Git Status Report" | Out-File -FilePath $outputFile
"==================" | Out-File -FilePath $outputFile -Append
"" | Out-File -FilePath $outputFile -Append

# Kontrola, zda je složka Git repozitářem
"Kontrola, zda je složka Git repozitářem:" | Out-File -FilePath $outputFile -Append
if (Test-Path ".git") {
    "ANO - Složka je Git repozitářem" | Out-File -FilePath $outputFile -Append
    
    # Kontrola konfigurace vzdáleného repozitáře
    "Konfigurace vzdáleného repozitáře:" | Out-File -FilePath $outputFile -Append
    git remote -v 2>&1 | Out-File -FilePath $outputFile -Append
    
    # Kontrola stavu repozitáře
    "Stav repozitáře:" | Out-File -FilePath $outputFile -Append
    git status 2>&1 | Out-File -FilePath $outputFile -Append
    
    # Kontrola větví
    "Větve:" | Out-File -FilePath $outputFile -Append
    git branch 2>&1 | Out-File -FilePath $outputFile -Append
} else {
    "NE - Složka není Git repozitářem" | Out-File -FilePath $outputFile -Append
}

# Výpis obsahu složky
"" | Out-File -FilePath $outputFile -Append
"Obsah složky:" | Out-File -FilePath $outputFile -Append
Get-ChildItem -Force | Out-File -FilePath $outputFile -Append

# Výpis informací o systému
"" | Out-File -FilePath $outputFile -Append
"Informace o systému:" | Out-File -FilePath $outputFile -Append
"OS: $([System.Environment]::OSVersion.VersionString)" | Out-File -FilePath $outputFile -Append
"PowerShell verze: $($PSVersionTable.PSVersion)" | Out-File -FilePath $outputFile -Append
"Git verze: $(git --version 2>&1)" | Out-File -FilePath $outputFile -Append

Write-Host "Kontrola dokončena. Výsledky byly uloženy do souboru: $outputFile"
