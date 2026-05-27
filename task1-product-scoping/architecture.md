# System Architecture: Marketing Performance Reporter

## 1. Architecture Overview

The Marketing Performance Reporter follows an ELT (Extract, Load, Transform) architecture pattern. This approach loads raw data first, then transforms it within the data warehouse, providing flexibility and auditability.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Data Sources Layer                              │
├─────────────────────────────────────────────────────────────────────────┤
│  Meta Marketing API  │  Google Ads API  │  Shopify API  │  GA4 API      │
└──────────┬───────────┴────────┬─────────┴───────┬───────┴──────┬────────┘
           │                    │                 │              │
           └────────────────────┴─────────────────┴──────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │    Ingestion Layer (Python)    │
                    │  - API Clients                 │
                    │  - Retry Logic                 │
                    │  - Rate Limiting               │
                    │  - Daily Schedule (6:00 AM)    │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │   Data Warehouse (BigQuery)    │
                    │                                │
                    │  ┌──────────────────────────┐ │
                    │  │  Raw Layer               │ │
                    │  │  - raw_meta_ads          │ │
                    │  │  - raw_google_ads        │ │
                    │  │  - raw_shopify           │ │
                    │  │  - raw_ga4               │ │
                    │  └──────────────────────────┘ │
                    │              │                 │
                    │  ┌──────────▼───────────────┐ │
                    │  │  Staging Layer           │ │
                    │  │  - stg_meta_ads          │ │
                    │  │  - stg_google_ads        │ │
                    │  │  - stg_shopify           │ │
                    │  │  - stg_ga4               │ │
                    │  └──────────┬───────────────┘ │
                    │             │                  │
                    │  ┌─────────▼────────────────┐ │
                    │  │  Mart Layer              │ │
                    │  │  - marketing_metrics_daily│ │
                    │  └─────────┬────────────────┘ │
                    └────────────┼──────────────────┘
                                 │
                    ┌────────────▼────────────────┐
                    │  Transformation Layer (SQL)  │
                    │  - Metric Calculations       │
                    │  - Currency Normalization    │
                    │  - Timezone Alignment        │
                    └────────────┬────────────────┘
                                 │
                    ┌────────────▼────────────────┐
                    │  Briefing Generation (Jinja2)│
                    │  - 7-day Comparisons         │
                    │  - Trend Indicators          │
                    │  - Anomaly Detection         │
                    │  - Narrative Generation      │
                    └────────────┬────────────────┘
                                 │
                    ┌────────────▼────────────────┐
                    │     Delivery Layer           │
                    │  - Slack API                 │
                    │  - Email (SMTP/SendGrid)     │
                    │  - Microsoft Teams (optional)│
                    └─────────────────────────────┘
