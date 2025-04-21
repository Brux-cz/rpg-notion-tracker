# RPG Notion

Systém pro automatické zaznamenávání obsahu solo RPG her s AI do Notion.

## Popis

Tento projekt implementuje komplexní systém, který automaticky extrahuje a organizuje informace z textových výstupů AI během hraní solo RPG her. Systém identifikuje postavy, lokace, předměty, příšery, questy a další entity, a ukládá je do strukturovaných databází v Notion.

## Funkce

- Automatické rozpoznávání a extrakce entit z textu hry
- Dynamická aktualizace záznamů v Notion
- Strukturovaná organizace dat v osmi propojených databázích
- Automatická kategorizace a tagování entit
- Propojení souvisejících entit
- Chronologický deník a časová osa událostí
- Sledování questů a úkolů
- Reputační systém a vztahy mezi frakcemi
- Intuitivní uživatelské rozhraní

## Instalace

1. Klonujte repozitář:
   ```
   git clone https://github.com/yourusername/rpg_notion.git
   cd rpg_notion
   ```

2. Vytvořte virtuální prostředí a nainstalujte závislosti:
   ```
   python -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   pip install -e .
   ```

3. Vytvořte soubor `.env` podle vzoru `.env.example` a nastavte potřebné proměnné prostředí.

## Použití

### Nastavení Notion API

1. Přejděte na stránku [Notion Integrations](https://www.notion.so/my-integrations)
2. Klikněte na tlačítko "+ New integration"
3. Vyplňte základní informace:
   - Název: "RPG Notion Tracker"
   - Logo: Můžete nahrát vlastní nebo ponechat výchozí
   - Vyberte pracovní prostor, kde budete integraci používat
4. V sekci "Capabilities" zaškrtněte:
   - Read content
   - Update content
   - Insert content
5. Klikněte na "Submit" pro vytvoření integrace
6. Zkopírujte vygenerovaný "Internal Integration Token" do souboru `.env`

### Inicializace databází v Notion

1. Vytvořte novou stránku v Notion, která bude sloužit jako rodičovská stránka pro všechny databáze
2. Klikněte na "..." v pravém horním rohu stránky
3. Vyberte "Add connections"
4. Vyhledejte a vyberte vaši integraci "RPG Notion Tracker"
5. Zkopírujte ID stránky z URL (je to dlouhý řetězec znaků po posledním "/" a před "?")
6. Spusťte skript pro inicializaci databází:
   ```
   python -m rpg_notion.scripts.init_notion_databases --parent-page-id ID_RODIČOVSKÉ_STRÁNKY
   ```

### Testování NLP funkcí

Pro testování extrakce entit a atributů z textu můžete použít skript `test_nlp.py`:

```
python -m rpg_notion.scripts.test_nlp --text-file rpg_notion/data/test_text.txt --entity-name "Gandalf" --entity-type "npc" --output output.json
```

Parametry:
- `--text`: Text k zpracování
- `--text-file`: Cesta k souboru s textem k zpracování
- `--entity-name`: Název entity pro extrakci atributů
- `--entity-type`: Typ entity (npc, location, monster, item, quest, faction, event)
- `--output`: Cesta k výstupnímu souboru

### Testování správců dat

Pro testování správců dat (entity updater, quest manager, reputation manager, state manager) můžete použít skript `test_data_managers.py`:

```
python -m rpg_notion.scripts.test_data_managers --text-file rpg_notion/data/test_text.txt --test-type all --output data_managers_output.txt
```

Parametry:
- `--text`: Text k zpracování
- `--text-file`: Cesta k souboru s textem k zpracování
- `--test-type`: Typ testu (entity-updater, quest-manager, reputation-manager, state-manager, all)
- `--output`: Cesta k výstupnímu souboru
- `--notion-token`: Notion API token (volitelné)
- `--notion-parent-page-id`: ID rodičovské stránky v Notion (volitelné)

## Licence

Tento projekt je licencován pod MIT licencí - viz soubor [LICENSE](LICENSE) pro detaily.
