"""
Configuration management using pydantic-settings.
Loads settings from environment variables or .env file.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # BigQuery Configuration
    bq_project_id: str = Field(
        default="tacheon-assessment-task2",
        description="GCP project ID"
    )
    bq_dataset_id: str = Field(
        default="crypto_market",
        description="BigQuery dataset ID"
    )
    bq_table_id: str = Field(
        default="coin_snapshots",
        description="BigQuery table ID"
    )
    
    # CoinGecko API Configuration
    coingecko_api_endpoint: str = Field(
        default="https://api.coingecko.com/api/v3/coins/markets",
        description="CoinGecko API endpoint"
    )
    coingecko_vs_currency: str = Field(
        default="usd",
        description="Currency for price comparison"
    )
    coingecko_per_page: int = Field(
        default=100,
        ge=1,
        le=250,
        description="Number of coins per page (max 250)"
    )
    coingecko_max_pages: int = Field(
        default=3,
        ge=1,
        description="Maximum number of pages to fetch"
    )
    
    # Pipeline Configuration
    volatility_threshold: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Threshold for volatility flag (e.g., 0.05 = 5%)"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    @property
    def bq_full_table_id(self) -> str:
        """Full BigQuery table ID in format: project.dataset.table"""
        return f"{self.bq_project_id}.{self.bq_dataset_id}.{self.bq_table_id}"


# Singleton instance
config = Config()