```

## 2. Component Details

### 2.1 Data Sources Layer

**Purpose**: External marketing platforms that provide raw data.

**Supported Sources (v1)**:
- **Meta Marketing API**: Ad spend, impressions, clicks, conversions, revenue
- **Google Ads API**: Ad spend, impressions, clicks, conversions, revenue
- **Shopify API**: E-commerce revenue and order data
- **GA4 API**: Website sessions, user behavior, conversion events

**API Access Requirements**:
- Meta: Marketing API read access with ads_management permission
- Google Ads: Google Ads API access with read-only scope
- Shopify: Admin API access with read_orders and read_products scopes
- GA4: Google Analytics Data API access with read-only scope

**Data Freshness**: All APIs are queried daily at 6:00 AM UTC. Data from the previous day is pulled, with a 24-hour delay to ensure attribution windows have settled.

### 2.2 Ingestion Layer

**Purpose**: Extract data from external APIs and load it into the data warehouse.

**Technology**: Python 3.11+ with the following libraries:
- `requests` for HTTP calls
- `google-cloud-bigquery` for BigQuery interactions
- `tenacity` for retry logic
- `pyyaml` for configuration parsing

**Key Features**:

1. **API Clients**: Separate client classes for each data source, handling authentication, pagination, and response parsing.

2. **Retry Logic**: Exponential backoff with jitter for transient failures:
   - Attempt 1: Immediate
   - Attempt 2: Wait 1 minute
   - Attempt 3: Wait 5 minutes
   - Attempt 4: Wait 15 minutes
   - After 4 failures: Log error and mark data as incomplete

3. **Rate Limiting**: Respect API rate limits by:
   - Reading rate limit headers from responses
   - Implementing request queuing when limits are approached
   - Spreading requests across the ingestion window (6:00 AM - 6:30 AM UTC)

4. **Idempotency**: Each ingestion run is idempotent. Re-running a job for a specific date overwrites existing data rather than appending duplicates.

5. **Logging**: All API calls are logged with:
   - Timestamp
   - API endpoint
   - Response status code
   - Response time (milliseconds)
   - Success/failure status

**Directory Structure**:
```
ingestion/
├── clients/
│   ├── meta_client.py
│   ├── google_ads_client.py
│   ├── shopify_client.py
│   └── ga4_client.py
├── config/
│   └── clients.yaml
├── utils/
│   ├── retry.py
│   └── rate_limiter.py
└── main.py
```

### 2.3 Data Warehouse (BigQuery)

**Purpose**: Central storage for all marketing data, organized in three layers.

**Project**: `marketing-performance-reporter` (or client-specific project)

**Dataset**: `marketing_data`

**Table Naming Convention**:
- Raw layer: `raw_{source}` (e.g., `raw_meta_ads`)
- Staging layer: `stg_{source}` (e.g., `stg_meta_ads`)
- Mart layer: `marketing_metrics_daily`

#### Raw Layer

**Purpose**: Store unmodified API responses for audit and debugging.

**Schema**: Flexible JSON-based schema to accommodate API changes without breaking the pipeline.

**Example Table**: `raw_meta_ads`

| Column | Type | Description |
|--------|------|-------------|
| ingestion_date | DATE | Date when data was ingested |
| client_id | STRING | Client identifier |
| data_date | DATE | Date the data represents |
| raw_json | JSON | Full API response |
| ingestion_timestamp | TIMESTAMP | Exact time of ingestion |

**Partitioning**: Partitioned by `ingestion_date` for efficient cleanup of old data.

**Retention**: 90 days (configurable). Older data is automatically deleted.

#### Staging Layer

**Purpose**: Clean and normalize raw data into consistent schemas.

**Schema**: Standardized columns with consistent data types.

**Example Table**: `stg_meta_ads`

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Reporting date |
| client_id | STRING | Client identifier |
| campaign_id | STRING | Campaign identifier |
| campaign_name | STRING | Campaign name |
| spend | FLOAT64 | Spend in original currency |
| currency | STRING | Original currency code |
| impressions | INT64 | Total impressions |
| clicks | INT64 | Total clicks |
| conversions | INT64 | Total conversions |
| revenue | FLOAT64 | Revenue in original currency |
| ingestion_timestamp | TIMESTAMP | When data was ingested |

**Partitioning**: Partitioned by `date`.

**Clustering**: Clustered by `client_id` for fast client-specific queries.

**Transformations**:
- Parse JSON from raw layer
- Standardize date formats to ISO 8601
- Convert currency codes to uppercase
- Handle NULL values (replace with 0 for numeric fields)

#### Mart Layer

**Purpose**: Aggregated business metrics ready for analysis and reporting.

**Table**: `marketing_metrics_daily`

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Reporting date |
| client_id | STRING | Client identifier |
| channel | STRING | Marketing channel (meta, google_ads, shopify, ga4) |
| spend | FLOAT64 | Total spend in base currency (USD) |
| impressions | INT64 | Total impressions |
| clicks | INT64 | Total clicks |
| conversions | INT64 | Total conversions |
| revenue | FLOAT64 | Revenue in base currency (USD) |
| roas | FLOAT64 | Return on ad spend (revenue / spend) |
| cpa | FLOAT64 | Cost per acquisition (spend / conversions) |
| ctr | FLOAT64 | Click-through rate (clicks / impressions) |
| cvr | FLOAT64 | Conversion rate (conversions / clicks) |
| spend_currency | STRING | Original currency code |
| revenue_currency | STRING | Original currency code |
| ingestion_timestamp | TIMESTAMP | When data was last updated |

**Partitioning**: Partitioned by `date` for efficient date-range queries.

**Clustering**: Clustered by `client_id` and `channel` for fast filtering.

**Derived Metrics**:
```sql
-- ROAS calculation with division-by-zero handling
CASE 
  WHEN spend > 0 THEN revenue / spend 
  ELSE NULL 
