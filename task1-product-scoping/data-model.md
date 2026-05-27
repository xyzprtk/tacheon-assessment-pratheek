# Data Model: Marketing Performance Reporter

## Overview

The data model follows a three-layer architecture (Raw, Staging, Mart) to ensure data quality, auditability, and performance. All tables are stored in BigQuery with appropriate partitioning and clustering strategies.

**Dataset**: `marketing_data`  
**Project**: `marketing-performance-reporter`

---

## Layer 1: Raw Tables

Raw tables store unmodified API responses for audit and debugging purposes. These tables use flexible JSON schemas to accommodate API changes without breaking the pipeline.

### Table: `raw_meta_ads`

Stores raw responses from the Meta Marketing API.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| ingestion_date | DATE | REQUIRED | Date when data was ingested (partition key) |
| client_id | STRING | REQUIRED | Client identifier |
| data_date | DATE | REQUIRED | Date the data represents |
| raw_json | JSON | REQUIRED | Full API response payload |
| ingestion_timestamp | TIMESTAMP | REQUIRED | Exact timestamp of ingestion |
| api_version | STRING | REQUIRED | Meta Marketing API version used |
| request_id | STRING | NULLABLE | Meta API request ID for debugging |

**Partitioning**: Partitioned by `ingestion_date` (daily)  
**Clustering**: Clustered by `client_id`  
**Retention**: 90 days (older data automatically deleted)

**Example Query**:
```sql
SELECT 
  data_date,
  JSON_VALUE(raw_json, '$.spend') AS spend,
  JSON_VALUE(raw_json, '$.impressions') AS impressions
FROM `marketing-performance-reporter.marketing_data.raw_meta_ads`
WHERE ingestion_date = '2024-01-15'
  AND client_id = 'acme_corp'
```

---

### Table: `raw_google_ads`

Stores raw responses from the Google Ads API.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| ingestion_date | DATE | REQUIRED | Date when data was ingested (partition key) |
| client_id | STRING | REQUIRED | Client identifier |
| data_date | DATE | REQUIRED | Date the data represents |
| raw_json | JSON | REQUIRED | Full API response payload |
| ingestion_timestamp | TIMESTAMP | REQUIRED | Exact timestamp of ingestion |
| api_version | STRING | REQUIRED | Google Ads API version used |
| request_id | STRING | NULLABLE | Google Ads API request ID |

**Partitioning**: Partitioned by `ingestion_date` (daily)  
**Clustering**: Clustered by `client_id`  
**Retention**: 90 days

---

### Table: `raw_shopify`

Stores raw responses from the Shopify API.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| ingestion_date | DATE | REQUIRED | Date when data was ingested (partition key) |
| client_id | STRING | REQUIRED | Client identifier |
| data_date | DATE | REQUIRED | Date the data represents |
| raw_json | JSON | REQUIRED | Full API response payload |
| ingestion_timestamp | TIMESTAMP | REQUIRED | Exact timestamp of ingestion |
| api_version | STRING | REQUIRED | Shopify API version used |
| shop_domain | STRING | REQUIRED | Shopify store domain |

**Partitioning**: Partitioned by `ingestion_date` (daily)  
**Clustering**: Clustered by `client_id`  
**Retention**: 90 days

---

### Table: `raw_ga4`

Stores raw responses from the GA4 API.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| ingestion_date | DATE | REQUIRED | Date when data was ingested (partition key) |
| client_id | STRING | REQUIRED | Client identifier |
| data_date | DATE | REQUIRED | Date the data represents |
| raw_json | JSON | REQUIRED | Full API response payload |
| ingestion_timestamp | TIMESTAMP | REQUIRED | Exact timestamp of ingestion |
| property_id | STRING | REQUIRED | GA4 property ID |

**Partitioning**: Partitioned by `ingestion_date` (daily)  
**Clustering**: Clustered by `client_id`  
**Retention**: 90 days

---

## Layer 2: Staging Tables

Staging tables clean and normalize raw data into consistent schemas. These tables handle data type conversions, NULL handling, and standardization.

### Table: `stg_meta_ads`

