#!/usr/bin/env python
"""
Skript pro testování správců dat.
"""
import argparse
import json
import logging
import sys
from pathlib import Path

# Přidání nadřazeného adresáře do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from rpg_notion.api.notion_client import NotionClient
from rpg_notion.data.entity_updater import EntityUpdater
from rpg_notion.data.quest_manager import QuestManager, QuestStatus
from rpg_notion.data.reputation_manager import ReputationManager, FactionRelationship, ReputationLevel
from rpg_notion.data.state_manager import StateManager
from rpg_notion.models.entities import (
    AdventureJournalEntry, BaseEntity, EntityType, Event, Faction, Item, Location, Monster, NPC, Quest
)
from rpg_notion.models.repository import EntityRepository
from rpg_notion.nlp.text_processor import TextProcessor

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def parse_args():
    """
    Parsování argumentů příkazové řádky.
    """
    parser = argparse.ArgumentParser(description="Test správců dat.")
    parser.add_argument(
        "--text",
        type=str,
        help="Text k zpracování.",
    )
    parser.add_argument(
        "--text-file",
        type=str,
        help="Cesta k souboru s textem k zpracování.",
    )
    parser.add_argument(
        "--test-type",
        type=str,
        choices=["entity-updater", "quest-manager", "reputation-manager", "state-manager", "all"],
        default="all",
        help="Typ testu.",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Cesta k výstupnímu souboru.",
    )
    parser.add_argument(
        "--notion-token",
        type=str,
        help="Notion API token.",
    )
    parser.add_argument(
        "--notion-parent-page-id",
        type=str,
        help="ID rodičovské stránky v Notion.",
    )
    return parser.parse_args()


def test_entity_updater(text, notion_client=None, entity_repository=None, text_processor=None):
    """
    Test správce aktualizací entit.
    """
    logger.info("=== Test správce aktualizací entit ===")
    
    # Inicializace správce aktualizací entit
    entity_updater = EntityUpdater(
        notion_client=notion_client,
        entity_repository=entity_repository,
        text_processor=text_processor,
    )
    
    # Zpracování textu a aktualizace entit
    logger.info("Zpracovávám text a aktualizuji entity...")
    entities = entity_updater.process_and_update(text)
    
    # Výpis entit
    for entity_type, entity_list in entities.items():
        if entity_list:
            logger.info(f"Entity typu {entity_type}:")
            for entity in entity_list:
                logger.info(f"  - {entity.name}")
    
    # Vytvoření záznamu v deníku
    logger.info("Vytvářím záznam v deníku...")
    journal_entry = entity_updater.create_journal_entry(
        text=text,
        title="Testovací záznam",
        session_number=1,
    )
    logger.info(f"Vytvořen záznam v deníku: {journal_entry.title}")
    
    return entities


