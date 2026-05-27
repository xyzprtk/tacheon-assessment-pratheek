# CoinGecko Data Pipeline to BigQuery

A Python-based ETL pipeline that extracts cryptocurrency market data from the CoinGecko API, transforms it with derived analytical fields, and loads it into Google BigQuery for analysis.

## Project Structure

```
task2/
├── config.py              # Configuration management using pydantic-settings
├── fetch.py               # API extraction with retry logic and error handling
├── transform.py           # Data cleansing and derived field calculations
├── load.py                # BigQuery loading with schema and partitioning
├── main.py                # Pipeline orchestrator
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── sql/                   # SQL queries for analysis
│   ├── create_table.sql
│   ├── summary_volatility.sql
│   ├── summary_market_tiers.sql
│   └── summary_trends.sql
├── tests/                 # Unit and integration tests
│   ├── test_fetch.py
│   ├── test_transform.py
│   └── test_load.py
└── docs/
    └── production_thinking.md
```

## Why CoinGecko

CoinGecko provides cryptocurrency market data through a public API that returns rich nested JSON structures. The data includes price information, market capitalization, trading volume, supply metrics, and historical data like all-time highs and lows. This makes it suitable for demonstrating data pipeline capabilities including JSON flattening, type casting, and derived field calculations.

The API does not require authentication for basic access, which simplifies setup. However, it enforces rate limits that require proper error handling and retry logic with exponential backoff.

## Prerequisites

- Python 3.11 or higher
- Google Cloud SDK (gcloud)
- A Google Cloud Platform project with BigQuery API enabled
- A service account with BigQuery Data Editor and BigQuery Job User roles

## Setup

### 1. Create a GCP Project

1. Go to Google Cloud Console
2. Create a new project
3. Enable the BigQuery API
4. Create a service account with BigQuery Data Editor and BigQuery Job User roles
5. Download the service account key as JSON
6. Move the key file to a secure location outside the project directory:
   ```bash
   mkdir -p ~/.config/gcloud
   mv ~/Downloads/your-key-file.json ~/.config/gcloud/bigquery-sa-key.json
   chmod 600 ~/.config/gcloud/bigquery-sa-key.json
   ```

### 2. Set Environment Variables

Add to your shell profile (~/.bashrc, ~/.zshrc, or equivalent):
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/bigquery-sa-key.json"
```

### 3. Create a BigQuery Dataset

Using the gcloud CLI:
```bash
bq mk --location=US crypto_market
```

Or through the BigQuery UI:
1. Navigate to BigQuery in the GCP Console
2. Create a new dataset named `crypto_market`
3. Set location to US (or your preferred region)

### 4. Install Python Dependencies

```bash
cd task2
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure the Pipeline

Copy the environment template and edit it:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
BQ_PROJECT_ID="your-gcp-project-id"
BQ_DATASET_ID="crypto_market"
BQ_TABLE_ID="coin_snapshots"
VOLATILITY_THRESHOLD=0.05
LOG_LEVEL="INFO"
```

## Running the Pipeline

```bash
python main.py
```

The pipeline will:
1. Fetch cryptocurrency data from CoinGecko API (up to 3 pages by default)
2. Flatten nested JSON structures
3. Cleanse data and add derived analytical fields
4. Load the transformed data into BigQuery

Check the logs to monitor progress and verify successful completion.

## Running Tests

```bash
pytest tests/ -v
```

For coverage report:
```bash
pytest tests/ --cov=. --cov-report=html
```

## Data Model

The pipeline loads data into a BigQuery table with the following structure:

**Partitioning:** By `snapshot_date` (DAY)
**Clustering:** By `id` and `market_cap_tier`

### Core Fields
- `id`, `symbol`, `name`: Coin identifiers
- `snapshot_timestamp`, `snapshot_date`: When data was fetched
- `current_price`, `price_change_24h`, `price_change_percentage_24h`: Price metrics
- `market_cap`, `market_cap_rank`, `total_volume`: Market data
- `circulating_supply`, `total_supply`, `max_supply`: Supply metrics
- `ath`, `ath_date`, `atl`, `atl_date`: Historical highs and lows

### Derived Fields
- `volatility_flag`: Boolean indicating if 24h price change exceeds threshold
- `market_cap_tier`: Categorical bucket (Large Cap, Mid Cap, Small Cap, Micro Cap)
- `price_to_ath_ratio`: Current price as percentage of all-time high
- `supply_circulation_pct`: Percentage of total supply in circulation
- `volume_to_mcap_ratio`: Trading volume relative to market cap
- `price_range_24h_pct`: Daily high-low range as percentage

## SQL Queries

The `sql/` directory contains analysis queries:

- `create_table.sql`: DDL for creating the partitioned table
- `summary_volatility.sql`: Identifies most volatile coins over 7 days
- `summary_market_tiers.sql`: Distribution of coins by market cap tier
- `summary_trends.sql`: Price trends with 7-day moving averages for top coins

Run queries using the BigQuery UI or gcloud CLI:
```bash
bq query --use_legacy_sql=false "$(cat sql/summary_volatility.sql)"
```

## Error Handling

The pipeline handles various error scenarios:

- **Rate limits (HTTP 429):** Exponential backoff with retry, respects Retry-After header
- **Client errors (HTTP 4xx):** Fails fast without retry (invalid request parameters)
- **Server errors (HTTP 5xx):** Retries with exponential backoff
- **Network timeouts:** Retries like server errors
- **Empty API responses:** Exits gracefully without loading empty data
- **Duplicate records:** Deduplicates on coin ID and snapshot date
- **Null values:** Preserves as NULL in BigQuery, does not invent defaults
- **Idempotent writes:** Uses WRITE_TRUNCATE on partition to prevent duplicates on re-run

## Production Considerations

See `docs/production_thinking.md` for details on:
- Scheduling with Cloud Scheduler and Cloud Run Jobs
- Observability and alerting
- Scaling strategies for higher data volumes
- Edge cases and resilience patterns

## API Choice Rationale

CoinGecko was selected because:

1. **Rich nested JSON:** Requires flattening operations (demonstrates data transformation skills)
2. **Natural derived fields:** Volatility, market cap tiers, price ratios (shows analytical value-add)
3. **Real-world relevance:** Cryptocurrency data is volatile and time-sensitive
4. **Rate limits:** Forces implementation of proper retry logic and backoff strategies
5. **No authentication required:** Simplifies setup for assessment purposes
6. **Comprehensive data:** Includes price, volume, market cap, supply, and historical data

## Technology Choices

- **requests:** Standard HTTP library for API calls
- **tenacity:** Retry logic with exponential backoff
- **pydantic-settings:** Type-safe configuration management with environment variable support
- **pandas:** Data transformation and cleansing
- **google-cloud-bigquery:** Official BigQuery client
- **pytest:** Testing framework

## What Could Be Improved With More Time

- Data quality framework (Great Expectations or Soda Core)
- Incremental loading (only fetch coins that changed since last run)
- Historical backfill capability
- Dashboard in Metabase or Looker Studio
- Integration tests with actual BigQuery table
- CI/CD pipeline with GitHub Actions
- Prometheus metrics for monitoring
- Slack notifications for pipeline status
