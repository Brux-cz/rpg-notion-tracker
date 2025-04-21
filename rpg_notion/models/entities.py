"""
Datové modely pro entity v RPG Notion.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """
    Typy entit v RPG Notion.
    """
    NPC = "npc"
    LOCATION = "location"
    MONSTER = "monster"
    ITEM = "item"
    QUEST = "quest"
    FACTION = "faction"
    EVENT = "event"
    ADVENTURE_JOURNAL = "adventure_journal"


class NPCStatus(str, Enum):
    """
    Stavy NPC.
    """
    ALIVE = "Živý"
    DEAD = "Mrtvý"
    INJURED = "Zraněný"
    UNKNOWN = "Neznámý"


class LocationType(str, Enum):
    """
    Typy lokací.
    """
    CITY = "Město"
    VILLAGE = "Vesnice"
    DUNGEON = "Dungeon"
    FOREST = "Les"
    MOUNTAIN = "Hora"
    CAVE = "Jeskyně"
    CASTLE = "Hrad"
    TEMPLE = "Chrám"
    RUINS = "Ruiny"


class LocationStatus(str, Enum):
    """
    Stavy lokací.
    """
    PROSPEROUS = "Prosperující"
    DECLINING = "V úpadku"
    DESTROYED = "Zničené"
    ABANDONED = "Opuštěné"
    DANGEROUS = "Nebezpečné"
    SAFE = "Bezpečné"


class MonsterStatus(str, Enum):
    """
    Stavy příšer.
    """
    ALIVE = "Živá"
    DEAD = "Mrtvá"
    INJURED = "Zraněná"
    UNKNOWN = "Neznámý"


class ItemType(str, Enum):
    """
    Typy předmětů.
    """
    WEAPON = "Zbraň"
    ARMOR = "Brnění"
    ARTIFACT = "Artefakt"
    POTION = "Lektvar"
    SCROLL = "Svitek"
    COMMON_ITEM = "Běžný předmět"
    KEY = "Klíč"


class QuestStatus(str, Enum):
    """
    Stavy questů.
    """
    ACTIVE = "Aktivní"
    COMPLETED = "Dokončený"
    FAILED = "Selhaný"
    PAUSED = "Pozastavený"


class BaseEntity(BaseModel):
    """
    Základní model pro entity.
    """
    id: Optional[str] = None
    name: str
    type: EntityType
    tags: List[str] = Field(default_factory=list)
    notion_page_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NPC(BaseEntity):
    """
    Model pro NPC.
    """
    type: EntityType = EntityType.NPC
    description: str = ""
    status: NPCStatus = NPCStatus.ALIVE
    occupation: str = ""
    location_id: Optional[str] = None
    related_npc_ids: List[str] = Field(default_factory=list)
    item_ids: List[str] = Field(default_factory=list)
    history: str = ""


class Location(BaseEntity):
    """
    Model pro lokaci.
    """
    type: EntityType = EntityType.LOCATION
    location_type: LocationType
    hierarchy: str = ""
    description: str = ""
    npc_ids: List[str] = Field(default_factory=list)
    item_ids: List[str] = Field(default_factory=list)
    event_ids: List[str] = Field(default_factory=list)
    status: LocationStatus = LocationStatus.SAFE


class Monster(BaseEntity):
    """
    Model pro příšeru.
    """
    type: EntityType = EntityType.MONSTER
    description: str = ""
    location_ids: List[str] = Field(default_factory=list)
    status: MonsterStatus = MonsterStatus.ALIVE
    combat_history: str = ""
    weaknesses_strengths: str = ""
    loot_ids: List[str] = Field(default_factory=list)


class Item(BaseEntity):
    """
    Model pro předmět.
    """
    type: EntityType = EntityType.ITEM
    item_type: ItemType
    description: str = ""
    location_id: Optional[str] = None
    owner_id: Optional[str] = None
    ownership_history: str = ""
    special_abilities: str = ""


class Quest(BaseEntity):
    """
    Model pro quest.
    """
    type: EntityType = EntityType.QUEST
    description: str = ""
    giver_id: Optional[str] = None
    status: QuestStatus = QuestStatus.ACTIVE
    rewards: str = ""
    location_ids: List[str] = Field(default_factory=list)
    npc_ids: List[str] = Field(default_factory=list)
    timeline: str = ""


class Faction(BaseEntity):
    """
    Model pro frakci.
    """
    type: EntityType = EntityType.FACTION
    description: str = ""
    member_ids: List[str] = Field(default_factory=list)
    territory_ids: List[str] = Field(default_factory=list)
    faction_relations: str = ""
    player_relation: int = 0
    event_ids: List[str] = Field(default_factory=list)


class Event(BaseEntity):
    """
    Model pro událost.
    """
    type: EntityType = EntityType.EVENT
    date: Optional[datetime] = None
    description: str = ""
    location_id: Optional[str] = None
    npc_ids: List[str] = Field(default_factory=list)
    consequences: str = ""


class AdventureJournalEntry(BaseEntity):
    """
    Model pro záznam v deníku dobrodružství.
    """
    type: EntityType = EntityType.ADVENTURE_JOURNAL
    date: Optional[datetime] = None
    summary: str = ""
    event_ids: List[str] = Field(default_factory=list)
    npc_ids: List[str] = Field(default_factory=list)
    location_ids: List[str] = Field(default_factory=list)