Cleaned and normalized Meta Ads data.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| date | DATE | REQUIRED | Reporting date (ISO 8601 format) |
| client_id | STRING | REQUIRED | Client identifier |
| campaign_id | STRING | REQUIRED | Meta campaign ID |
| campaign_name | STRING | REQUIRED | Campaign name |
| adset_id | STRING | NULLABLE | Ad set ID (if applicable) |
| adset_name | STRING | NULLABLE | Ad set name |
| spend | FLOAT64 | REQUIRED | Spend in original currency (0 if NULL) |
| currency | STRING | REQUIRED | Original currency code (uppercase) |
| impressions | INT64 | REQUIRED | Total impressions (0 if NULL) |
| clicks | INT64 | REQUIRED | Total clicks (0 if NULL) |
| conversions | INT64 | REQUIRED | Total conversions (0 if NULL) |
| revenue | FLOAT64 | REQUIRED | Revenue in original currency (0 if NULL) |
| ctr | FLOAT64 | NULLABLE | Click-through rate (NULL if impressions = 0) |
| cpc | FLOAT64 | NULLABLE | Cost per click (NULL if clicks = 0) |
| cpm | FLOAT64 | NULLABLE | Cost per mille (NULL if impressions = 0) |
| ingestion_timestamp | TIMESTAMP | REQUIRED | When data was ingested |
| attribution_window | STRING | REQUIRED | Attribution window used (e.g., "7d_click") |

**Partitioning**: Partitioned by `date`  
**Clustering**: Clustered by `client_id`, `campaign_id`

**Transformations Applied**:
- Parse JSON from `raw_meta_ads`
- Convert date to ISO 8601 format
- Uppercase currency codes
- Replace NULL numeric values with 0
- Calculate CTR, CPC, CPM (NULL if denominator is 0)

**Example Query**:
```sql
SELECT 
  date,
  campaign_name,
  spend,
  impressions,
  clicks,
  conversions
FROM `marketing-performance-reporter.marketing_data.stg_meta_ads`
WHERE date BETWEEN '2024-01-08' AND '2024-01-14'
  AND client_id = 'acme_corp'
ORDER BY spend DESC
```

---

### Table: `stg_google_ads`

Cleaned and normalized Google Ads data.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| date | DATE | REQUIRED | Reporting date |
| client_id | STRING | REQUIRED | Client identifier |
| campaign_id | STRING | REQUIRED | Google Ads campaign ID |
| campaign_name | STRING | REQUIRED | Campaign name |
| ad_group_id | STRING | NULLABLE | Ad group ID |
| ad_group_name | STRING | NULLABLE | Ad group name |
| spend | FLOAT64 | REQUIRED | Spend in original currency |
| currency | STRING | REQUIRED | Original currency code |
| impressions | INT64 | REQUIRED | Total impressions |
| clicks | INT64 | REQUIRED | Total clicks |
| conversions | INT64 | REQUIRED | Total conversions |
| revenue | FLOAT64 | REQUIRED | Revenue in original currency |
| ctr | FLOAT64 | NULLABLE | Click-through rate |
| cpc | FLOAT64 | NULLABLE | Cost per click |
| cpm | FLOAT64 | NULLABLE | Cost per mille |
| ingestion_timestamp | TIMESTAMP | REQUIRED | When data was ingested |
| attribution_model | STRING | REQUIRED | Attribution model used |

**Partitioning**: Partitioned by `date`  
**Clustering**: Clustered by `client_id`, `campaign_id`

---

### Table: `stg_shopify`

Cleaned and normalized Shopify order data.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| date | DATE | REQUIRED | Order date |
| client_id | STRING | REQUIRED | Client identifier |
| order_id | STRING | REQUIRED | Shopify order ID |
| order_number | STRING | REQUIRED | Human-readable order number |
| revenue | FLOAT64 | REQUIRED | Order revenue in original currency |
| currency | STRING | REQUIRED | Original currency code |
| items_count | INT64 | REQUIRED | Number of items in order |
| customer_id | STRING | NULLABLE | Shopify customer ID |
| source_name | STRING | NULLABLE | Traffic source (e.g., "facebook", "google") |
| landing_site | STRING | NULLABLE | Landing page URL |
| created_at | TIMESTAMP | REQUIRED | Order creation timestamp (UTC) |
| ingestion_timestamp | TIMESTAMP | REQUIRED | When data was ingested |

**Partitioning**: Partitioned by `date`  
**Clustering**: Clustered by `client_id`, `order_id`

**Note**: Shopify data is attributed to marketing channels based on `source_name` and UTM parameters. This attribution happens in the mart layer.

