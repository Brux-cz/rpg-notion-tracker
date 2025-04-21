"""
Modul pro extrakci atributů entit z textu.
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


class AttributeExtractor:
    """
    Třída pro extrakci atributů entit z textu.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Inicializace extraktoru atributů.

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

    def extract_npc_attributes(self, text: str, npc_name: str) -> Dict[str, str]:
        """
        Extrahuje atributy NPC z textu.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            npc_name: Jméno NPC, pro které se mají extrahovat atributy.

        Returns:
            Slovník s extrahovanými atributy.
        """
        doc = self.nlp(text)
        
        # Inicializace slovníku pro atributy
        attributes = {
            "description": "",
            "status": "Živý",  # Výchozí hodnota
            "occupation": "",
            "location": "",
            "history": "",
        }
        
        # Hledání vět, které zmiňují NPC
        npc_sentences = []
        for sent in doc.sents:
            if npc_name.lower() in sent.text.lower():
                npc_sentences.append(sent)
        
        # Extrakce popisu
        description_patterns = [
            r"(?i)" + re.escape(npc_name) + r"(?:\s+je|\s+byl|\s+byla|\s+vypadá|\s+má)\s+([^.!?]+)[.!?]",
            r"(?i)(?:popis|vzhled|charakteristika)\s+(?:postavy\s+)?" + re.escape(npc_name) + r"\s*:\s*([^.!?]+)[.!?]",
        ]
        
        for pattern in description_patterns:
            matches = re.findall(pattern, text)
            if matches:
                attributes["description"] = " ".join(matches)
                break
        
        # Pokud nebyl nalezen popis pomocí regulárních výrazů, zkusíme extrahovat z vět
        if not attributes["description"]:
            for sent in npc_sentences:
                if any(token.lemma_ in ["být", "vypadat", "mít"] for token in sent):
                    attributes["description"] = sent.text
                    break
        
        # Extrakce stavu
        status_patterns = {
            "Živý": [r"(?i)" + re.escape(npc_name) + r"(?:\s+je|\s+zůstává)\s+(?:naživu|živý|zdravý)"],
            "Mrtvý": [r"(?i)" + re.escape(npc_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:mrtvý|mrtvá|zabit|zabita|zemřel|zemřela)"],
            "Zraněný": [r"(?i)" + re.escape(npc_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:zraněn|zraněna|zraněný|zraněná|poraněn|poraněna)"],
        }
        
        for status, patterns in status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    attributes["status"] = status
                    break
        
        # Extrakce povolání/role
        occupation_patterns = [
            r"(?i)" + re.escape(npc_name) + r"(?:\s+je|\s+byl|\s+byla|\s+pracuje\s+jako)\s+([^,.!?]+(?:čaroděj|kouzelník|válečník|zloděj|hraničář|bard|mnich|paladin|druid|alchymista|obchodník|kovář|hostinský|král|královna|princ|princezna|rytíř|šlechtic|šlechtična|lord|lady|baron|baronka|hrabě|hraběnka|vévoda|vévodkyně|kněz|kněžka|šaman|vůdce|náčelník)[^.!?]*)[.!?]",
            r"(?i)(?:povolání|role|zaměstnání|profese)\s+(?:postavy\s+)?" + re.escape(npc_name) + r"\s*:\s*([^.!?]+)[.!?]",
        ]
        
        for pattern in occupation_patterns:
            matches = re.findall(pattern, text)
            if matches:
                attributes["occupation"] = matches[0].strip()
                break
        
        # Extrakce lokace
        location_patterns = [
            r"(?i)" + re.escape(npc_name) + r"(?:\s+se\s+nachází|\s+žije|\s+bydlí|\s+přebývá|\s+pobývá)\s+v\s+([^.!?]+)[.!?]",
            r"(?i)" + re.escape(npc_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:spatřen|spatřena|viděn|viděna)\s+v\s+([^.!?]+)[.!?]",
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                attributes["location"] = matches[0].strip()
                break
        
        # Extrakce historie
        history_patterns = [
            r"(?i)(?:historie|minulost|příběh)\s+(?:postavy\s+)?" + re.escape(npc_name) + r"\s*:\s*([^.!?]+(?:[.!?][^.!?]+){0,5})[.!?]",
            r"(?i)" + re.escape(npc_name) + r"(?:\s+dříve|\s+předtím|\s+kdysi)\s+([^.!?]+(?:[.!?][^.!?]+){0,2})[.!?]",
        ]
        
        for pattern in history_patterns:
            matches = re.findall(pattern, text)
            if matches:
                attributes["history"] = matches[0].strip()
                break
        
        return attributes

    def extract_location_attributes(self, text: str, location_name: str) -> Dict[str, str]:
        """
        Extrahuje atributy lokace z textu.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            location_name: Název lokace, pro kterou se mají extrahovat atributy.

        Returns:
            Slovník s extrahovanými atributy.
        """
        doc = self.nlp(text)
        
        # Inicializace slovníku pro atributy
        attributes = {
            "location_type": "",
            "hierarchy": "",
            "description": "",
            "status": "Bezpečné",  # Výchozí hodnota
        }
        
        # Hledání vět, které zmiňují lokaci
        location_sentences = []
        for sent in doc.sents:
            if location_name.lower() in sent.text.lower():
                location_sentences.append(sent)
        
        # Extrakce typu lokace
        location_type_patterns = {
            "Město": [r"(?i)(?:město|metropole|velkoměsto)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+bylo)\s+(?:město|metropole|velkoměsto)"],
            "Vesnice": [r"(?i)(?:vesnice|vesnička|osada)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+byla)\s+(?:vesnice|vesnička|osada)"],
            "Dungeon": [r"(?i)(?:dungeon|kobka|žalář|vězení)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:dungeon|kobka|žalář|vězení)"],
            "Les": [r"(?i)(?:les|hvozd|prales)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+byl)\s+(?:les|hvozd|prales)"],
            "Hora": [r"(?i)(?:hora|pohoří|vrchol)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+byla)\s+(?:hora|pohoří|vrchol)"],
            "Jeskyně": [r"(?i)(?:jeskyně|sluj|doupě)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+byla)\s+(?:jeskyně|sluj|doupě)"],
            "Hrad": [r"(?i)(?:hrad|pevnost|tvrz)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+byl)\s+(?:hrad|pevnost|tvrz)"],
            "Chrám": [r"(?i)(?:chrám|svatyně|katedrála)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:chrám|svatyně|katedrála)"],
            "Ruiny": [r"(?i)(?:ruiny|zřícenina|trosky)\s+" + re.escape(location_name), r"(?i)" + re.escape(location_name) + r"(?:\s+jsou|\s+je|\s+byla)\s+(?:ruiny|zřícenina|trosky)"],
        }
        
        for loc_type, patterns in location_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    attributes["location_type"] = loc_type
                    break
            if attributes["location_type"]:
                break
        
        # Extrakce hierarchie
        hierarchy_patterns = [
            r"(?i)" + re.escape(location_name) + r"(?:\s+se\s+nachází|\s+leží|\s+je)\s+v\s+([^.!?]+)[.!?]",
            r"(?i)(?:oblast|region|země|kontinent)\s+(?:kolem|obsahující)\s+" + re.escape(location_name) + r"\s+(?:je|se\s+nazývá)\s+([^.!?]+)[.!?]",
        ]
        
        for pattern in hierarchy_patterns:
            matches = re.findall(pattern, text)
            if matches:
                attributes["hierarchy"] = matches[0].strip()
                break
        
        # Extrakce popisu
        description_patterns = [
            r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+bylo|\s+byla|\s+vypadá)\s+([^.!?]+)[.!?]",
            r"(?i)(?:popis|vzhled|charakteristika)\s+(?:lokace\s+)?" + re.escape(location_name) + r"\s*:\s*([^.!?]+)[.!?]",
        ]
        
        for pattern in description_patterns:
            matches = re.findall(pattern, text)
            if matches:
                attributes["description"] = " ".join(matches)
                break
        
        # Pokud nebyl nalezen popis pomocí regulárních výrazů, zkusíme extrahovat z vět
        if not attributes["description"]:
            for sent in location_sentences:
                if any(token.lemma_ in ["být", "vypadat", "mít"] for token in sent):
                    attributes["description"] = sent.text
                    break
        
        # Extrakce stavu
        status_patterns = {
            "Prosperující": [r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+bylo|\s+byla)\s+(?:prosperující|bohaté|bohatá|úspěšné|úspěšná|vzkvétající)"],
            "V úpadku": [r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+bylo|\s+byla)\s+(?:v\s+úpadku|upadající|chudé|chudá|zchátralé|zchátralá)"],
            "Zničené": [r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+bylo|\s+byla)\s+(?:zničené|zničená|zničeno|zpustošené|zpustošená|zpustošeno)"],
            "Opuštěné": [r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+bylo|\s+byla)\s+(?:opuštěné|opuštěná|opuštěno|prázdné|prázdná|prázdno)"],
            "Nebezpečné": [r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+bylo|\s+byla)\s+(?:nebezpečné|nebezpečná|nebezpečno|hrozivé|hrozivá|hrozivo)"],
            "Bezpečné": [r"(?i)" + re.escape(location_name) + r"(?:\s+je|\s+bylo|\s+byla)\s+(?:bezpečné|bezpečná|bezpečno|klidné|klidná|klidno)"],
        }
        
        for status, patterns in status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    attributes["status"] = status
                    break
            if attributes["status"] != "Bezpečné":  # Pokud jsme našli jiný stav než výchozí
                break
        
        return attributes

    def extract_monster_attributes(self, text: str, monster_name: str) -> Dict[str, str]:
        """
        Extrahuje atributy příšery z textu.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            monster_name: Název příšery, pro kterou se mají extrahovat atributy.

        Returns:
            Slovník s extrahovanými atributy.
        """
        doc = self.nlp(text)
        
        # Inicializace slovníku pro atributy
        attributes = {
            "description": "",
            "status": "Živá",  # Výchozí hodnota
            "combat_history": "",
            "weaknesses_strengths": "",
        }
        
        # Hledání vět, které zmiňují příšeru
        monster_sentences = []
        for sent in doc.sents:
            if monster_name.lower() in sent.text.lower():
                monster_sentences.append(sent)
        
        # Extrakce popisu
        description_patterns = [
            r"(?i)" + re.escape(monster_name) + r"(?:\s+je|\s+byl|\s+byla|\s+vypadá|\s+má)\s+([^.!?]+)[.!?]",
            r"(?i)(?:popis|vzhled|charakteristika)\s+(?:příšery\s+)?" + re.escape(monster_name) + r"\s*:\s*([^.!?]+)[.!?]",
        ]
        
        for pattern in description_patterns:
            matches = re.findall(pattern, text)
            if matches:
                attributes["description"] = " ".join(matches)
                break
        
        # Pokud nebyl nalezen popis pomocí regulárních výrazů, zkusíme extrahovat z vět
        if not attributes["description"]:
            for sent in monster_sentences:
                if any(token.lemma_ in ["být", "vypadat", "mít"] for token in sent):
                    attributes["description"] = sent.text
                    break
        
        # Extrakce stavu
        status_patterns = {
            "Živá": [r"(?i)" + re.escape(monster_name) + r"(?:\s+je|\s+zůstává)\s+(?:naživu|živá|živý|zdravá|zdravý)"],
            "Mrtvá": [r"(?i)" + re.escape(monster_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:mrtvá|mrtvý|zabita|zabit|zemřela|zemřel)"],
            "Zraněná": [r"(?i)" + re.escape(monster_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:zraněná|zraněný|zraněna|zraněn|poraněná|poraněný|poraněna|poraněn)"],
        }
        
        for status, patterns in status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    attributes["status"] = status
                    break
            if attributes["status"] != "Živá":  # Pokud jsme našli jiný stav než výchozí
                break
        
        # Extrakce historie soubojů
        combat_patterns = [
            r"(?i)" + re.escape(monster_name) + r"(?:\s+bojovala|\s+bojoval|\s+zaútočila|\s+zaútočil|\s+napadla|\s+napadl)\s+([^.!?]+)[.!?]",
            r"(?i)(?:souboj|boj|střet|konfrontace)\s+s\s+" + re.escape(monster_name) + r"\s+([^.!?]+)[.!?]",
        ]
        
        combat_history = []
        for pattern in combat_patterns:
            matches = re.findall(pattern, text)
            combat_history.extend(matches)
        
        if combat_history:
            attributes["combat_history"] = " ".join(combat_history)
        
        # Extrakce slabin a silných stránek
        weakness_patterns = [
            r"(?i)(?:slabina|slabost|slabé\s+místo)\s+(?:příšery\s+)?" + re.escape(monster_name) + r"(?:\s+je|\s+byla)\s+([^.!?]+)[.!?]",
            r"(?i)" + re.escape(monster_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:slabá|slabý|zranitelná|zranitelný)\s+(?:vůči|proti)\s+([^.!?]+)[.!?]",
        ]
        
        strength_patterns = [
            r"(?i)(?:silná\s+stránka|síla|přednost)\s+(?:příšery\s+)?" + re.escape(monster_name) + r"(?:\s+je|\s+byla)\s+([^.!?]+)[.!?]",
            r"(?i)" + re.escape(monster_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:silná|silný|odolná|odolný)\s+(?:vůči|proti)\s+([^.!?]+)[.!?]",
        ]
        
        weaknesses = []
        for pattern in weakness_patterns:
            matches = re.findall(pattern, text)
            weaknesses.extend(matches)
        
        strengths = []
        for pattern in strength_patterns:
            matches = re.findall(pattern, text)
            strengths.extend(matches)
        
        if weaknesses or strengths:
            if weaknesses:
                attributes["weaknesses_strengths"] = "Slabiny: " + ", ".join(weaknesses)
            if strengths:
                if attributes["weaknesses_strengths"]:
                    attributes["weaknesses_strengths"] += "; "
                attributes["weaknesses_strengths"] += "Silné stránky: " + ", ".join(strengths)
        
        return attributes

    def extract_item_attributes(self, text: str, item_name: str) -> Dict[str, str]:
        """
        Extrahuje atributy předmětu z textu.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            item_name: Název předmětu, pro který se mají extrahovat atributy.

        Returns:
            Slovník s extrahovanými atributy.
        """
        doc = self.nlp(text)
        
        # Inicializace slovníku pro atributy
        attributes = {
            "item_type": "",
            "description": "",
            "ownership_history": "",
            "special_abilities": "",
        }
        
        # Hledání vět, které zmiňují předmět
        item_sentences = []
        for sent in doc.sents:
            if item_name.lower() in sent.text.lower():
                item_sentences.append(sent)
        
        # Extrakce typu předmětu
        item_type_patterns = {
            "Zbraň": [r"(?i)(?:zbraň|meč|dýka|sekera|kladivo|palice|hůl|luk|kuše|šíp|kopí)\s+" + re.escape(item_name), r"(?i)" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:zbraň|meč|dýka|sekera|kladivo|palice|hůl|luk|kuše|šíp|kopí)"],
            "Brnění": [r"(?i)(?:brnění|zbroj|přilba|helma|rukavice|boty|štít)\s+" + re.escape(item_name), r"(?i)" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:brnění|zbroj|přilba|helma|rukavice|boty|štít)"],
            "Artefakt": [r"(?i)(?:artefakt|relikvie|posvátný\s+předmět)\s+" + re.escape(item_name), r"(?i)" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:artefakt|relikvie|posvátný\s+předmět)"],
            "Lektvar": [r"(?i)(?:lektvar|elixír|nápoj)\s+" + re.escape(item_name), r"(?i)" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:lektvar|elixír|nápoj)"],
            "Svitek": [r"(?i)(?:svitek|pergamen)\s+" + re.escape(item_name), r"(?i)" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:svitek|pergamen)"],
            "Běžný předmět": [r"(?i)(?:předmět|věc|nástroj)\s+" + re.escape(item_name), r"(?i)" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:předmět|věc|nástroj)"],
            "Klíč": [r"(?i)(?:klíč|klíček)\s+" + re.escape(item_name), r"(?i)" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla)\s+(?:klíč|klíček)"],
        }
        
        for item_type, patterns in item_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    attributes["item_type"] = item_type
                    break
            if attributes["item_type"]:
                break
        
        # Extrakce popisu
        description_patterns = [
            r"(?i)" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla|\s+vypadá|\s+má)\s+([^.!?]+)[.!?]",
            r"(?i)(?:popis|vzhled|charakteristika)\s+(?:předmětu\s+)?" + re.escape(item_name) + r"\s*:\s*([^.!?]+)[.!?]",
        ]
        
        for pattern in description_patterns:
            matches = re.findall(pattern, text)
            if matches:
                attributes["description"] = " ".join(matches)
                break
        
        # Pokud nebyl nalezen popis pomocí regulárních výrazů, zkusíme extrahovat z vět
        if not attributes["description"]:
            for sent in item_sentences:
                if any(token.lemma_ in ["být", "vypadat", "mít"] for token in sent):
                    attributes["description"] = sent.text
                    break
        
        # Extrakce historie vlastnictví
        ownership_patterns = [
            r"(?i)" + re.escape(item_name) + r"(?:\s+patřil|\s+patřila|\s+patřilo|\s+náležel|\s+náležela|\s+náleželo)\s+([^.!?]+)[.!?]",
            r"(?i)(?:vlastník|majitel|držitel)\s+(?:předmětu\s+)?" + re.escape(item_name) + r"(?:\s+je|\s+byl|\s+byla)\s+([^.!?]+)[.!?]",
            r"(?i)" + re.escape(item_name) + r"(?:\s+byl|\s+byla|\s+bylo)\s+(?:získán|získána|získáno|nalezen|nalezena|nalezeno)\s+([^.!?]+)[.!?]",
        ]
        
        ownership_history = []
        for pattern in ownership_patterns:
            matches = re.findall(pattern, text)
            ownership_history.extend(matches)
        
        if ownership_history:
            attributes["ownership_history"] = " ".join(ownership_history)
        
        # Extrakce speciálních schopností
        ability_patterns = [
            r"(?i)" + re.escape(item_name) + r"(?:\s+má|\s+poskytuje|\s+dává|\s+umožňuje)\s+(?:schopnost|možnost|sílu)\s+([^.!?]+)[.!?]",
            r"(?i)(?:schopnost|moc|síla|vlastnost)\s+(?:předmětu\s+)?" + re.escape(item_name) + r"(?:\s+je|\s+spočívá\s+v)\s+([^.!?]+)[.!?]",
            r"(?i)" + re.escape(item_name) + r"(?:\s+může|\s+dokáže|\s+umí)\s+([^.!?]+)[.!?]",
        ]
        
        abilities = []
        for pattern in ability_patterns:
            matches = re.findall(pattern, text)
            abilities.extend(matches)
        
        if abilities:
            attributes["special_abilities"] = " ".join(abilities)
        
        return attributes