def test_quest_manager(text, notion_client=None, entity_repository=None):
    """
    Test správce questů.
    """
    logger.info("=== Test správce questů ===")
    
    # Inicializace správce questů
    quest_manager = QuestManager(
        entity_repository=entity_repository,
    )
    
    # Extrakce questů z textu
    logger.info("Extrahuji questy z textu...")
    quests = quest_manager.extract_quests_from_text(text)
    
    # Výpis questů
    if quests:
        logger.info(f"Extrahováno {len(quests)} questů:")
        for quest in quests:
            logger.info(f"  - {quest.name}")
    else:
        logger.info("Nebyly extrahovány žádné questy.")
    
    # Vytvoření testovacího questu
    logger.info("Vytvářím testovací quest...")
    test_quest = quest_manager.create_quest(
        name="Testovací quest",
        description="Toto je testovací quest vytvořený pro účely testování.",
        quest_type="Test",
        tags=["Test", "Automaticky vytvořený"],
    )
    logger.info(f"Vytvořen quest: {test_quest.name}")
    
    # Přidání úkolů do questu
    logger.info("Přidávám úkoly do questu...")
    task1 = quest_manager.add_task_to_quest(
        quest=test_quest,
        task_name="Úkol 1",
        task_description="Toto je první úkol.",
    )
    task2 = quest_manager.add_task_to_quest(
        quest=test_quest,
        task_name="Úkol 2",
        task_description="Toto je druhý úkol.",
    )
    task3 = quest_manager.add_task_to_quest(
        quest=test_quest,
        task_name="Úkol 3",
        task_description="Toto je třetí úkol.",
        optional=True,
    )
    logger.info(f"Přidány úkoly: {task1.name}, {task2.name}, {task3.name}")
    
    # Zahájení questu
    logger.info("Zahajuji quest...")
    test_quest = quest_manager.start_quest(test_quest)
    logger.info(f"Quest zahájen. Stav: {test_quest.status}")
    
    # Dokončení úkolů
    logger.info("Dokončuji úkoly...")
    test_quest = quest_manager.complete_task(test_quest, task1.id)
    logger.info(f"Úkol 1 dokončen.")
    test_quest = quest_manager.complete_task(test_quest, task2.id)
    logger.info(f"Úkol 2 dokončen.")
    
    # Kontrola stavu questu
    logger.info(f"Stav questu po dokončení úkolů: {test_quest.status}")
    
    # Získání aktivních questů
    logger.info("Získávám aktivní questy...")
    active_quests = quest_manager.get_active_quests()
    logger.info(f"Počet aktivních questů: {len(active_quests)}")
    
    # Získání dokončených questů
    logger.info("Získávám dokončené questy...")
    completed_quests = quest_manager.get_completed_quests()
    logger.info(f"Počet dokončených questů: {len(completed_quests)}")
    
    return quests + [test_quest]


def test_reputation_manager(notion_client=None, entity_repository=None):
    """
    Test správce reputace.
    """
    logger.info("=== Test správce reputace ===")
    
    # Inicializace správce reputace
    reputation_manager = ReputationManager(
        entity_repository=entity_repository,
    )
    
    # Vytvoření testovacích frakcí
    logger.info("Vytvářím testovací frakce...")
    faction1 = reputation_manager.create_faction(
        name="Testovací frakce 1",
        description="Toto je první testovací frakce.",
        faction_type="Test",
        tags=["Test", "Automaticky vytvořená"],
    )
    faction2 = reputation_manager.create_faction(
        name="Testovací frakce 2",
        description="Toto je druhá testovací frakce.",
        faction_type="Test",
        tags=["Test", "Automaticky vytvořená"],
    )
    logger.info(f"Vytvořeny frakce: {faction1.name}, {faction2.name}")
    
    # Nastavení vztahu mezi frakcemi
    logger.info("Nastavuji vztah mezi frakcemi...")
    faction1, faction2 = reputation_manager.set_faction_relationship(
        faction1=faction1,
        faction2=faction2,
        relationship=FactionRelationship.FRIENDLY,
    )
    logger.info(f"Vztah nastaven na: {FactionRelationship.FRIENDLY.value}")
    
    # Změna reputace hráče
    logger.info("Měním reputaci hráče...")
    faction1 = reputation_manager.change_player_reputation(
        faction=faction1,
        change=1500,
        reason="Test změny reputace",
    )
    logger.info(f"Reputace hráče u frakce {faction1.name}: {faction1.player_reputation}")
    
    # Získání úrovně reputace
    logger.info("Získávám úroveň reputace...")
    reputation_level = reputation_manager.get_player_reputation_level(faction1)
    logger.info(f"Úroveň reputace: {reputation_level.value}")
    
    # Získání spojeneckých frakcí
    logger.info("Získávám spojenecké frakce...")
    allied_factions = reputation_manager.get_allied_factions(faction1)
    logger.info(f"Počet spojeneckých frakcí: {len(allied_factions)}")
    
    # Získání nepřátelských frakcí
    logger.info("Získávám nepřátelské frakce...")
    hostile_factions = reputation_manager.get_hostile_factions(faction1)
    logger.info(f"Počet nepřátelských frakcí: {len(hostile_factions)}")
    
    return [faction1, faction2]