---

### Table: `stg_ga4`

Cleaned and normalized GA4 session data.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| date | DATE | REQUIRED | Session date |
| client_id | STRING | REQUIRED | Client identifier |
| session_id | STRING | REQUIRED | GA4 session ID |
| user_id | STRING | NULLABLE | GA4 user ID |
| sessions | INT64 | REQUIRED | Number of sessions (typically 1) |
| users | INT64 | REQUIRED | Number of users (typically 1) |
| pageviews | INT64 | REQUIRED | Number of pageviews |
| bounces | INT64 | REQUIRED | Number of bounces |
| session_duration | FLOAT64 | REQUIRED | Session duration in seconds |
| source | STRING | NULLABLE | Traffic source (e.g., "facebook", "google") |
| medium | STRING | NULLABLE | Traffic medium (e.g., "cpc", "organic") |
| campaign | STRING | NULLABLE | Campaign name |
| landing_page | STRING | NULLABLE | Landing page path |
| conversions | INT64 | REQUIRED | Number of conversion events |
| ingestion_timestamp | TIMESTAMP | REQUIRED | When data was ingested |

**Partitioning**: Partitioned by `date`  
**Clustering**: Clustered by `client_id`, `session_id`

---

## Layer 3: Mart Tables

Mart tables contain aggregated business metrics ready for analysis and reporting. These tables are optimized for query performance and are the primary source for briefing generation.

### Table: `marketing_metrics_daily`

Daily aggregated marketing metrics at the client-channel level.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| date | DATE | REQUIRED | Reporting date (partition key) |
| client_id | STRING | REQUIRED | Client identifier |
| channel | STRING | REQUIRED | Marketing channel (meta, google_ads, shopify, ga4) |
| spend | FLOAT64 | REQUIRED | Total spend in base currency (USD) |
| impressions | INT64 | REQUIRED | Total impressions |
| clicks | INT64 | REQUIRED | Total clicks |
| conversions | INT64 | REQUIRED | Total conversions |
| revenue | FLOAT64 | REQUIRED | Revenue in base currency (USD) |
| roas | FLOAT64 | NULLABLE | Return on ad spend (revenue / spend) |
| cpa | FLOAT64 | NULLABLE | Cost per acquisition (spend / conversions) |
| ctr | FLOAT64 | NULLABLE | Click-through rate (clicks / impressions) |
| cvr | FLOAT64 | NULLABLE | Conversion rate (conversions / clicks) |
| spend_currency | STRING | REQUIRED | Original currency code for spend |
| revenue_currency | STRING | REQUIRED | Original currency code for revenue |
| exchange_rate_spend | FLOAT64 | REQUIRED | Exchange rate used for spend conversion |
| exchange_rate_revenue | FLOAT64 | REQUIRED | Exchange rate used for revenue conversion |
| ingestion_timestamp | TIMESTAMP | REQUIRED | When data was last updated |

**Partitioning**: Partitioned by `date` (daily)  
**Clustering**: Clustered by `client_id`, `channel`

**Derived Metrics**:

```sql
-- ROAS (Return on Ad Spend)
CASE 
  WHEN spend > 0 THEN revenue / spend 
  ELSE NULL 
END AS roas

-- CPA (Cost per Acquisition)
CASE 
  WHEN conversions > 0 THEN spend / conversions 
  ELSE NULL 
END AS cpa

-- CTR (Click-Through Rate)
CASE 
  WHEN impressions > 0 THEN clicks / impressions 
  ELSE NULL 
END AS ctr

-- CVR (Conversion Rate)
CASE 
  WHEN clicks > 0 THEN conversions / clicks 
  ELSE NULL 
END AS cvr
```

**Example Queries**:

1. **Get daily metrics for a specific client**:
```sql
SELECT 
  date,
  channel,
  spend,
  revenue,
  roas,
  cpa
FROM `marketing-performance-reporter.marketing_data.marketing_metrics_daily`
WHERE client_id = 'acme_corp'
  AND date BETWEEN '2024-01-08' AND '2024-01-14'
ORDER BY date, channel
```

