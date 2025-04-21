@echo off
echo Nahrávám projekt na GitHub...

cd "c:\Users\user\Documents\augment-projects\ai bot"

echo Inicializuji Git repozitář...
git init

echo Přidávám soubory do Gitu...
git add .

echo Vytvářím první commit...
git commit -m "Počáteční commit - implementace Fáze 1-3"

echo Nastavuji vzdálený repozitář...
git remote add origin https://github.com/Brux-cz/rpg-notion-tracker.git

echo Nahrávám na GitHub...
git push -u origin master

echo Hotovo! Projekt byl nahrán na GitHub.
echo URL repozitáře: https://github.com/Brux-cz/rpg-notion-tracker

pause
