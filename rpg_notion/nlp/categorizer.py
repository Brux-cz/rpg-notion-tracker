"""
Modul pro kategorizaci a tagování entit.
"""
import logging
import re
from typing import Dict, List, Optional, Set, Tuple, Union

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span, Token

from rpg_notion.config.settings import SPACY_MODEL
from rpg_notion.models.entities import EntityType

logger = logging.getLogger(__name__)


class EntityCategorizer:
    """
    Třída pro kategorizaci a tagování entit.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Inicializace kategorizátoru entit.

        Args:
            model_name: Název modelu spaCy. Pokud není zadán, použije se model z konfigurace.
        """
        self.model_name = model_name or SPACY_MODEL
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Načten model spaCy: {self.model_name}")
        except OSError:
            logger.warning(f"Model {self.model_name} není nainstalován. Stahuji...")
            spacy.cli.download(self.model_name)
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Model {self.model_name} byl úspěšně stažen a načten.")
        
        # Definice tagů pro jednotlivé typy entit
        self.npc_tags = {
            "Spojenec": ["spojenec", "přítel", "pomocník", "ochránce", "zachránce", "mentor", "učitel", "rádce"],
            "Nepřítel": ["nepřítel", "protivník", "záporák", "padouch", "zrádce", "vrah", "zločinec", "bandita", "lupič"],
            "Obchodník": ["obchodník", "prodavač", "kupec", "kramář", "handlíř", "překupník", "hokynář", "trhovník"],
            "Zadavatel questů": ["zadavatel", "quest", "úkol", "mise", "zakázka", "žádost", "prosba"],
            "Důležitý": ["důležitý", "klíčový", "významný", "mocný", "vlivný", "vůdce", "vládce", "král", "královna", "náčelník"]
        }
        
        self.location_tags = {
            "Obydlené": ["obydlené", "osídlené", "obývané", "lidé", "obyvatelé", "vesničané", "měšťané", "občané"],
            "Nebezpečné": ["nebezpečné", "nebezpečí", "hrozba", "riziko", "smrtící", "zákeřné", "zrádné", "děsivé", "strašidelné"],
            "Prozkoumané": ["prozkoumané", "známé", "zmapované", "objevené", "navštívené"],
            "Neprozkoumané": ["neprozkoumané", "neznámé", "nezmapované", "neobjevené", "tajemné", "záhadné"],
            "Důležité": ["důležité", "klíčové", "významné", "strategické", "mocné", "vlivné", "hlavní", "centrální"]
        }
        
        self.monster_tags = {
            "Boss": ["boss", "vůdce", "náčelník", "král", "královna", "pán", "paní", "vládce", "vládkyně", "mocný", "mocná", "silný", "silná"],
            "Běžná": ["běžná", "obyčejná", "normální", "slabá", "malá", "mladá", "nedospělá"],
            "Unikátní": ["unikátní", "jedinečná", "vzácná", "legendární", "mytická", "bájná", "pověstná"],
            "Inteligentní": ["inteligentní", "chytrá", "moudrá", "lstivá", "vychytralá", "mazaná", "důvtipná", "mluvící"],
            "Nemrtvá": ["nemrtvá", "neživá", "oživlá", "zombie", "kostlivec", "duch", "přízrak", "stín", "upír", "lich"]
        }
        
        self.item_tags = {
            "Běžný": ["běžný", "obyčejný", "normální", "všední", "každodenní", "prostý"],
            "Vzácný": ["vzácný", "neobvyklý", "nezvyklý", "výjimečný", "cenný", "drahý"],
            "Epický": ["epický", "mocný", "silný", "výkonný", "působivý", "úžasný"],
            "Legendární": ["legendární", "bájný", "mytický", "pověstný", "slavný", "proslulý"],
            "Prokletý": ["prokletý", "zlořečený", "zatracený", "temný", "zlý", "nebezpečný", "zákeřný"],
            "Questový": ["questový", "úkolový", "misijní", "klíčový", "důležitý", "nezbytný"]
        }
        
        self.quest_tags = {
            "Hlavní": ["hlavní", "primární", "klíčový", "důležitý", "zásadní", "nezbytný", "příběhový"],
            "Vedlejší": ["vedlejší", "sekundární", "volitelný", "doplňkový", "postranní", "nepodstatný"],
            "Frakční": ["frakční", "frakce", "organizace", "skupina", "cech", "gilda", "řád", "klan"],
            "Časově omezený": ["časově omezený", "časový limit", "termín", "deadline", "spěch", "rychle", "brzy"],
            "Průzkumný": ["průzkumný", "průzkum", "objevování", "hledání", "pátrání", "zkoumání", "mapování"]
        }
        
        self.faction_tags = {
            "Přátelská": ["přátelská", "spojenecká", "spřátelená", "mírumilovná", "nápomocná", "podporující"],
            "Nepřátelská": ["nepřátelská", "protivnická", "nepřátelství", "válčící", "agresivní", "útočná"],
            "Neutrální": ["neutrální", "nestranná", "nezaujatá", "nezúčastněná", "nezapojená"],
            "Obchodní": ["obchodní", "kupecká", "tržní", "ekonomická", "finanční", "výdělečná"],
            "Vojenská": ["vojenská", "bojová", "válečná", "armádní", "bitevní", "útočná", "obranná"],
            "Náboženská": ["náboženská", "církevní", "kultovní", "duchovní", "svatá", "posvátná", "božská"]
        }
        
        self.event_tags = {
            "Souboj": ["souboj", "boj", "bitva", "střet", "konflikt", "válka", "útok", "obrana"],
            "Dialog": ["dialog", "rozhovor", "konverzace", "diskuze", "debata", "hovor", "povídání"],
            "Objev": ["objev", "nález", "objevení", "nalezení", "odhalení", "zjištění", "poznání"],
            "Quest": ["quest", "úkol", "mise", "zakázka", "žádost", "prosba", "zadání"],
            "Důležitá": ["důležitá", "klíčová", "významná", "zásadní", "přelomová", "rozhodující"],
            "Vedlejší": ["vedlejší", "nepodstatná", "okrajová", "doplňková", "méně důležitá"]
        }

    def categorize_npc(self, text: str, npc_name: str) -> List[str]:
        """
        Kategorizuje NPC a přiřadí mu tagy na základě textu.

        Args:
            text: Text, na základě kterého se má NPC kategorizovat.
            npc_name: Jméno NPC.

        Returns:
            Seznam tagů pro NPC.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu tagů
        tags = []
        
        # Hledání vět, které zmiňují NPC
        npc_sentences = []
        for sent in doc.sents:
            if npc_name.lower() in sent.text.lower():
                npc_sentences.append(sent)
        
        # Procházení tagů a hledání odpovídajících klíčových slov v textu
        for tag, keywords in self.npc_tags.items():
            # Kontrola, zda některé z klíčových slov je v textu
            for keyword in keywords:
                # Hledání v celém textu
                if re.search(r"(?i)" + re.escape(keyword), text):
                    # Kontrola, zda klíčové slovo je spojeno s NPC
                    for sent in npc_sentences:
                        if keyword.lower() in sent.text.lower():
                            tags.append(tag)
                            break
                    else:
                        # Hledání v blízkosti jména NPC
                        pattern = r"(?i)" + re.escape(npc_name) + r"(?:[^.!?]*\s+" + re.escape(keyword) + r"|" + re.escape(keyword) + r"\s+[^.!?]*" + re.escape(npc_name) + r")"
                        if re.search(pattern, text):
                            tags.append(tag)
                    
                    # Pokud jsme našli tag, přejdeme na další
                    if tag in tags:
                        break
        
        # Odstranění duplicit
        return list(set(tags))

    def categorize_location(self, text: str, location_name: str) -> List[str]:
        """
        Kategorizuje lokaci a přiřadí jí tagy na základě textu.

        Args:
            text: Text, na základě kterého se má lokace kategorizovat.
            location_name: Název lokace.

        Returns:
            Seznam tagů pro lokaci.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu tagů
        tags = []
        
        # Hledání vět, které zmiňují lokaci
        location_sentences = []
        for sent in doc.sents:
            if location_name.lower() in sent.text.lower():
                location_sentences.append(sent)
        
        # Procházení tagů a hledání odpovídajících klíčových slov v textu
        for tag, keywords in self.location_tags.items():
            # Kontrola, zda některé z klíčových slov je v textu
            for keyword in keywords:
                # Hledání v celém textu
                if re.search(r"(?i)" + re.escape(keyword), text):
                    # Kontrola, zda klíčové slovo je spojeno s lokací
                    for sent in location_sentences:
                        if keyword.lower() in sent.text.lower():
                            tags.append(tag)
                            break
                    else:
                        # Hledání v blízkosti názvu lokace
                        pattern = r"(?i)" + re.escape(location_name) + r"(?:[^.!?]*\s+" + re.escape(keyword) + r"|" + re.escape(keyword) + r"\s+[^.!?]*" + re.escape(location_name) + r")"
                        if re.search(pattern, text):
                            tags.append(tag)
                    
                    # Pokud jsme našli tag, přejdeme na další
                    if tag in tags:
                        break
        
        # Odstranění duplicit
        return list(set(tags))

    def categorize_monster(self, text: str, monster_name: str) -> List[str]:
        """
        Kategorizuje příšeru a přiřadí jí tagy na základě textu.

        Args:
            text: Text, na základě kterého se má příšera kategorizovat.
            monster_name: Název příšery.

        Returns:
            Seznam tagů pro příšeru.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu tagů
        tags = []
        
        # Hledání vět, které zmiňují příšeru
        monster_sentences = []
        for sent in doc.sents:
            if monster_name.lower() in sent.text.lower():
                monster_sentences.append(sent)
        
        # Procházení tagů a hledání odpovídajících klíčových slov v textu
        for tag, keywords in self.monster_tags.items():
            # Kontrola, zda některé z klíčových slov je v textu
            for keyword in keywords:
                # Hledání v celém textu
                if re.search(r"(?i)" + re.escape(keyword), text):
                    # Kontrola, zda klíčové slovo je spojeno s příšerou
                    for sent in monster_sentences:
                        if keyword.lower() in sent.text.lower():
                            tags.append(tag)
                            break
                    else:
                        # Hledání v blízkosti názvu příšery
                        pattern = r"(?i)" + re.escape(monster_name) + r"(?:[^.!?]*\s+" + re.escape(keyword) + r"|" + re.escape(keyword) + r"\s+[^.!?]*" + re.escape(monster_name) + r")"
                        if re.search(pattern, text):
                            tags.append(tag)
                    
                    # Pokud jsme našli tag, přejdeme na další
                    if tag in tags:
                        break
        
        # Odstranění duplicit
        return list(set(tags))

    def categorize_item(self, text: str, item_name: str) -> List[str]:
        """
        Kategorizuje předmět a přiřadí mu tagy na základě textu.

        Args:
            text: Text, na základě kterého se má předmět kategorizovat.
            item_name: Název předmětu.

        Returns:
            Seznam tagů pro předmět.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu tagů
        tags = []
        
        # Hledání vět, které zmiňují předmět
        item_sentences = []
        for sent in doc.sents:
            if item_name.lower() in sent.text.lower():
                item_sentences.append(sent)
        
        # Procházení tagů a hledání odpovídajících klíčových slov v textu
        for tag, keywords in self.item_tags.items():
            # Kontrola, zda některé z klíčových slov je v textu
            for keyword in keywords:
                # Hledání v celém textu
                if re.search(r"(?i)" + re.escape(keyword), text):
                    # Kontrola, zda klíčové slovo je spojeno s předmětem
                    for sent in item_sentences:
                        if keyword.lower() in sent.text.lower():
                            tags.append(tag)
                            break
                    else:
                        # Hledání v blízkosti názvu předmětu
                        pattern = r"(?i)" + re.escape(item_name) + r"(?:[^.!?]*\s+" + re.escape(keyword) + r"|" + re.escape(keyword) + r"\s+[^.!?]*" + re.escape(item_name) + r")"
                        if re.search(pattern, text):
                            tags.append(tag)
                    
                    # Pokud jsme našli tag, přejdeme na další
                    if tag in tags:
                        break
        
        # Odstranění duplicit
        return list(set(tags))

    def categorize_quest(self, text: str, quest_name: str) -> List[str]:
        """
        Kategorizuje quest a přiřadí mu tagy na základě textu.

        Args:
            text: Text, na základě kterého se má quest kategorizovat.
            quest_name: Název questu.

        Returns:
            Seznam tagů pro quest.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu tagů
        tags = []
        
        # Hledání vět, které zmiňují quest
        quest_sentences = []
        for sent in doc.sents:
            if quest_name.lower() in sent.text.lower():
                quest_sentences.append(sent)
        
        # Procházení tagů a hledání odpovídajících klíčových slov v textu
        for tag, keywords in self.quest_tags.items():
            # Kontrola, zda některé z klíčových slov je v textu
            for keyword in keywords:
                # Hledání v celém textu
                if re.search(r"(?i)" + re.escape(keyword), text):
                    # Kontrola, zda klíčové slovo je spojeno s questem
                    for sent in quest_sentences:
                        if keyword.lower() in sent.text.lower():
                            tags.append(tag)
                            break
                    else:
                        # Hledání v blízkosti názvu questu
                        pattern = r"(?i)" + re.escape(quest_name) + r"(?:[^.!?]*\s+" + re.escape(keyword) + r"|" + re.escape(keyword) + r"\s+[^.!?]*" + re.escape(quest_name) + r")"
                        if re.search(pattern, text):
                            tags.append(tag)
                    
                    # Pokud jsme našli tag, přejdeme na další
                    if tag in tags:
                        break
        
        # Odstranění duplicit
        return list(set(tags))

    def categorize_faction(self, text: str, faction_name: str) -> List[str]:
        """
        Kategorizuje frakci a přiřadí jí tagy na základě textu.

        Args:
            text: Text, na základě kterého se má frakce kategorizovat.
            faction_name: Název frakce.

        Returns:
            Seznam tagů pro frakci.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu tagů
        tags = []
        
        # Hledání vět, které zmiňují frakci
        faction_sentences = []
        for sent in doc.sents:
            if faction_name.lower() in sent.text.lower():
                faction_sentences.append(sent)
        
        # Procházení tagů a hledání odpovídajících klíčových slov v textu
        for tag, keywords in self.faction_tags.items():
            # Kontrola, zda některé z klíčových slov je v textu
            for keyword in keywords:
                # Hledání v celém textu
                if re.search(r"(?i)" + re.escape(keyword), text):
                    # Kontrola, zda klíčové slovo je spojeno s frakcí
                    for sent in faction_sentences:
                        if keyword.lower() in sent.text.lower():
                            tags.append(tag)
                            break
                    else:
                        # Hledání v blízkosti názvu frakce
                        pattern = r"(?i)" + re.escape(faction_name) + r"(?:[^.!?]*\s+" + re.escape(keyword) + r"|" + re.escape(keyword) + r"\s+[^.!?]*" + re.escape(faction_name) + r")"
                        if re.search(pattern, text):
                            tags.append(tag)
                    
                    # Pokud jsme našli tag, přejdeme na další
                    if tag in tags:
                        break
        
        # Odstranění duplicit
        return list(set(tags))

    def categorize_event(self, text: str, event_name: str) -> List[str]:
        """
        Kategorizuje událost a přiřadí jí tagy na základě textu.

        Args:
            text: Text, na základě kterého se má událost kategorizovat.
            event_name: Název události.

        Returns:
            Seznam tagů pro událost.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu tagů
        tags = []
        
        # Hledání vět, které zmiňují událost
        event_sentences = []
        for sent in doc.sents:
            if event_name.lower() in sent.text.lower():
                event_sentences.append(sent)
        
        # Procházení tagů a hledání odpovídajících klíčových slov v textu
        for tag, keywords in self.event_tags.items():
            # Kontrola, zda některé z klíčových slov je v textu
            for keyword in keywords:
                # Hledání v celém textu
                if re.search(r"(?i)" + re.escape(keyword), text):
                    # Kontrola, zda klíčové slovo je spojeno s událostí
                    for sent in event_sentences:
                        if keyword.lower() in sent.text.lower():
                            tags.append(tag)
                            break
                    else:
                        # Hledání v blízkosti názvu události
                        pattern = r"(?i)" + re.escape(event_name) + r"(?:[^.!?]*\s+" + re.escape(keyword) + r"|" + re.escape(keyword) + r"\s+[^.!?]*" + re.escape(event_name) + r")"
                        if re.search(pattern, text):
                            tags.append(tag)
                    
                    # Pokud jsme našli tag, přejdeme na další
                    if tag in tags:
                        break
        
        # Odstranění duplicit
        return list(set(tags))

    def categorize_entity(self, text: str, entity_name: str, entity_type: EntityType) -> List[str]:
        """
        Kategorizuje entitu a přiřadí jí tagy na základě textu.

        Args:
            text: Text, na základě kterého se má entita kategorizovat.
            entity_name: Název entity.
            entity_type: Typ entity.

        Returns:
            Seznam tagů pro entitu.
        """
        if entity_type == EntityType.NPC:
            return self.categorize_npc(text, entity_name)
        elif entity_type == EntityType.LOCATION:
            return self.categorize_location(text, entity_name)
        elif entity_type == EntityType.MONSTER:
            return self.categorize_monster(text, entity_name)
        elif entity_type == EntityType.ITEM:
            return self.categorize_item(text, entity_name)
        elif entity_type == EntityType.QUEST:
            return self.categorize_quest(text, entity_name)
        elif entity_type == EntityType.FACTION:
            return self.categorize_faction(text, entity_name)
        elif entity_type == EntityType.EVENT:
            return self.categorize_event(text, entity_name)
        else:
            return []
