-- Create the partitioned and clustered table
CREATE TABLE IF NOT EXISTS `crypto_market.coin_snapshots` (
    id STRING NOT NULL,
    symbol STRING NOT NULL,
    name STRING NOT NULL,
    snapshot_timestamp TIMESTAMP NOT NULL,
    snapshot_date DATE NOT NULL,
    
    current_price FLOAT64,
    price_change_24h FLOAT64,
    price_change_percentage_24h FLOAT64,
    high_24h FLOAT64,
    low_24h FLOAT64,
    
    market_cap FLOAT64,
    market_cap_rank INT64,
    fully_diluted_valuation FLOAT64,
    total_volume FLOAT64,
    
    circulating_supply FLOAT64,
    total_supply FLOAT64,
    max_supply FLOAT64,
    
    ath FLOAT64,
    ath_change_percentage FLOAT64,
    ath_date TIMESTAMP,
    atl FLOAT64,
    atl_change_percentage FLOAT64,
    atl_date TIMESTAMP,
    
    volatility_flag BOOLEAN,
    market_cap_tier STRING,
    price_to_ath_ratio FLOAT64,
    supply_circulation_pct FLOAT64,
    volume_to_mcap_ratio FLOAT64,
    price_range_24h_pct FLOAT64,
    
    last_updated TIMESTAMP
)
PARTITION BY snapshot_date
CLUSTER BY id, market_cap_tier
OPTIONS(
    description="Daily cryptocurrency market snapshots from CoinGecko"
);