END AS roas

-- CPA calculation
CASE 
  WHEN conversions > 0 THEN spend / conversions 
  ELSE NULL 
END AS cpa

-- CTR calculation
CASE 
  WHEN impressions > 0 THEN clicks / impressions 
  ELSE NULL 
END AS ctr

-- CVR calculation
CASE 
  WHEN clicks > 0 THEN conversions / clicks 
  ELSE NULL 
END AS cvr
```

### 2.4 Transformation Layer

**Purpose**: Calculate derived metrics and apply business logic.

**Technology**: SQL transformations compatible with dbt (data build tool).

**Key Transformations**:

1. **Currency Normalization**: Convert all spend and revenue to base currency (USD) using daily exchange rates from a currency API.

2. **Timezone Alignment**: Convert all timestamps to UTC before aggregation to ensure consistent date boundaries.

3. **Metric Calculations**: Calculate ROAS, CPA, CTR, and CVR using the formulas above.

4. **Data Quality Checks**: Validate that:
   - Spend is not negative
   - ROAS does not exceed 100 (likely data error)
   - Impressions, clicks, and conversions are non-negative integers

**Directory Structure** (dbt-compatible):
```
transformations/
├── models/
│   ├── staging/
│   │   ├── stg_meta_ads.sql
│   │   ├── stg_google_ads.sql
│   │   ├── stg_shopify.sql
│   │   └── stg_ga4.sql
│   └── marts/
│       └── marketing_metrics_daily.sql
├── tests/
│   ├── assert_spend_not_negative.sql
│   └── assert_roas_reasonable.sql
└── dbt_project.yml
```

### 2.5 Briefing Generation Layer

**Purpose**: Generate human-readable daily briefings from mart data.

**Technology**: Python with Jinja2 templating.

**Key Components**:

1. **Comparison Calculator**: Calculates 7-day vs. 7-day comparisons:
   ```python
   current_period = query_metrics(start_date=today - 7, end_date=today - 1)
   previous_period = query_metrics(start_date=today - 14, end_date=today - 8)
   comparison = calculate_percentage_change(current_period, previous_period)
   ```

2. **Trend Indicator Generator**: Assigns trend arrows based on percentage change:
   - Green up arrow (↑): >5% improvement
   - Red down arrow (↓): >5% decline
   - Gray horizontal arrow (→): within ±5%

3. **Anomaly Detector**: Flags metrics that breach thresholds:
   - Spend changes by >50% day-over-day
   - ROAS drops below 1.0
   - Channel has zero spend for 24+ hours
   - Any metric is NULL when it should have data

4. **Narrative Generator**: Creates a one-sentence summary:
   ```python
   largest_change = find_largest_percentage_change(metrics)
   narrative = f"{largest_change.metric} {largest_change.direction} {largest_change.percentage}% on {largest_change.channel}"
   if largest_change.cause:
       narrative += f" due to {largest_change.cause}"
   ```

5. **Template Renderer**: Uses Jinja2 to format the final briefing message:
   ```jinja2
   📊 Daily Marketing Briefing for {{ client_name }}
   Data as of {{ timestamp }} (UTC)
   
   Last 7 Days vs. Previous 7 Days:
   • Total Spend: ${{ current_spend }} ({{ spend_change }}%)
   • Total Revenue: ${{ current_revenue }} ({{ revenue_change }}%)
   • Overall ROAS: {{ current_roas }} ({{ roas_change }}%)
   
   Channel Breakdown (Top 3 by Spend):
   {% for channel in top_channels %}
   {{ channel.rank }}. {{ channel.name }}
      • Spend: ${{ channel.spend }} {{ channel.spend_trend }}
      • Revenue: ${{ channel.revenue }} {{ channel.revenue_trend }}
      • ROAS: {{ channel.roas }} {{ channel.roas_trend }}
      • CPA: ${{ channel.cpa }} {{ channel.cpa_trend }}
   {% endfor %}
   
   💡 {{ narrative }}
   
   {% if anomalies %}
   ⚠️  Anomalies Detected:
   {% for anomaly in anomalies %}
   • {{ anomaly.message }}
   {% endfor %}
   {% endif %}
   
   Data Sources:
   • Spend: Meta/Google Ads API
   • Revenue: Shopify API
   • Clicks: Meta/Google Ads API
   • Sessions: GA4 API
   
   Note: These numbers will not match across platforms due to attribution differences.
   
   To verify any metric, query BigQuery:
   SELECT * FROM marketing_metrics_daily 
   WHERE date = '{{ yesterday }}' AND channel = '{{ channel }}'
   ```

**Directory Structure**:
```
briefing/
├── templates/
│   └── daily_briefing.jinja2
├── generators/
│   ├── comparison.py
│   ├── trends.py
│   ├── anomalies.py
│   └── narrative.py
└── main.py
```

### 2.6 Delivery Layer

**Purpose**: Send briefings to designated channels (Slack, email, Teams).

**Technology**: Python with platform-specific API clients.

**Supported Channels**:

1. **Slack**:
   - Uses Slack API with bot token
   - Sends message to designated channel (e.g., `#marketing-performance`)
   - Supports markdown formatting
   - Includes "View in BigQuery" button linking to pre-filtered query