2. **Calculate 7-day vs 7-day comparison**:
```sql
WITH current_period AS (
  SELECT 
    channel,
    SUM(spend) AS spend,
    SUM(revenue) AS revenue,
    SUM(conversions) AS conversions
  FROM `marketing-performance-reporter.marketing_data.marketing_metrics_daily`
  WHERE client_id = 'acme_corp'
    AND date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) 
                 AND DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  GROUP BY channel
),
previous_period AS (
  SELECT 
    channel,
    SUM(spend) AS spend,
    SUM(revenue) AS revenue,
    SUM(conversions) AS conversions
  FROM `marketing-performance-reporter.marketing_data.marketing_metrics_daily`
  WHERE client_id = 'acme_corp'
    AND date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) 
                 AND DATE_SUB(CURRENT_DATE(), INTERVAL 8 DAY)
  GROUP BY channel
)
SELECT 
  c.channel,
  c.spend AS current_spend,
  p.spend AS previous_spend,
  ROUND((c.spend - p.spend) / p.spend * 100, 2) AS spend_change_pct,
  c.revenue AS current_revenue,
  p.revenue AS previous_revenue,
  ROUND((c.revenue - p.revenue) / p.revenue * 100, 2) AS revenue_change_pct
FROM current_period c
LEFT JOIN previous_period p ON c.channel = p.channel
ORDER BY c.spend DESC
```

3. **Identify top 3 channels by spend**:
```sql
SELECT 
  channel,
  SUM(spend) AS total_spend,
  SUM(revenue) AS total_revenue,
  ROUND(SUM(revenue) / SUM(spend), 2) AS roas
FROM `marketing-performance-reporter.marketing_data.marketing_metrics_daily`
WHERE client_id = 'acme_corp'
  AND date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) 
               AND DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
GROUP BY channel
ORDER BY total_spend DESC
LIMIT 3
```

4. **Detect anomalies (spend dropped >50%)**:
```sql
WITH daily_spend AS (
  SELECT 
    date,
    channel,
    SUM(spend) AS spend
  FROM `marketing-performance-reporter.marketing_data.marketing_metrics_daily`
  WHERE client_id = 'acme_corp'
    AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)
  GROUP BY date, channel
),
spend_comparison AS (
  SELECT 
    curr.date,
    curr.channel,
    curr.spend AS current_spend,
    prev.spend AS previous_spend,
    ROUND((curr.spend - prev.spend) / prev.spend * 100, 2) AS change_pct
  FROM daily_spend curr
  LEFT JOIN daily_spend prev 
    ON curr.channel = prev.channel 
    AND prev.date = DATE_SUB(curr.date, INTERVAL 1 DAY)
)
SELECT 
  date,
  channel,
  current_spend,
  previous_spend,
  change_pct
FROM spend_comparison
WHERE change_pct < -50
  AND date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
```

---

## Supporting Tables

### Table: `exchange_rates`

Daily exchange rates for currency normalization.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| date | DATE | REQUIRED | Date of exchange rate |
| from_currency | STRING | REQUIRED | Source currency code |
| to_currency | STRING | REQUIRED | Target currency code (base currency) |
| rate | FLOAT64 | REQUIRED | Exchange rate |
| source | STRING | REQUIRED | Exchange rate API source |
| ingestion_timestamp | TIMESTAMP | REQUIRED | When rate was fetched |

**Partitioning**: Partitioned by `date`  
**Clustering**: Clustered by `from_currency`, `to_currency`

**Usage**:
```sql
SELECT 
  s.date,
  s.spend * e.rate AS spend_usd
FROM stg_meta_ads s
JOIN exchange_rates e 
  ON s.currency = e.from_currency 
  AND s.date = e.date
  AND e.to_currency = 'USD'
WHERE s.client_id = 'acme_corp'
```

---

### Table: `ingestion_logs`

Audit log of all ingestion activities.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| log_id | STRING | REQUIRED | Unique log identifier |
| ingestion_date | DATE | REQUIRED | Date of ingestion |
| client_id | STRING | REQUIRED | Client identifier |
| channel | STRING | REQUIRED | Data source channel |
| status | STRING | REQUIRED | Status (success, failed, partial) |
| records_ingested | INT64 | NULLABLE | Number of records ingested |
| api_response_time_ms | INT64 | NULLABLE | API response time in milliseconds |
| error_message | STRING | NULLABLE | Error message if failed |
| retry_count | INT64 | REQUIRED | Number of retry attempts |
| ingestion_timestamp | TIMESTAMP | REQUIRED | When ingestion occurred |

