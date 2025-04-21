"""
Testy pro datové modely entit.
"""
from datetime import datetime

import pytest

from rpg_notion.models.entities import (
    AdventureJournalEntry, EntityType, Event, Faction, Item, ItemType, Location, LocationStatus, LocationType, Monster,
    MonsterStatus, NPC, NPCStatus, Quest, QuestStatus
)


def test_npc_creation():
    """
    Test vytvoření NPC.
    """
    npc = NPC(
        name="Gandalf",
        description="Mocný čaroděj",
        status=NPCStatus.ALIVE,
        occupation="Čaroděj",
        tags=["Důležitý", "Spojenec"]
    )
    
    assert npc.name == "Gandalf"
    assert npc.description == "Mocný čaroděj"
    assert npc.status == NPCStatus.ALIVE
    assert npc.occupation == "Čaroděj"
    assert npc.tags == ["Důležitý", "Spojenec"]
    assert npc.type == EntityType.NPC


def test_location_creation():
    """
    Test vytvoření lokace.
    """
    location = Location(
        name="Roklinka",
        location_type=LocationType.CITY,
        hierarchy="Středozem > Eriador > Roklinka",
        description="Elfské město v údolí",
        status=LocationStatus.PROSPEROUS,
        tags=["Elfské", "Bezpečné"]
    )
    
    assert location.name == "Roklinka"
    assert location.location_type == LocationType.CITY
    assert location.hierarchy == "Středozem > Eriador > Roklinka"
    assert location.description == "Elfské město v údolí"
    assert location.status == LocationStatus.PROSPEROUS
    assert location.tags == ["Elfské", "Bezpečné"]
    assert location.type == EntityType.LOCATION


def test_monster_creation():
    """
    Test vytvoření příšery.
    """
    monster = Monster(
        name="Drak",
        description="Obrovský ohnivý drak",
        status=MonsterStatus.ALIVE,
        weaknesses_strengths="Slabina: břicho, Silné stránky: oheň, drápy",
        tags=["Boss", "Unikátní"]
    )
    
    assert monster.name == "Drak"
    assert monster.description == "Obrovský ohnivý drak"
    assert monster.status == MonsterStatus.ALIVE
    assert monster.weaknesses_strengths == "Slabina: břicho, Silné stránky: oheň, drápy"
    assert monster.tags == ["Boss", "Unikátní"]
    assert monster.type == EntityType.MONSTER


def test_item_creation():
    """
    Test vytvoření předmětu.
    """
    item = Item(
        name="Excalibur",
        item_type=ItemType.WEAPON,
        description="Legendární meč",
        special_abilities="Zvyšuje sílu o 5",
        tags=["Legendární", "Questový"]
    )
    
    assert item.name == "Excalibur"
    assert item.item_type == ItemType.WEAPON
    assert item.description == "Legendární meč"
    assert item.special_abilities == "Zvyšuje sílu o 5"
    assert item.tags == ["Legendární", "Questový"]
    assert item.type == EntityType.ITEM


def test_quest_creation():
    """
    Test vytvoření questu.
    """
    quest = Quest(
        name="Záchrana princezny",
        description="Zachraňte princeznu ze spárů draka",
        status=QuestStatus.ACTIVE,
        rewards="1000 zlatých, meč +2",
        tags=["Hlavní", "Časově omezený"]
    )
    
    assert quest.name == "Záchrana princezny"
    assert quest.description == "Zachraňte princeznu ze spárů draka"
    assert quest.status == QuestStatus.ACTIVE
    assert quest.rewards == "1000 zlatých, meč +2"
    assert quest.tags == ["Hlavní", "Časově omezený"]
    assert quest.type == EntityType.QUEST


def test_faction_creation():
    """
    Test vytvoření frakce.
    """
    faction = Faction(
        name="Království Gondor",
        description="Lidské království na jihu",
        faction_relations="Spojenec s Rohanem, nepřítel Mordoru",
        player_relation=75,
        tags=["Přátelská", "Vojenská"]
    )
    
    assert faction.name == "Království Gondor"
    assert faction.description == "Lidské království na jihu"
    assert faction.faction_relations == "Spojenec s Rohanem, nepřítel Mordoru"
    assert faction.player_relation == 75
    assert faction.tags == ["Přátelská", "Vojenská"]
    assert faction.type == EntityType.FACTION


def test_event_creation():
    """
    Test vytvoření události.
    """
    event = Event(
        name="Bitva o Helmův žleb",
        date=datetime(2023, 1, 15, 14, 30),
        description="Velká bitva mezi lidmi a skřety",
        consequences="Vítězství lidí, mnoho padlých na obou stranách",
        tags=["Souboj", "Důležitá"]
    )
    
    assert event.name == "Bitva o Helmův žleb"
    assert event.date == datetime(2023, 1, 15, 14, 30)
    assert event.description == "Velká bitva mezi lidmi a skřety"
    assert event.consequences == "Vítězství lidí, mnoho padlých na obou stranách"
    assert event.tags == ["Souboj", "Důležitá"]
    assert event.type == EntityType.EVENT


def test_adventure_journal_entry_creation():
    """
    Test vytvoření záznamu v deníku dobrodružství.
    """
    entry = AdventureJournalEntry(
        name="Začátek dobrodružství",
        date=datetime(2023, 1, 10, 18, 0),
        summary="Družina se setkala v hostinci a vydala se na cestu",
        tags=["Začátek", "Setkání"]
    )
    
    assert entry.name == "Začátek dobrodružství"
    assert entry.date == datetime(2023, 1, 10, 18, 0)
    assert entry.summary == "Družina se setkala v hostinci a vydala se na cestu"
    assert entry.tags == ["Začátek", "Setkání"]
    assert entry.type == EntityType.ADVENTURE_JOURNAL
