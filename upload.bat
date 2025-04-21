@echo off
echo ===== Nahrávání projektu na GitHub =====
echo.

echo 1. Inicializuji Git repozitář...
git init

echo 2. Nastavuji uživatelské jméno a email...
git config --global user.email "your.email@example.com"
git config --global user.name "Brux-cz"

echo 3. Přidávám soubory do Gitu...
git add .

echo 4. Vytvářím první commit...
git commit -m "Počáteční commit - implementace Fáze 1-3"

echo 5. Nastavuji vzdálený repozitář...
git remote add origin https://github.com/Brux-cz/rpg-notion-tracker.git

echo 6. Nastavuji hlavní větev na 'main'...
git branch -M main

echo 7. Nahrávám na GitHub...
git push -u origin main

echo.
echo ===== Hotovo! =====
echo Zkontrolujte svůj GitHub repozitář: https://github.com/Brux-cz/rpg-notion-tracker
echo.

pause