**Partitioning**: Partitioned by `ingestion_date`  
**Clustering**: Clustered by `client_id`, `channel`

**Usage**:
```sql
SELECT 
  channel,
  status,
  COUNT(*) AS attempt_count,
  AVG(api_response_time_ms) AS avg_response_time
FROM `marketing-performance-reporter.marketing_data.ingestion_logs`
WHERE ingestion_date = CURRENT_DATE()
GROUP BY channel, status
```

---

## Data Quality Checks

### Table: `data_quality_checks`

Results of data quality validation checks.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| check_id | STRING | REQUIRED | Unique check identifier |
| check_date | DATE | REQUIRED | Date of check |
| table_name | STRING | REQUIRED | Table being checked |
| check_name | STRING | REQUIRED | Name of the check |
| check_type | STRING | REQUIRED | Type (assertion, threshold, anomaly) |
| passed | BOOLEAN | REQUIRED | Whether check passed |
| failed_records | INT64 | NULLABLE | Number of failed records |
| error_message | STRING | NULLABLE | Error details if failed |
| check_timestamp | TIMESTAMP | REQUIRED | When check was run |

**Partitioning**: Partitioned by `check_date`

**Example Checks**:
```sql
-- Check: Spend should not be negative
INSERT INTO data_quality_checks
SELECT 
  GENERATE_UUID() AS check_id,
  CURRENT_DATE() AS check_date,
  'marketing_metrics_daily' AS table_name,
  'spend_not_negative' AS check_name,
  'assertion' AS check_type,
  CASE WHEN COUNT(*) = 0 THEN TRUE ELSE FALSE END AS passed,
  COUNT(*) AS failed_records,
  NULL AS error_message,
  CURRENT_TIMESTAMP() AS check_timestamp
FROM marketing_metrics_daily
WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND spend < 0

-- Check: ROAS should not exceed 100 (likely data error)
INSERT INTO data_quality_checks
SELECT 
  GENERATE_UUID() AS check_id,
  CURRENT_DATE() AS check_date,
  'marketing_metrics_daily' AS table_name,
  'roas_reasonable' AS check_name,
  'threshold' AS check_type,
  CASE WHEN COUNT(*) = 0 THEN TRUE ELSE FALSE END AS passed,
  COUNT(*) AS failed_records,
  NULL AS error_message,
  CURRENT_TIMESTAMP() AS check_timestamp
FROM marketing_metrics_daily
WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND roas > 100
```

---

## Indexing Strategy

### Partitioning

All tables are partitioned by date to:
- Reduce query costs (only scan relevant partitions)
- Improve query performance (partition pruning)
- Simplify data retention (drop old partitions)

### Clustering

Tables are clustered by frequently filtered columns:
- `client_id`: Most queries filter by client
- `channel`: Briefings filter by channel
- `campaign_id`: Analysts drill down by campaign

Clustering improves query performance by:
- Reducing the amount of data scanned
- Enabling efficient filtering and aggregation
- Improving JOIN performance

---

## Data Retention Policy

| Layer | Retention | Reason |
|-------|-----------|--------|
| Raw | 90 days | Audit and debugging, but storage costs add up |
| Staging | 1 year | Historical analysis and trend detection |
| Mart | 2 years | Long-term performance analysis |
| Exchange Rates | 2 years | Historical currency conversion audit |
| Ingestion Logs | 90 days | Operational debugging |
| Data Quality Checks | 1 year | Quality trend analysis |

**Implementation**:
```sql
-- Set partition expiration on raw tables
ALTER TABLE raw_meta_ads
SET OPTIONS (
  partition_expiration_days = 90
);

-- Set partition expiration on ingestion logs
ALTER TABLE ingestion_logs
SET OPTIONS (
  partition_expiration_days = 90
);
```

---

## Cost Estimation

### Storage Costs (BigQuery)

**Assumptions**:
- 50 clients
- 4 channels per client
- 365 days of data
- Average row size: 1 KB

**Calculations**:
- Raw layer: 50 clients × 4 channels × 365 days × 1 KB = ~73 MB (90 days retention = ~18 MB)
- Staging layer: 50 clients × 4 channels × 365 days × 1 KB = ~73 MB
- Mart layer: 50 clients × 4 channels × 365 days × 1 KB = ~73 MB
- Total storage: ~164 MB
- Cost: ~$0.01/month (at $0.02 per GB/month)

