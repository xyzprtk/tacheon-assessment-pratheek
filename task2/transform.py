"""
Transform module: Cleanses data and adds derived analytical fields.
"""
import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from config import config

logger = logging.getLogger(__name__)


def flatten_coin_data(raw_data: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Flatten nested JSON from CoinGecko API into a tabular DataFrame.
    
    Args:
        raw_data: List of coin dictionaries from API
    
    Returns:
        Flattened pandas DataFrame
    """
    logger.info(
        f"Flattening {len(raw_data)} coin records",
        extra={"event": "transform_flatten_start", "rows": len(raw_data)}
    )
    
    df = pd.json_normalize(raw_data, sep="_")
    
    logger.info(
        f"Flattened to {len(df.columns)} columns",
        extra={"event": "transform_flatten_complete", "columns": len(df.columns)}
    )
    
    return df


def cleanse_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleanse data by handling nulls, type mismatches, and duplicates.
    
    Args:
        df: Raw flattened DataFrame
    
    Returns:
        Cleansed DataFrame
    """
    logger.info("Starting data cleansing", extra={"event": "transform_cleanse_start"})
    
    df_clean = df.copy()
    
    df_clean["snapshot_timestamp"] = datetime.now(timezone.utc)
    df_clean["snapshot_date"] = pd.to_datetime(df_clean["snapshot_timestamp"]).dt.date
    
    numeric_columns = [
        "current_price", "market_cap", "fully_diluted_valuation",
        "total_volume", "high_24h", "low_24h", "price_change_24h",
        "price_change_percentage_24h", "market_cap_change_24h",
        "market_cap_change_percentage_24h", "circulating_supply",
        "total_supply", "max_supply", "ath", "ath_change_percentage",
        "atl", "atl_change_percentage", "market_cap_rank"
    ]
    
    for col in numeric_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
    
    datetime_columns = ["last_updated", "ath_date", "atl_date"]
    for col in datetime_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce", utc=True)
    
    initial_count = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=["id", "snapshot_date"], keep="last")
    duplicates_removed = initial_count - len(df_clean)
    
    if duplicates_removed > 0:
        logger.warning(
            f"Removed {duplicates_removed} duplicate records",
            extra={"event": "transform_dedup", "duplicates": duplicates_removed}
        )
    
    logger.info(
        f"Cleansing complete: {len(df_clean)} records",
        extra={"event": "transform_cleanse_complete", "rows": len(df_clean)}
    )
    
    return df_clean


def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived analytical fields that provide value beyond raw API data.
    
    Args:
        df: Cleansed DataFrame
    
    Returns:
        DataFrame with derived fields
    """
    logger.info("Adding derived fields", extra={"event": "transform_derived_start"})
    
    df_derived = df.copy()
    
    if "price_change_percentage_24h" in df_derived.columns:
        df_derived["volatility_flag"] = (
            df_derived["price_change_percentage_24h"].abs() > config.volatility_threshold
        )
        logger.info(
            f"Added volatility_flag (threshold: {config.volatility_threshold})",
            extra={"event": "transform_derived_volatility"}
        )
    
    if "market_cap" in df_derived.columns:
        def categorize_market_cap(mcap):
            if pd.isna(mcap):
                return None
            elif mcap >= 1e11:
                return "Large Cap"
            elif mcap >= 1e10:
                return "Mid Cap"
            elif mcap >= 1e9:
                return "Small Cap"
            else:
                return "Micro Cap"
        
        df_derived["market_cap_tier"] = df_derived["market_cap"].apply(categorize_market_cap)
        logger.info("Added market_cap_tier", extra={"event": "transform_derived_mcap_tier"})
    
    if "current_price" in df_derived.columns and "ath" in df_derived.columns:
        df_derived["price_to_ath_ratio"] = (
            df_derived["current_price"] / df_derived["ath"]
        ).round(4)
        logger.info("Added price_to_ath_ratio", extra={"event": "transform_derived_ath_ratio"})
    
    if "circulating_supply" in df_derived.columns and "total_supply" in df_derived.columns:
        df_derived["supply_circulation_pct"] = (
            (df_derived["circulating_supply"] / df_derived["total_supply"]) * 100
        ).round(2)
        logger.info("Added supply_circulation_pct", extra={"event": "transform_derived_supply"})
    
    if "total_volume" in df_derived.columns and "market_cap" in df_derived.columns:
        df_derived["volume_to_mcap_ratio"] = (
            df_derived["total_volume"] / df_derived["market_cap"]
        ).round(6)
        logger.info("Added volume_to_mcap_ratio", extra={"event": "transform_derived_vol_mcap"})
    
    if "high_24h" in df_derived.columns and "low_24h" in df_derived.columns:
        df_derived["price_range_24h_pct"] = (
            ((df_derived["high_24h"] - df_derived["low_24h"]) / df_derived["low_24h"]) * 100
        ).round(2)
        logger.info("Added price_range_24h_pct", extra={"event": "transform_derived_range"})
    
    logger.info(
        f"Derived fields complete: {len(df_derived.columns)} total columns",
        extra={"event": "transform_derived_complete", "columns": len(df_derived.columns)}
    )
    
    return df_derived


def select_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select and reorder columns for the final output.
    
    Args:
        df: DataFrame with derived fields
    
    Returns:
        DataFrame with selected columns in desired order
    """
    final_columns = [
        "id", "symbol", "name", "snapshot_timestamp", "snapshot_date",
        "current_price", "price_change_24h", "price_change_percentage_24h",
        "high_24h", "low_24h",
        "market_cap", "market_cap_rank", "fully_diluted_valuation",
        "total_volume",
        "circulating_supply", "total_supply", "max_supply",
        "ath", "ath_change_percentage", "ath_date",
        "atl", "atl_change_percentage", "atl_date",
        "volatility_flag", "market_cap_tier", "price_to_ath_ratio",
        "supply_circulation_pct", "volume_to_mcap_ratio", "price_range_24h_pct",
        "last_updated"
    ]
    
    available_columns = [col for col in final_columns if col in df.columns]
    df_final = df[available_columns].copy()
    
    logger.info(
        f"Selected {len(available_columns)} columns for final output",
        extra={"event": "transform_columns_selected", "columns": len(available_columns)}
    )
    
    return df_final


def transform(raw_data: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Main transformation pipeline: flatten, cleanse, derive, select.
    
    Args:
        raw_data: List of coin dictionaries from API
    
    Returns:
        Transformed DataFrame ready for BigQuery
    """
    logger.info("Starting transformation pipeline", extra={"event": "transform_start"})
    
    df_flat = flatten_coin_data(raw_data)
    df_clean = cleanse_data(df_flat)
    df_derived = add_derived_fields(df_clean)
    df_final = select_final_columns(df_derived)
    
    logger.info(
        f"Transformation complete: {len(df_final)} rows, {len(df_final.columns)} columns",
        extra={
            "event": "transform_complete",
            "rows": len(df_final),
            "columns": len(df_final.columns)
        }
    )
    
    return df_final
