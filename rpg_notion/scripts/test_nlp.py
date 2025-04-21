#!/usr/bin/env python
"""
Skript pro testování NLP funkcí.
"""
import argparse
import json
import logging
import sys
from pathlib import Path

# Přidání nadřazeného adresáře do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from rpg_notion.nlp.attribute_extractor import AttributeExtractor
from rpg_notion.nlp.categorizer import EntityCategorizer
from rpg_notion.nlp.entity_matcher import EntityMatcher
from rpg_notion.nlp.ner import EntityExtractor
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
    parser = argparse.ArgumentParser(description="Test NLP funkcí.")
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
        "--entity-name",
        type=str,
        help="Název entity pro extrakci atributů.",
    )
    parser.add_argument(
        "--entity-type",
        type=str,
        choices=["npc", "location", "monster", "item", "quest", "faction", "event"],
        help="Typ entity pro extrakci atributů.",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Cesta k výstupnímu souboru.",
    )
    return parser.parse_args()


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

    # Inicializace NLP komponent
    entity_extractor = EntityExtractor()
    attribute_extractor = AttributeExtractor()
    entity_categorizer = EntityCategorizer()
    entity_matcher = EntityMatcher()
    text_processor = TextProcessor(
        entity_extractor=entity_extractor,
        attribute_extractor=attribute_extractor,
        entity_categorizer=entity_categorizer,
        entity_matcher=entity_matcher,
    )

    # Zpracování textu
    logger.info("Zpracovávám text...")
    
    # Extrakce entit
    entities = entity_extractor.extract_entities(text)
    logger.info(f"Extrahováno {sum(len(entities[entity_type]) for entity_type in entities)} entit.")
    
    # Výpis entit
    for entity_type, entity_list in entities.items():
        if entity_list:
            logger.info(f"Entity typu {entity_type}:")
            for entity in entity_list:
                logger.info(f"  - {entity['text']}")
    
    # Extrakce atributů pro konkrétní entitu
    if args.entity_name and args.entity_type:
        logger.info(f"Extrahuji atributy pro entitu {args.entity_name} typu {args.entity_type}...")
        
        if args.entity_type == "npc":
            attributes = attribute_extractor.extract_npc_attributes(text, args.entity_name)
            tags = entity_categorizer.categorize_npc(text, args.entity_name)
        elif args.entity_type == "location":
            attributes = attribute_extractor.extract_location_attributes(text, args.entity_name)
            tags = entity_categorizer.categorize_location(text, args.entity_name)
        elif args.entity_type == "monster":
            attributes = attribute_extractor.extract_monster_attributes(text, args.entity_name)
            tags = entity_categorizer.categorize_monster(text, args.entity_name)
        elif args.entity_type == "item":
            attributes = attribute_extractor.extract_item_attributes(text, args.entity_name)
            tags = entity_categorizer.categorize_item(text, args.entity_name)
        elif args.entity_type == "quest":
            attributes = {}
            tags = entity_categorizer.categorize_quest(text, args.entity_name)
        elif args.entity_type == "faction":
            attributes = {}
            tags = entity_categorizer.categorize_faction(text, args.entity_name)
        elif args.entity_type == "event":
            attributes = {}
            tags = entity_categorizer.categorize_event(text, args.entity_name)
        
        logger.info(f"Atributy: {json.dumps(attributes, ensure_ascii=False, indent=2)}")
        logger.info(f"Tagy: {tags}")
    
    # Extrakce vztahů
    relationships = entity_extractor.extract_relationships(text)
    if relationships:
        logger.info(f"Extrahováno {len(relationships)} vztahů:")
        for relationship in relationships:
            logger.info(f"  - {relationship['subject']} ({relationship['subject_type']}) {relationship['predicate']} {relationship['object']} ({relationship['object_type']})")
    
    # Uložení výsledků do souboru
    if args.output:
        try:
            results = {
                "entities": entities,
                "relationships": relationships,
            }
            
            if args.entity_name and args.entity_type:
                results["attributes"] = attributes
                results["tags"] = tags
            
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Výsledky byly uloženy do souboru {args.output}")
        except Exception as e:
            logger.error(f"Chyba při ukládání výsledků: {e}")


if __name__ == "__main__":
    main()