### Query Costs (BigQuery)

**Daily Operations**:
- Ingestion queries: ~100 MB scanned per day
- Transformation queries: ~50 MB scanned per day
- Briefing generation: ~10 MB scanned per day
- Analyst queries: ~500 MB scanned per day (estimated)
- Total: ~660 MB/day = ~20 GB/month
- Cost: ~$0.10/month (at $5 per TB)

**Total Estimated Cost**: ~$0.11/month for storage and queries

---

## Schema Evolution

### Adding a New Channel

To add a new marketing channel (e.g., TikTok):

1. **Create raw table**:
```sql
CREATE TABLE raw_tiktok (
  ingestion_date DATE,
  client_id STRING,
  data_date DATE,
  raw_json JSON,
  ingestion_timestamp TIMESTAMP,
  api_version STRING
)
PARTITION BY ingestion_date
CLUSTER BY client_id;
```

2. **Create staging table**:
```sql
CREATE TABLE stg_tiktok (
  date DATE,
  client_id STRING,
  campaign_id STRING,
  campaign_name STRING,
  spend FLOAT64,
  currency STRING,
  impressions INT64,
  clicks INT64,
  conversions INT64,
  revenue FLOAT64,
  ingestion_timestamp TIMESTAMP
)
PARTITION BY date
CLUSTER BY client_id, campaign_id;
```

3. **Update mart transformation**:
Add TikTok to the UNION query in `marketing_metrics_daily.sql`

4. **Update configuration**:
Add `tiktok` to `enabled_channels` in `clients.yaml`

### Adding a New Metric

To add a new metric (e.g., `video_views`):

1. **Add column to staging tables**:
```sql
ALTER TABLE stg_meta_ads
ADD COLUMN video_views INT64;
```

2. **Add column to mart table**:
```sql
ALTER TABLE marketing_metrics_daily
ADD COLUMN video_views INT64;
```

3. **Update transformation logic**:
```sql
SUM(video_views) AS video_views
```

4. **Update briefing template**:
Add video_views to the Jinja2 template

---

## Security and Access Control

### Service Account Permissions

**Ingestion Service Account**:
- `bigquery.dataEditor` on raw tables (write access)
- `bigquery.dataViewer` on raw tables (read for validation)

**Transformation Service Account**:
- `bigquery.dataViewer` on raw tables (read)
- `bigquery.dataEditor` on staging and mart tables (write)

**Briefing Service Account**:
- `bigquery.dataViewer` on mart tables (read only)

**Analyst Access**:
- `bigquery.dataViewer` on mart tables (read only)
- `bigquery.jobUser` (ability to run queries)

### Row-Level Security (Future Enhancement)

For multi-tenant scenarios, implement row-level security:
```sql
CREATE ROW ACCESS POLICY client_access
ON marketing_metrics_daily
GRANT TO ('user:analyst1@company.com')
FILTER USING (client_id = 'acme_corp');
```

---

## Monitoring and Alerts

### Query Performance Monitoring

```sql
-- Monitor query costs
SELECT 
  DATE(creation_time) AS query_date,
  COUNT(*) AS query_count,
  SUM(total_bytes_processed) / POW(1024, 4) AS total_tb_processed,
  SUM(total_bytes_processed) / POW(1024, 4) * 5 AS estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS
WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY query_date
ORDER BY query_date
```

### Data Freshness Monitoring

```sql
-- Check if data is fresh (ingested within last 24 hours)
SELECT 
  channel,
  MAX(ingestion_timestamp) AS last_ingestion,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(ingestion_timestamp), HOUR) AS hours_since_ingestion
FROM marketing_metrics_daily
WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
GROUP BY channel
HAVING hours_since_ingestion > 24
```

---

## Summary

The data model is designed for:

1. **Auditability**: Raw tables preserve original API responses for 90 days
2. **Data Quality**: Staging tables clean and validate data before aggregation
3. **Performance**: Mart tables are partitioned and clustered for fast queries
4. **Flexibility**: Schema can evolve to add new channels and metrics
5. **Cost Efficiency**: Partitioning and clustering minimize query costs
6. **Security**: Role-based access control ensures data protection

All tables follow consistent naming conventions and include comprehensive documentation for analysts to query and verify metrics independently.