def test_state_manager(notion_client=None, entity_repository=None):
    """
    Test správce stavu.
    """
    logger.info("=== Test správce stavu ===")
    
    # Inicializace správce stavu
    state_manager = StateManager(
        entity_repository=entity_repository,
    )
    
    # Vytvoření testovací NPC postavy
    logger.info("Vytvářím testovací NPC...")
    npc = NPC(
        name="Testovací NPC",
        description="Toto je testovací NPC vytvořené pro účely testování.",
        status="Živý",
        tags=["Test", "Automaticky vytvořené"],
    )
    npc = entity_repository.create_npc(npc)
    logger.info(f"Vytvořeno NPC: {npc.name}")
    
    # Sledování změny stavu
    logger.info("Sleduji změnu stavu...")
    state_change = state_manager.track_state_change(
        entity=npc,
        old_state="Živý",
        new_state="Zraněný",
        description="NPC bylo zraněno během testu.",
    )
    logger.info(f"Změna stavu: {state_change}")
    
    # Získání změn stavu
    logger.info("Získávám změny stavu...")
    state_changes = state_manager.get_state_changes(
        entity_type=EntityType.NPC,
        entity_id=npc.id,
    )
    logger.info(f"Počet změn stavu: {len(state_changes)}")
    
    # Vytvoření události na časové ose
    logger.info("Vytvářím událost na časové ose...")
    event = state_manager.create_timeline_event(state_change)
    logger.info(f"Vytvořena událost: {event.name}")
    
    return [npc, event]


def main():
    """
    Hlavní funkce skriptu.
    """
    args = parse_args()

    # Kontrola, zda je zadán text nebo cesta k souboru
    if not args.text and not args.text_file:
        logger.error("Musí být zadán text nebo cesta k souboru.")
        sys.exit(1)

    # Načtení textu
    if args.text_file:
        try:
            with open(args.text_file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Chyba při načítání souboru: {e}")
            sys.exit(1)
    else:
        text = args.text

    # Inicializace Notion klienta
    notion_client = None
    if args.notion_token:
        notion_client = NotionClient(token=args.notion_token)
    
    # Inicializace repozitáře entit
    entity_repository = EntityRepository(notion_client=notion_client)
    
    # Inicializace procesoru textu
    text_processor = TextProcessor(entity_repository=entity_repository)
    
    # Výsledky testů
    results = {}
    
    # Spuštění testů podle typu
    if args.test_type in ["entity-updater", "all"]:
        results["entity_updater"] = test_entity_updater(
            text=text,
            notion_client=notion_client,
            entity_repository=entity_repository,
            text_processor=text_processor,
        )
    
    if args.test_type in ["quest-manager", "all"]:
        results["quest_manager"] = test_quest_manager(
            text=text,
            notion_client=notion_client,
            entity_repository=entity_repository,
        )
    
    if args.test_type in ["reputation-manager", "all"]:
        results["reputation_manager"] = test_reputation_manager(
            notion_client=notion_client,
            entity_repository=entity_repository,
        )
    
    if args.test_type in ["state-manager", "all"]:
        results["state_manager"] = test_state_manager(
            notion_client=notion_client,
            entity_repository=entity_repository,
        )
    
    # Uložení výsledků do souboru
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write("=== Výsledky testů ===\n\n")
                
                for test_type, result in results.items():
                    f.write(f"=== {test_type} ===\n")
                    if isinstance(result, dict):
                        for entity_type, entities in result.items():
                            f.write(f"Entity typu {entity_type}:\n")
                            for entity in entities:
                                f.write(f"  - {entity.name}\n")
                    elif isinstance(result, list):
                        f.write(f"Počet entit: {len(result)}\n")
                        for entity in result:
                            f.write(f"  - {entity.name}\n")
                    f.write("\n")
            
            logger.info(f"Výsledky byly uloženy do souboru {args.output}")
        except Exception as e:
            logger.error(f"Chyba při ukládání výsledků: {e}")


if __name__ == "__main__":
    main()
