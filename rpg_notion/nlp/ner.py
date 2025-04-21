"""
Modul pro rozpoznávání pojmenovaných entit (NER) v textu.
"""
import logging
from typing import Dict, List, Optional, Set, Tuple, Union

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span

from rpg_notion.config.settings import NLP_MODELS_DIR, SPACY_MODEL
from rpg_notion.models.entities import EntityType

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Třída pro extrakci entit z textu pomocí NER.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Inicializace extraktoru entit.

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
        
        # Přidání vlastních komponent do pipeline
        self._add_custom_components()

    def _add_custom_components(self) -> None:
        """
        Přidá vlastní komponenty do pipeline spaCy.
        """
        # Přidání vlastního rozpoznávání entit pro fantasy RPG doménu
        if "fantasy_ner" not in self.nlp.pipe_names:
            fantasy_ner = self._create_fantasy_ner()
            self.nlp.add_pipe("fantasy_ner", after="ner")
            logger.info("Přidána vlastní komponenta pro rozpoznávání fantasy entit.")

    def _create_fantasy_ner(self) -> Language.component:
        """
        Vytvoří vlastní komponentu pro rozpoznávání fantasy entit.

        Returns:
            Komponenta pro pipeline spaCy.
        """
        # Definice vzorů pro rozpoznávání fantasy entit
        location_patterns = [
            "hrad", "pevnost", "věž", "jeskyně", "dungeon", "les", "hora", "město", "vesnice",
            "chrám", "svatyně", "ruiny", "zřícenina", "hostinec", "taverna", "krčma", "palác",
            "tvrz", "ostrov", "údolí", "poušť", "bažina", "močál", "řeka", "jezero", "moře",
            "oceán", "propast", "rokle", "průsmyk", "podzemí", "kobka", "žalář", "vězení"
        ]
        
        npc_patterns = [
            "král", "královna", "princ", "princezna", "rytíř", "čaroděj", "čarodějka", "kouzelník",
            "kouzelnice", "mág", "čarodějnice", "alchymista", "obchodník", "hostinský", "kovář",
            "zbrojíř", "lovec", "hraničář", "druid", "bard", "zloděj", "vrah", "vůdce", "náčelník",
            "šaman", "kněz", "kněžka", "mnich", "válečník", "bojovník", "paladin", "šlechtic",
            "šlechtična", "lord", "lady", "baron", "baronka", "hrabě", "hraběnka", "vévoda", "vévodkyně"
        ]
        
        monster_patterns = [
            "drak", "goblin", "skřet", "ork", "troll", "obr", "démon", "nemrtvý", "zombie", "kostlivec",
            "upír", "vlkodlak", "medvěd", "vlk", "krysa", "netopýr", "pavouk", "had", "bazilišek",
            "gryf", "hydra", "chiméra", "mantikora", "minotaur", "kyklop", "harpyje", "gorgona",
            "golem", "elementál", "duch", "přízrak", "stín", "lich", "bludička", "sukuba", "inkubus"
        ]
        
        item_patterns = [
            "meč", "dýka", "sekera", "kladivo", "palice", "hůl", "luk", "kuše", "šíp", "kopí",
            "štít", "brnění", "přilba", "rukavice", "boty", "plášť", "amulet", "prsten", "náhrdelník",
            "náramek", "lektvar", "svitek", "kniha", "grimoár", "mapa", "klíč", "truhla", "poklad",
            "zlato", "stříbro", "drahokam", "rubín", "safír", "diamant", "smaragd", "artefakt"
        ]
        
        # Vytvoření komponenty
        def fantasy_ner(doc: Doc) -> Doc:
            """
            Vlastní komponenta pro rozpoznávání fantasy entit.

            Args:
                doc: Dokument spaCy.

            Returns:
                Dokument s rozpoznanými entitami.
            """
            # Pomocná funkce pro kontrolu, zda token odpovídá vzoru
            def token_matches_pattern(token, patterns: List[str]) -> bool:
                """
                Kontroluje, zda token odpovídá některému ze vzorů.

                Args:
                    token: Token spaCy.
                    patterns: Seznam vzorů.

                Returns:
                    True, pokud token odpovídá některému ze vzorů, jinak False.
                """
                return token.text.lower() in patterns or token.lemma_.lower() in patterns
            
            # Procházení tokenů a hledání vzorů
            entities = []
            i = 0
            while i < len(doc):
                # Kontrola, zda token odpovídá některému ze vzorů
                if token_matches_pattern(doc[i], location_patterns):
                    # Hledání celé fráze (např. "temný les", "opuštěná věž")
                    start = i
                    end = i + 1
                    # Hledání přídavných jmen před tokenem
                    j = i - 1
                    while j >= 0 and (doc[j].pos_ == "ADJ" or doc[j].pos_ == "PROPN"):
                        start = j
                        j -= 1
                    # Hledání podstatných jmen a přídavných jmen za tokenem
                    j = i + 1
                    while j < len(doc) and (doc[j].pos_ == "NOUN" or doc[j].pos_ == "ADJ" or doc[j].pos_ == "PROPN"):
                        end = j + 1
                        j += 1
                    # Vytvoření entity
                    entities.append((start, end, "LOCATION"))
                    i = end
                elif token_matches_pattern(doc[i], npc_patterns):
                    # Podobný postup pro NPC
                    start = i
                    end = i + 1
                    j = i - 1
                    while j >= 0 and (doc[j].pos_ == "ADJ" or doc[j].pos_ == "PROPN"):
                        start = j
                        j -= 1
                    j = i + 1
                    while j < len(doc) and (doc[j].pos_ == "NOUN" or doc[j].pos_ == "ADJ" or doc[j].pos_ == "PROPN"):
                        end = j + 1
                        j += 1
                    entities.append((start, end, "PERSON"))
                    i = end
                elif token_matches_pattern(doc[i], monster_patterns):
                    # Podobný postup pro příšery
                    start = i
                    end = i + 1
                    j = i - 1
                    while j >= 0 and (doc[j].pos_ == "ADJ" or doc[j].pos_ == "PROPN"):
                        start = j
                        j -= 1
                    j = i + 1
                    while j < len(doc) and (doc[j].pos_ == "NOUN" or doc[j].pos_ == "ADJ" or doc[j].pos_ == "PROPN"):
                        end = j + 1
                        j += 1
                    entities.append((start, end, "MONSTER"))
                    i = end
                elif token_matches_pattern(doc[i], item_patterns):
                    # Podobný postup pro předměty
                    start = i
                    end = i + 1
                    j = i - 1
                    while j >= 0 and (doc[j].pos_ == "ADJ" or doc[j].pos_ == "PROPN"):
                        start = j
                        j -= 1
                    j = i + 1
                    while j < len(doc) and (doc[j].pos_ == "NOUN" or doc[j].pos_ == "ADJ" or doc[j].pos_ == "PROPN"):
                        end = j + 1
                        j += 1
                    entities.append((start, end, "ITEM"))
                    i = end
                else:
                    i += 1
            
            # Přidání entit do dokumentu
            for start, end, label in entities:
                # Kontrola, zda se entity nepřekrývají
                if not any(start < e.end and end > e.start for e in doc.ents):
                    span = Span(doc, start, end, label=label)
                    doc.ents = list(doc.ents) + [span]
            
            return doc
        
        return fantasy_ner

    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Extrahuje entity z textu.

        Args:
            text: Text, ze kterého se mají extrahovat entity.

        Returns:
            Slovník s extrahovanými entitami podle typu.
        """
        doc = self.nlp(text)
        
        # Inicializace slovníku pro entity
        entities = {
            EntityType.NPC.value: [],
            EntityType.LOCATION.value: [],
            EntityType.MONSTER.value: [],
            EntityType.ITEM.value: [],
            EntityType.EVENT.value: [],
            EntityType.FACTION.value: [],
        }
        
        # Mapování typů entit ze spaCy na naše typy
        entity_type_mapping = {
            "PERSON": EntityType.NPC.value,
            "LOCATION": EntityType.LOCATION.value,
            "GPE": EntityType.LOCATION.value,
            "FAC": EntityType.LOCATION.value,
            "MONSTER": EntityType.MONSTER.value,
            "ITEM": EntityType.ITEM.value,
            "ORG": EntityType.FACTION.value,
            "EVENT": EntityType.EVENT.value,
        }
        
        # Extrakce entit
        for ent in doc.ents:
            entity_type = entity_type_mapping.get(ent.label_, None)
            if entity_type:
                entity = {
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "label": ent.label_,
                }
                entities[entity_type].append(entity)
        
        return entities

    def extract_entity_attributes(self, text: str, entity_text: str) -> Dict[str, str]:
        """
        Extrahuje atributy entity z textu.

        Args:
            text: Text, ze kterého se mají extrahovat atributy.
            entity_text: Text entity, pro kterou se mají extrahovat atributy.

        Returns:
            Slovník s extrahovanými atributy.
        """
        doc = self.nlp(text)
        
        # Inicializace slovníku pro atributy
        attributes = {
            "description": "",
            "status": "",
            "location": "",
            "relationships": "",
        }
        
        # Hledání zmínek o entitě v textu
        entity_mentions = []
        for sent in doc.sents:
            if entity_text.lower() in sent.text.lower():
                entity_mentions.append(sent)
        
        # Extrakce atributů z vět, které zmiňují entitu
        for sent in entity_mentions:
            # Hledání popisů
            if any(token.lemma_ in ["být", "vypadat", "mít"] for token in sent):
                # Věta pravděpodobně obsahuje popis
                if not attributes["description"]:
                    attributes["description"] = sent.text
                else:
                    attributes["description"] += " " + sent.text
            
            # Hledání stavu
            status_keywords = ["živý", "mrtvý", "zraněný", "nemocný", "zdravý", "unavený", "odpočatý"]
            if any(keyword in sent.text.lower() for keyword in status_keywords):
                if not attributes["status"]:
                    attributes["status"] = sent.text
                else:
                    attributes["status"] += " " + sent.text
            
            # Hledání lokace
            location_verbs = ["nacházet", "žít", "bydlet", "přebývat", "pobývat"]
            if any(token.lemma_ in location_verbs for token in sent):
                for ent in sent.ents:
                    if ent.label_ in ["LOCATION", "GPE", "FAC"]:
                        if not attributes["location"]:
                            attributes["location"] = ent.text
                        else:
                            attributes["location"] += ", " + ent.text
            
            # Hledání vztahů
            relationship_verbs = ["znát", "přátelit", "milovat", "nenávidět", "spolupracovat", "bojovat"]
            if any(token.lemma_ in relationship_verbs for token in sent):
                for ent in sent.ents:
                    if ent.label_ in ["PERSON", "ORG"]:
                        if ent.text.lower() != entity_text.lower():
                            if not attributes["relationships"]:
                                attributes["relationships"] = ent.text
                            else:
                                attributes["relationships"] += ", " + ent.text
        
        return attributes

    def extract_relationships(self, text: str) -> List[Dict[str, str]]:
        """
        Extrahuje vztahy mezi entitami z textu.

        Args:
            text: Text, ze kterého se mají extrahovat vztahy.

        Returns:
            Seznam slovníků s extrahovanými vztahy.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu pro vztahy
        relationships = []
        
        # Extrakce vztahů z vět
        for sent in doc.sents:
            # Hledání entit ve větě
            entities = list(sent.ents)
            if len(entities) >= 2:
                # Hledání sloves, která mohou indikovat vztah
                relationship_verbs = ["znát", "přátelit", "milovat", "nenávidět", "spolupracovat", "bojovat",
                                     "mluvit", "setkat", "pomáhat", "útočit", "bránit", "dát", "vzít"]
                
                for token in sent:
                    if token.pos_ == "VERB" and token.lemma_ in relationship_verbs:
                        # Hledání subjektu a objektu
                        subject = None
                        obj = None
                        
                        for child in token.children:
                            if child.dep_ == "nsubj" and child.head == token:
                                # Hledání entity, která obsahuje subjekt
                                for ent in entities:
                                    if child.i >= ent.start and child.i < ent.end:
                                        subject = ent
                                        break
                            
                            if child.dep_ in ["dobj", "pobj", "iobj"] and child.head == token:
                                # Hledání entity, která obsahuje objekt
                                for ent in entities:
                                    if child.i >= ent.start and child.i < ent.end:
                                        obj = ent
                                        break
                        
                        # Pokud jsme našli subjekt a objekt, přidáme vztah
                        if subject and obj and subject != obj:
                            relationship = {
                                "subject": subject.text,
                                "subject_type": subject.label_,
                                "predicate": token.lemma_,
                                "object": obj.text,
                                "object_type": obj.label_,
                                "sentence": sent.text,
                            }
                            relationships.append(relationship)
        
        return relationships

    def extract_state_changes(self, text: str, entity_text: str) -> List[Dict[str, str]]:
        """
        Extrahuje změny stavu entity z textu.

        Args:
            text: Text, ze kterého se mají extrahovat změny stavu.
            entity_text: Text entity, pro kterou se mají extrahovat změny stavu.

        Returns:
            Seznam slovníků s extrahovanými změnami stavu.
        """
        doc = self.nlp(text)
        
        # Inicializace seznamu pro změny stavu
        state_changes = []
        
        # Slovník sloves, která mohou indikovat změnu stavu
        state_change_verbs = {
            "zemřít": "Mrtvý",
            "zabít": "Mrtvý",
            "zranit": "Zraněný",
            "uzdravit": "Živý",
            "onemocnět": "Nemocný",
            "vyléčit": "Živý",
            "unavit": "Unavený",
            "odpočinout": "Odpočatý",
            "změnit": "Změněný",
            "stát se": "Změněný",
            "přesunout": "Přesunutý",
            "odejít": "Přesunutý",
            "přijít": "Přesunutý",
            "získat": "Získal",
            "ztratit": "Ztratil",
            "najít": "Našel",
            "objevit": "Objevil",
        }
        
        # Extrakce změn stavu z vět
        for sent in doc.sents:
            if entity_text.lower() in sent.text.lower():
                # Hledání sloves, která mohou indikovat změnu stavu
                for token in sent:
                    if token.pos_ == "VERB" and token.lemma_ in state_change_verbs:
                        # Kontrola, zda se sloveso vztahuje k entitě
                        for child in token.children:
                            if child.dep_ == "nsubj" and entity_text.lower() in child.text.lower():
                                state_change = {
                                    "entity": entity_text,
                                    "verb": token.lemma_,
                                    "new_state": state_change_verbs[token.lemma_],
                                    "sentence": sent.text,
                                }
                                state_changes.append(state_change)
                                break
                            elif child.dep_ == "dobj" and entity_text.lower() in child.text.lower():
                                state_change = {
                                    "entity": entity_text,
                                    "verb": token.lemma_,
                                    "new_state": state_change_verbs[token.lemma_],
                                    "sentence": sent.text,
                                }
                                state_changes.append(state_change)
                                break
        
        return state_changes