2. **Email**:
   - Uses SMTP or SendGrid API
   - Sends to distribution list (configured in `clients.yaml`)
   - HTML-formatted for better readability
   - Includes CSV attachment with raw data

3. **Microsoft Teams** (optional):
   - Uses Teams webhook URL
   - Sends adaptive card with formatted message
   - Supports action buttons for drill-downs

**Retry Logic**: If delivery fails, retry up to 3 times with 5-minute delays.

**Logging**: Log delivery success/failure, including:
- Timestamp
- Channel type (Slack/email/Teams)
- Recipient (channel name or email list)
- Success/failure status
- Error message (if failed)

**Directory Structure**:
```
delivery/
├── channels/
│   ├── slack.py
│   ├── email.py
│   └── teams.py
├── utils/
│   └── retry.py
└── main.py
```

## 3. Data Flow

### 3.1 Daily Ingestion Flow

```
1. Scheduler triggers ingestion at 6:00 AM UTC
   │
2. For each enabled client in clients.yaml:
   │
   ├─> Meta Client: Query Marketing API for yesterday's data
   │   └─> Load into raw_meta_ads
   │
   ├─> Google Ads Client: Query Google Ads API for yesterday's data
   │   └─> Load into raw_google_ads
   │
   ├─> Shopify Client: Query Shopify API for yesterday's orders
   │   └─> Load into raw_shopify
   │
   └─> GA4 Client: Query GA4 API for yesterday's sessions
       └─> Load into raw_ga4
   │
3. Transformation pipeline runs:
   │
   ├─> Staging: Clean and normalize raw data
   │   └─> Load into stg_* tables
   │
   └─> Mart: Calculate derived metrics
       └─> Load into marketing_metrics_daily
   │
4. Briefing generation runs at 9:00 AM local time:
   │
   ├─> Query mart table for last 7 days and previous 7 days
   ├─> Calculate comparisons and trends
   ├─> Detect anomalies
   ├─> Generate narrative
   └─> Render Jinja2 template
   │
5. Delivery:
   │
   ├─> Send to Slack channel
   ├─> Send to email distribution list
   └─> (Optional) Send to Teams channel
```

### 3.2 Error Handling Flow

```
Ingestion Error:
  ├─> Retry with exponential backoff (3 attempts)
  ├─> If all retries fail:
  │   ├─> Log error
  │   ├─> Mark channel as "incomplete"
  │   └─> Continue with other channels
  └─> Briefing flags incomplete data

Transformation Error:
  ├─> Log error with details
  ├─> Skip problematic records
  └─> Alert team via Slack

Delivery Error:
  ├─> Retry up to 3 times with 5-minute delays
  ├─> If all retries fail:
  │   ├─> Log error
  │   └─> Send alert to ops Slack channel
  └─> Briefing is still generated and available in BigQuery
```

