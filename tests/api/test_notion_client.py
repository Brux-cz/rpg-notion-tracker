"""
Testy pro NotionClientWrapper.
"""
import os
from unittest.mock import MagicMock, patch

import pytest
from notion_client.errors import APIResponseError

from rpg_notion.api.notion_client import NotionClientWrapper


@pytest.fixture
def mock_notion_client():
    """
    Fixture pro mock Notion klienta.
    """
    with patch("rpg_notion.api.notion_client.Client") as mock_client:
        yield mock_client


@pytest.fixture
def notion_client_wrapper(mock_notion_client):
    """
    Fixture pro NotionClientWrapper s mock Notion klientem.
    """
    with patch.dict(os.environ, {"NOTION_API_KEY": "test_api_key"}):
        return NotionClientWrapper()


def test_init_without_api_key():
    """
    Test inicializace bez API klíče.
    """
    with patch.dict(os.environ, {"NOTION_API_KEY": ""}):
        with pytest.raises(ValueError):
            NotionClientWrapper()


def test_init_with_api_key(mock_notion_client):
    """
    Test inicializace s API klíčem.
    """
    with patch.dict(os.environ, {"NOTION_API_KEY": "test_api_key"}):
        client = NotionClientWrapper()
        assert client.api_key == "test_api_key"
        mock_notion_client.assert_called_once_with(auth="test_api_key", version="2022-06-28")


def test_handle_rate_limit(notion_client_wrapper):
    """
    Test zpracování rate limitu.
    """
    with patch("time.sleep") as mock_sleep:
        notion_client_wrapper._handle_rate_limit(0)
        mock_sleep.assert_called_once_with(0.5)

        mock_sleep.reset_mock()
        notion_client_wrapper._handle_rate_limit(1)
        mock_sleep.assert_called_once_with(1.0)

        mock_sleep.reset_mock()
        notion_client_wrapper._handle_rate_limit(2)
        mock_sleep.assert_called_once_with(2.0)


def test_execute_with_retry_success(notion_client_wrapper):
    """
    Test úspěšného provedení operace.
    """
    mock_operation = MagicMock(return_value="success")
    result = notion_client_wrapper._execute_with_retry(mock_operation, "arg1", kwarg1="kwarg1")
    assert result == "success"
    mock_operation.assert_called_once_with("arg1", kwarg1="kwarg1")


def test_execute_with_retry_rate_limit(notion_client_wrapper):
    """
    Test provedení operace s rate limitem.
    """
    mock_operation = MagicMock(side_effect=[
        APIResponseError(message="Rate limited", code="rate_limited", headers={}),
        "success"
    ])
    
    with patch.object(notion_client_wrapper, "_handle_rate_limit") as mock_handle_rate_limit:
        result = notion_client_wrapper._execute_with_retry(mock_operation, "arg1", kwarg1="kwarg1")
        assert result == "success"
        assert mock_operation.call_count == 2
        mock_handle_rate_limit.assert_called_once_with(1)


def test_execute_with_retry_max_retries(notion_client_wrapper):
    """
    Test provedení operace s maximálním počtem pokusů.
    """
    mock_operation = MagicMock(side_effect=APIResponseError(message="Rate limited", code="rate_limited", headers={}))
    
    with patch.object(notion_client_wrapper, "_handle_rate_limit") as mock_handle_rate_limit:
        with pytest.raises(APIResponseError):
            notion_client_wrapper._execute_with_retry(mock_operation, "arg1", kwarg1="kwarg1")
        assert mock_operation.call_count == notion_client_wrapper.max_retries + 1
        assert mock_handle_rate_limit.call_count == notion_client_wrapper.max_retries
