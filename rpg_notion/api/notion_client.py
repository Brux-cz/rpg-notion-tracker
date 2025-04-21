"""
Klientská třída pro interakci s Notion API.
"""
import logging
import time
from typing import Any, Dict, List, Optional, Union

import requests
from notion_client import Client
from notion_client.errors import APIResponseError, HTTPResponseError

from rpg_notion.config.settings import (
    NOTION_API_KEY,
    NOTION_MAX_RETRIES,
    NOTION_RATE_LIMIT_DELAY,
    NOTION_VERSION,
)

logger = logging.getLogger(__name__)


class NotionClientWrapper:
    """
    Wrapper kolem oficiálního Notion klienta s přidanou funkcionalitou
    pro správu rate limitů a zpracování chyb.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializace Notion klienta.

        Args:
            api_key: Notion API klíč. Pokud není zadán, použije se z konfigurace.
        """
        self.api_key = api_key or NOTION_API_KEY
        if not self.api_key:
            raise ValueError("Notion API klíč není nastaven.")

        self.client = Client(auth=self.api_key, version=NOTION_VERSION)
        self.max_retries = NOTION_MAX_RETRIES
        self.rate_limit_delay = NOTION_RATE_LIMIT_DELAY

    def _handle_rate_limit(self, retry_count: int) -> None:
        """
        Zpracování rate limitu s exponenciálním zpožděním.

        Args:
            retry_count: Počet dosavadních pokusů.
        """
        delay = self.rate_limit_delay * (2 ** retry_count)
        logger.warning(f"Rate limit dosažen. Čekání {delay} sekund před dalším pokusem.")
        time.sleep(delay)

    def _execute_with_retry(self, operation, *args, **kwargs) -> Any:
        """
        Provede operaci s automatickým opakováním při rate limitu.

        Args:
            operation: Funkce k provedení.
            *args: Argumenty pro funkci.
            **kwargs: Klíčové argumenty pro funkci.

        Returns:
            Výsledek operace.

        Raises:
            Exception: Pokud operace selže i po maximálním počtu pokusů.
        """
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                return operation(*args, **kwargs)
            except (APIResponseError, HTTPResponseError) as e:
                if hasattr(e, "code") and e.code == "rate_limited" and retry_count < self.max_retries:
                    retry_count += 1
                    self._handle_rate_limit(retry_count)
                else:
                    logger.error(f"Chyba při volání Notion API: {e}")
                    raise
            except Exception as e:
                logger.error(f"Neočekávaná chyba: {e}")
                raise

    # Databáze

    def create_database(
        self, parent_page_id: str, title: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Vytvoří novou databázi v Notion.

        Args:
            parent_page_id: ID rodičovské stránky.
            title: Název databáze.
            properties: Vlastnosti databáze.

        Returns:
            Vytvořená databáze.
        """
        return self._execute_with_retry(
            self.client.databases.create,
            parent={
                "type": "page_id",
                "page_id": parent_page_id,
            },
            title=[
                {
                    "type": "text",
                    "text": {
                        "content": title,
                    },
                }
            ],
            properties=properties,
        )

    def update_database(
        self, database_id: str, title: Optional[str] = None, properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aktualizuje existující databázi v Notion.

        Args:
            database_id: ID databáze.
            title: Nový název databáze.
            properties: Nové vlastnosti databáze.

        Returns:
            Aktualizovaná databáze.
        """
        params = {}
        if title:
            params["title"] = [
                {
                    "type": "text",
                    "text": {
                        "content": title,
                    },
                }
            ]
        if properties:
            params["properties"] = properties

        return self._execute_with_retry(
            self.client.databases.update,
            database_id=database_id,
            **params,
        )

    def query_database(
        self, database_id: str, filter: Optional[Dict[str, Any]] = None, sorts: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Dotaz na databázi v Notion.

        Args:
            database_id: ID databáze.
            filter: Filtr pro dotaz.
            sorts: Řazení výsledků.

        Returns:
            Seznam stránek v databázi.
        """
        params = {}
        if filter:
            params["filter"] = filter
        if sorts:
            params["sorts"] = sorts

        response = self._execute_with_retry(
            self.client.databases.query,
            database_id=database_id,
            **params,
        )
        return response.get("results", [])

    # Stránky

    def create_page(
        self, parent_id: str, parent_type: str = "database_id", properties: Optional[Dict[str, Any]] = None, 
        content: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Vytvoří novou stránku v Notion.

        Args:
            parent_id: ID rodiče (databáze nebo stránky).
            parent_type: Typ rodiče ('database_id' nebo 'page_id').
            properties: Vlastnosti stránky.
            content: Obsah stránky.

        Returns:
            Vytvořená stránka.
        """
        params = {
            "parent": {
                "type": parent_type,
                parent_type: parent_id,
            },
        }
        if properties:
            params["properties"] = properties
        if content:
            params["children"] = content

        return self._execute_with_retry(
            self.client.pages.create,
            **params,
        )

    def update_page(
        self, page_id: str, properties: Optional[Dict[str, Any]] = None, archived: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Aktualizuje existující stránku v Notion.

        Args:
            page_id: ID stránky.
            properties: Nové vlastnosti stránky.
            archived: Zda má být stránka archivována.

        Returns:
            Aktualizovaná stránka.
        """
        params = {}
        if properties:
            params["properties"] = properties
        if archived is not None:
            params["archived"] = archived

        return self._execute_with_retry(
            self.client.pages.update,
            page_id=page_id,
            **params,
        )

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        Získá stránku z Notion.

        Args:
            page_id: ID stránky.

        Returns:
            Stránka.
        """
        return self._execute_with_retry(
            self.client.pages.retrieve,
            page_id=page_id,
        )

    def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        """
        Získá potomky bloku (stránky nebo bloku) z Notion.

        Args:
            block_id: ID bloku.

        Returns:
            Seznam potomků bloku.
        """
        response = self._execute_with_retry(
            self.client.blocks.children.list,
            block_id=block_id,
        )
        return response.get("results", [])

    def append_block_children(self, block_id: str, children: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Přidá potomky k bloku (stránce nebo bloku) v Notion.

        Args:
            block_id: ID bloku.
            children: Seznam potomků k přidání.

        Returns:
            Výsledek operace.
        """
        return self._execute_with_retry(
            self.client.blocks.children.append,
            block_id=block_id,
            children=children,
        )

    # Vyhledávání

    def search(
        self, query: str, filter: Optional[Dict[str, Any]] = None, sort: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Vyhledávání v Notion.

        Args:
            query: Dotaz pro vyhledávání.
            filter: Filtr pro vyhledávání.
            sort: Řazení výsledků.

        Returns:
            Seznam výsledků vyhledávání.
        """
        params = {"query": query}
        if filter:
            params["filter"] = filter
        if sort:
            params["sort"] = sort

        response = self._execute_with_retry(
            self.client.search,
            **params,
        )
        return response.get("results", [])