## 4. Configuration

### 4.1 Client Configuration (`clients.yaml`)

```yaml
clients:
  - client_id: "acme_corp"
    client_name: "Acme Corporation"
    currency: "USD"
    timezone: "America/New_York"
    enabled_channels:
      - meta
      - google_ads
      - shopify
      - ga4
    delivery:
      slack:
        enabled: true
        channel: "#acme-marketing"
      email:
        enabled: true
        recipients:
          - "analyst1@company.com"
          - "analyst2@company.com"
      teams:
        enabled: false

  - client_id: "globex_inc"
    client_name: "Globex Inc."
    currency: "EUR"
    timezone: "Europe/London"
    enabled_channels:
      - meta
      - google_ads
    delivery:
      slack:
        enabled: true
        channel: "#globex-marketing"
      email:
        enabled: true
        recipients:
          - "analyst3@company.com"
      teams:
        enabled: false
```

### 4.2 Environment Variables

```bash
# BigQuery
BIGQUERY_PROJECT_ID=marketing-performance-reporter
BIGQUERY_DATASET=marketing_data
BIGQUERY_CREDENTIALS_PATH=/path/to/service-account.json

# Meta Marketing API
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_ACCESS_TOKEN=your_access_token
META_AD_ACCOUNT_ID=your_ad_account_id

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id

# Shopify API
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_access_token

# GA4 API
GA4_PROPERTY_ID=your_property_id
GA4_CREDENTIALS_PATH=/path/to/ga4-service-account.json

# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your_signing_secret

# Email (SendGrid)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=marketing-reporter@company.com

# Currency API (for currency conversion)
CURRENCY_API_KEY=your_currency_api_key
CURRENCY_BASE_CURRENCY=USD

# Scheduling
INGESTION_SCHEDULE="0 6 * * *"  # 6:00 AM UTC daily
BRIEFING_SCHEDULE="0 9 * * 1-5"  # 9:00 AM local time, weekdays only
```

## 5. Monitoring and Observability

### 5.1 Logging

All components log to a centralized log file (`logs/marketing_reporter.log`) with the following format:

```
[2024-01-15 06:00:00 UTC] [INFO] [ingestion.meta_client] Starting Meta API ingestion for client acme_corp
[2024-01-15 06:00:05 UTC] [INFO] [ingestion.meta_client] Meta API call successful: 200 OK, 150ms
[2024-01-15 06:00:05 UTC] [INFO] [ingestion.meta_client] Loaded 150 records into raw_meta_ads
[2024-01-15 06:30:00 UTC] [INFO] [transformation.staging] Staging transformation completed: 600 records
[2024-01-15 06:35:00 UTC] [INFO] [transformation.mart] Mart transformation completed: 12 records
[2024-01-15 09:00:00 UTC] [INFO] [briefing.generator] Generated briefing for client acme_corp
[2024-01-15 09:00:01 UTC] [INFO] [delivery.slack] Briefing delivered to #acme-marketing
```

**Log Levels**:
- DEBUG: Detailed debugging information (disabled in production)
- INFO: Normal operational messages
- WARNING: Non-critical issues (e.g., retry attempt)
- ERROR: Errors that prevent normal operation
- CRITICAL: System-level failures

### 5.2 Alerting

**Alert Triggers**:
- Data source unavailable for 24+ hours
- Data quality check fails (e.g., negative spend)
- Briefing delivery fails after 3 retries
- Ingestion takes longer than 30 minutes
- Transformation takes longer than 10 minutes

**Alert Channels**:
- Slack: `#marketing-reporter-ops` channel
- Email: `ops-team@company.com`

### 5.3 Health Check Endpoint

A simple HTTP endpoint (Flask or FastAPI) that returns the status of the last run:

```json
{
  "status": "healthy",
  "last_ingestion": "2024-01-15T06:30:00Z",
  "last_transformation": "2024-01-15T06:35:00Z",
  "last_briefing": "2024-01-15T09:00:01Z",
  "incomplete_channels": [],
  "errors": []
}
```

