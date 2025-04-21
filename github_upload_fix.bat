@echo off
echo ===== Řešení problémů s nahráním na GitHub =====
echo.

cd "c:\Users\user\Documents\augment-projects\ai bot"

echo 1. Kontrola stavu Git repozitáře...
git status
echo.

echo 2. Odstranění existujícího vzdáleného repozitáře (pokud existuje)...
git remote remove origin
echo.

echo 3. Přidání správného vzdáleného repozitáře...
git remote add origin https://github.com/Brux-cz/rpg-notion-tracker.git
echo.

echo 4. Kontrola vzdálených repozitářů...
git remote -v
echo.

echo 5. Nastavení hlavní větve na 'main'...
git branch -M main
echo.

echo 6. Přidání všech souborů (pokud ještě nejsou přidány)...
git add .
echo.

echo 7. Vytvoření commitu (pokud ještě není vytvořen)...
git commit -m "Počáteční commit - implementace Fáze 1-3"
echo.

echo 8. Nahrání na GitHub s přepsáním (force push)...
git push -f -u origin main
echo.

echo ===== Hotovo! =====
echo Zkontrolujte svůj GitHub repozitář: https://github.com/Brux-cz/rpg-notion-tracker
echo.

pause
