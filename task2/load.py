"""
Load module: Loads transformed data into BigQuery with explicit schema and partitioning.
"""
import logging
from datetime import date

import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

from config import config

logger = logging.getLogger(__name__)


BQ_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED", description="CoinGecko coin ID"),
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED", description="Coin symbol"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED", description="Coin name"),
    bigquery.SchemaField("snapshot_timestamp", "TIMESTAMP", mode="REQUIRED", description="When data was fetched"),
    bigquery.SchemaField("snapshot_date", "DATE", mode="REQUIRED", description="Date for partitioning"),
    
    bigquery.SchemaField("current_price", "FLOAT64", mode="NULLABLE", description="Current price in USD"),
    bigquery.SchemaField("price_change_24h", "FLOAT64", mode="NULLABLE", description="24h price change"),
    bigquery.SchemaField("price_change_percentage_24h", "FLOAT64", mode="NULLABLE", description="24h price change %"),
    bigquery.SchemaField("high_24h", "FLOAT64", mode="NULLABLE", description="24h high price"),
    bigquery.SchemaField("low_24h", "FLOAT64", mode="NULLABLE", description="24h low price"),
    
    bigquery.SchemaField("market_cap", "FLOAT64", mode="NULLABLE", description="Market capitalization"),
    bigquery.SchemaField("market_cap_rank", "INT64", mode="NULLABLE", description="Market cap rank"),
    bigquery.SchemaField("fully_diluted_valuation", "FLOAT64", mode="NULLABLE", description="Fully diluted valuation"),
    bigquery.SchemaField("total_volume", "FLOAT64", mode="NULLABLE", description="24h trading volume"),
    
    bigquery.SchemaField("circulating_supply", "FLOAT64", mode="NULLABLE", description="Circulating supply"),
    bigquery.SchemaField("total_supply", "FLOAT64", mode="NULLABLE", description="Total supply"),
    bigquery.SchemaField("max_supply", "FLOAT64", mode="NULLABLE", description="Max supply"),
    
    bigquery.SchemaField("ath", "FLOAT64", mode="NULLABLE", description="All-time high price"),
    bigquery.SchemaField("ath_change_percentage", "FLOAT64", mode="NULLABLE", description="ATH change %"),
    bigquery.SchemaField("ath_date", "TIMESTAMP", mode="NULLABLE", description="ATH date"),
    bigquery.SchemaField("atl", "FLOAT64", mode="NULLABLE", description="All-time low price"),
    bigquery.SchemaField("atl_change_percentage", "FLOAT64", mode="NULLABLE", description="ATL change %"),
    bigquery.SchemaField("atl_date", "TIMESTAMP", mode="NULLABLE", description="ATL date"),
    
    bigquery.SchemaField("volatility_flag", "BOOLEAN", mode="NULLABLE", description="True if 24h change > threshold"),
    bigquery.SchemaField("market_cap_tier", "STRING", mode="NULLABLE", description="Market cap category"),
    bigquery.SchemaField("price_to_ath_ratio", "FLOAT64", mode="NULLABLE", description="Current price / ATH"),
    bigquery.SchemaField("supply_circulation_pct", "FLOAT64", mode="NULLABLE", description="% of supply in circulation"),
    bigquery.SchemaField("volume_to_mcap_ratio", "FLOAT64", mode="NULLABLE", description="Volume / market cap"),
    bigquery.SchemaField("price_range_24h_pct", "FLOAT64", mode="NULLABLE", description="24h high-low range %"),
    
    bigquery.SchemaField("last_updated", "TIMESTAMP", mode="NULLABLE", description="Last updated by API"),
]


def get_bigquery_client() -> bigquery.Client:
    """
    Initialize and return a BigQuery client.
    
    Returns:
        BigQuery client instance
    
    Raises:
        GoogleAPIError: If authentication or connection fails
    """
    try:
        client = bigquery.Client(project=config.bq_project_id)
        logger.info(
            f"BigQuery client initialized for project: {config.bq_project_id}",
            extra={"event": "bq_client_init", "project": config.bq_project_id}
        )
        return client
    except GoogleAPIError as e:
        logger.error(
            f"Failed to initialize BigQuery client: {e}",
            extra={"event": "bq_client_error"}
        )
        raise


def ensure_table_exists(client: bigquery.Client) -> None:
    """
    Create the BigQuery table with partitioning if it doesn't exist.
    If table exists but isn't partitioned, delete and recreate it.
    
    Args:
        client: BigQuery client instance
    """
    table_id = config.bq_full_table_id
    
    try:
        table = client.get_table(table_id)
        
        # Check if table is partitioned
        if table.time_partitioning is None:
            logger.warning(
                f"Table {table_id} exists but is not partitioned. Deleting and recreating.",
                extra={"event": "bq_table_not_partitioned", "table": table_id}
            )
            client.delete_table(table_id)
            raise Exception("Table not partitioned, recreating")
        
        logger.info(
            f"Table already exists: {table_id}",
            extra={"event": "bq_table_exists", "table": table_id}
        )
    except Exception:
        logger.info(
            f"Creating table: {table_id}",
            extra={"event": "bq_table_create_start", "table": table_id}
        )
        
        table = bigquery.Table(table_id, schema=BQ_SCHEMA)
        
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="snapshot_date"
        )
        
        table.clustering_fields = ["id", "market_cap_tier"]
        
        table = client.create_table(table)
        
        logger.info(
            f"Table created: {table_id} with partitioning on snapshot_date",
            extra={
                "event": "bq_table_create_complete",
                "table": table_id,
                "partition_field": "snapshot_date"
            }
        )


def load_to_bigquery(df: pd.DataFrame, target_date: date) -> None:
    """
    Load DataFrame to BigQuery with idempotent write (truncate partition).
    
    Args:
        df: Transformed DataFrame
        target_date: Date partition to write to
    
    Raises:
        GoogleAPIError: If load job fails
    """
    client = get_bigquery_client()
    
    ensure_table_exists(client)
    
    job_config = bigquery.LoadJobConfig(
        schema=BQ_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="snapshot_date"
        ),
        clustering_fields=["id", "market_cap_tier"]
    )
    
    partition_decorator = f"{config.bq_full_table_id}${target_date.strftime('%Y%m%d')}"
    
    logger.info(
        f"Loading {len(df)} rows to BigQuery partition: {partition_decorator}",
        extra={
            "event": "bq_load_start",
            "table": config.bq_full_table_id,
            "partition": str(target_date),
            "rows": len(df)
        }
    )
    
    try:
        job = client.load_table_from_dataframe(
            df,
            partition_decorator,
            job_config=job_config
        )
        
        job.result()
        
        logger.info(
            f"Successfully loaded {len(df)} rows to {partition_decorator}",
            extra={
                "event": "bq_load_complete",
                "table": config.bq_full_table_id,
                "partition": str(target_date),
                "rows": len(df),
                "job_id": job.job_id
            }
        )
        
    except GoogleAPIError as e:
        logger.error(
            f"BigQuery load failed: {e}",
            extra={
                "event": "bq_load_error",
                "table": config.bq_full_table_id,
                "partition": str(target_date)
            }
        )
        raise
