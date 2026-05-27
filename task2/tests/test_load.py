"""
Integration tests for the load module.
"""
import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from load import get_bigquery_client, ensure_table_exists, load_to_bigquery


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "id": ["bitcoin", "ethereum"],
        "symbol": ["btc", "eth"],
        "name": ["Bitcoin", "Ethereum"],
        "snapshot_timestamp": pd.to_datetime(["2026-05-26", "2026-05-26"]),
        "snapshot_date": [date(2026, 5, 26), date(2026, 5, 26)],
        "current_price": [50000.0, 3000.0],
        "market_cap": [1e12, 3.6e11],
        "volatility_flag": [False, False],
        "market_cap_tier": ["Large Cap", "Large Cap"]
    })


def test_get_bigquery_client():
    """Test BigQuery client initialization."""
    with patch('load.bigquery.Client') as mock_client:
        client = get_bigquery_client()
        mock_client.assert_called_once()
        assert client is not None


def test_ensure_table_exists_table_already_exists():
    """Test table existence check when table exists."""
    mock_client = Mock()
    mock_client.get_table.return_value = Mock()
    
    with patch('load.config') as mock_config:
        mock_config.bq_full_table_id = "test.dataset.table"
        ensure_table_exists(mock_client)
        mock_client.get_table.assert_called_once()
        mock_client.create_table.assert_not_called()


def test_ensure_table_exists_creates_table():
    """Test table creation when table doesn't exist."""
    mock_client = Mock()
    mock_client.get_table.side_effect = Exception("Not found")
    
    with patch('load.config') as mock_config:
        mock_config.bq_full_table_id = "test.dataset.table"
        ensure_table_exists(mock_client)
        mock_client.create_table.assert_called_once()
