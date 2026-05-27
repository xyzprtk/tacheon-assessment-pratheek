"""
Unit tests for the transform module.
"""
import pytest
import pandas as pd
from transform import flatten_coin_data, cleanse_data, add_derived_fields


@pytest.fixture
def sample_raw_data():
    """Sample CoinGecko API response for testing."""
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 50000.0,
            "market_cap": 1e12,
            "market_cap_rank": 1,
            "total_volume": 2.5e10,
            "high_24h": 51000.0,
            "low_24h": 49000.0,
            "price_change_24h": 500.0,
            "price_change_percentage_24h": 1.0,
            "circulating_supply": 19500000.0,
            "total_supply": 21000000.0,
            "max_supply": 21000000.0,
            "ath": 69000.0,
            "ath_change_percentage": -27.5,
            "last_updated": "2026-05-26T10:00:00.000Z"
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 3000.0,
            "market_cap": 3.6e11,
            "market_cap_rank": 2,
            "total_volume": 1.5e10,
            "high_24h": 3100.0,
            "low_24h": 2900.0,
            "price_change_24h": -50.0,
            "price_change_percentage_24h": -1.6,
            "circulating_supply": 120000000.0,
            "total_supply": 120000000.0,
            "max_supply": None,
            "ath": 4800.0,
            "ath_change_percentage": -37.5,
            "last_updated": "2026-05-26T10:00:00.000Z"
        }
    ]


def test_flatten_coin_data(sample_raw_data):
    """Test that nested JSON is flattened correctly."""
    df = flatten_coin_data(sample_raw_data)
    
    assert len(df) == 2
    assert "id" in df.columns
    assert "current_price" in df.columns
    assert df.iloc[0]["id"] == "bitcoin"
    assert df.iloc[0]["current_price"] == 50000.0


def test_cleanse_data_adds_snapshot_fields(sample_raw_data):
    """Test that cleanse adds snapshot timestamp and date."""
    df_flat = flatten_coin_data(sample_raw_data)
    df_clean = cleanse_data(df_flat)
    
    assert "snapshot_timestamp" in df_clean.columns
    assert "snapshot_date" in df_clean.columns
    assert df_clean["snapshot_date"].notna().all()


def test_add_derived_fields_volatility_flag(sample_raw_data):
    """Test that volatility flag is calculated correctly."""
    df_flat = flatten_coin_data(sample_raw_data)
    df_clean = cleanse_data(df_flat)
    df_derived = add_derived_fields(df_clean)
    
    assert df_derived.iloc[0]["volatility_flag"] == False
    assert df_derived.iloc[1]["volatility_flag"] == False


def test_add_derived_fields_market_cap_tier(sample_raw_data):
    """Test that market cap tier is categorized correctly."""
    df_flat = flatten_coin_data(sample_raw_data)
    df_clean = cleanse_data(df_flat)
    df_derived = add_derived_fields(df_clean)
    
    assert df_derived.iloc[0]["market_cap_tier"] == "Large Cap"
    assert df_derived.iloc[1]["market_cap_tier"] == "Large Cap"


def test_add_derived_fields_price_to_ath_ratio(sample_raw_data):
    """Test that price to ATH ratio is calculated correctly."""
    df_flat = flatten_coin_data(sample_raw_data)
    df_clean = cleanse_data(df_flat)
    df_derived = add_derived_fields(df_clean)
    
    expected_ratio = 50000.0 / 69000.0
    assert abs(df_derived.iloc[0]["price_to_ath_ratio"] - expected_ratio) < 0.001


def test_handle_null_max_supply(sample_raw_data):
    """Test that null max_supply is handled gracefully."""
    df_flat = flatten_coin_data(sample_raw_data)
    df_clean = cleanse_data(df_flat)
    df_derived = add_derived_fields(df_clean)
    
    assert pd.isna(df_derived.iloc[1]["max_supply"])