**Status Values**:
- `healthy`: All components completed successfully
- `degraded`: Some components failed but briefing was delivered
- `unhealthy`: Critical failure, briefing not delivered

## 6. Security Considerations

### 6.1 API Credentials

- All API credentials are stored in environment variables, not in code or configuration files.
- Service account JSON files are stored in a secure directory with restricted permissions (e.g., `/etc/secrets/`).
- Credentials are rotated every 90 days.

### 6.2 Data Access

- BigQuery access is restricted to authorized service accounts.
- Raw tables are read-only for transformation jobs.
- Mart tables are read-only for briefing generation.
- Analysts have read-only access to mart tables for verification queries.

### 6.3 Network Security

- All API calls use HTTPS.
- BigQuery API calls use VPC Service Controls (if applicable).
- Slack API calls use TLS 1.2+.

### 6.4 Audit Logging

- All API calls are logged with timestamps.
- All BigQuery queries are logged with query text and execution time.
- All briefing deliveries are logged with recipient information.

## 7. Deployment

### 7.1 Infrastructure

**Recommended**: Google Cloud Platform (GCP)

**Components**:
- **Compute**: Cloud Run (containerized Python application)
- **Scheduler**: Cloud Scheduler (triggers ingestion and briefing generation)
- **Storage**: BigQuery (data warehouse)
- **Monitoring**: Cloud Logging and Cloud Monitoring
- **Secrets**: Secret Manager (API credentials)

**Alternative**: Run on a dedicated VM or Kubernetes cluster if GCP is not preferred.

### 7.2 Containerization

Docker image for the application:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "marketing_reporter.main"]
```

### 7.3 CI/CD Pipeline

**Recommended**: GitHub Actions

**Pipeline Stages**:
1. **Lint**: Run `flake8` and `black` on Python code
2. **Test**: Run unit tests with `pytest`
3. **Build**: Build Docker image and push to Container Registry
4. **Deploy**: Deploy to Cloud Run (staging environment)
5. **Integration Test**: Run integration tests against staging
6. **Deploy to Production**: Deploy to production environment

## 8. Cost Estimation

### 8.1 BigQuery Costs

**Storage**: 
- 50 clients × 10 channels × 365 days × 1 KB per row = ~180 MB
- Cost: ~$0.01/month (negligible)

**Query**:
- Daily ingestion: ~100 MB scanned per day = ~3 GB/month
- Daily briefing: ~10 MB scanned per day = ~300 MB/month
- Analyst queries: ~1 GB/day = ~30 GB/month
- Cost: ~$0.15/month (at $5 per TB)

### 8.2 Compute Costs

**Cloud Run**:
- 2 CPU, 4 GB memory
- 30 minutes of ingestion per day
- 5 minutes of briefing generation per day
- Cost: ~$5/month

### 8.3 API Costs

**Currency API**: ~$10/month for daily exchange rates

**SendGrid**: Free tier for up to 100 emails/day

**Total Estimated Cost**: ~$15/month for 50 clients

## 9. Future Enhancements

### 9.1 v2: Dashboard Layer

Add a simple Metabase or Looker Studio dashboard for on-demand drill-downs:
- Connect to BigQuery mart tables
- Create pre-built reports for common queries
- Allow analysts to filter by client, channel, and date range

### 9.2 v2: Client-Facing Reports

Generate branded PDF reports for client meetings:
- Use a PDF generation library (e.g., ReportLab or WeasyPrint)
- Include charts showing trends over time
- Add client branding (logo, colors)
- Send via email on a weekly or monthly schedule

### 9.3 v3: Predictive Recommendations

Use historical data to generate rule-based recommendations:
- "Meta ROAS is 5.2, which is above the 4.0 threshold. Consider increasing spend."
- "Google Ads CPA has increased 30% week-over-week. Review campaign performance."

### 9.4 v3: Multi-Touch Attribution

Implement data-driven attribution modeling:
- Track user journeys across touchpoints
- Assign credit to each channel based on contribution
- Requires integration with a customer data platform (CDP)
