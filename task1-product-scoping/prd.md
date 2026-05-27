# Product Requirements Document: Marketing Performance Reporter

## 1. Product Vision

The Marketing Performance Reporter is an internal tool that eliminates manual data aggregation and ensures every analyst gets consistent, timely answers to the question: "How is our marketing performing across channels, and where should we focus?"

## 2. User Personas

### Primary User (v1): Internal Analyst / Account Manager

**Profile**: 
- Manages 3-5 client brands
- Spends 2-4 hours daily pulling and analyzing marketing data
- Comfortable with SQL and basic Python
- Needs to answer client and leadership questions quickly
- Values accuracy and transparency over polish

**Pain Points**:
- Logs into 4-6 different platforms every morning
- Manually copies numbers into spreadsheets
- Different analysts produce different answers to the same question
- When they're unavailable, no one can pull the report
- Clients ask "why is this number different from what I see in Meta?"

**Goals**:
- Get a consistent daily summary without manual work
- Trust the numbers enough to use them in client meetings
- Quickly identify which channels are performing and which need attention
- Verify any metric by drilling into raw data

### Secondary User (v2): Client-Facing Brand Manager

**Profile**:
- Presents marketing performance to clients weekly/monthly
- Needs high-level summaries, not raw data
- Values clear narratives and visual charts
- Non-technical background

**Pain Points**:
- Relies on analysts to pull data for client meetings
- Needs answers faster than analysts can provide
- Wants to self-serve basic performance questions

**Goals**:
- Get automated client-ready reports
- Understand performance trends without digging into data
- Answer "what happened?" and "what should we do?"

### Tertiary User (v3): Internal Leadership

**Profile**:
- Oversees all client accounts
- Allocates team resources based on client needs
- Needs rollup views across all clients

**Pain Points**:
- No single view of how all clients are performing
- Difficult to identify which clients need more attention
- Cannot easily compare performance across client portfolios

**Goals**:
- See aggregate performance across all clients
- Identify underperforming accounts early
- Make data-driven resource allocation decisions

## 3. User Stories

### v1: Internal Analyst

**US-1.1**: As an analyst, I want to receive a daily morning briefing at 9 AM so that I don't have to manually pull data from multiple platforms.

**Acceptance Criteria**:
- Briefing is delivered by 9:00 AM local time every weekday
- Briefing is sent via Slack to a designated channel
- Briefing is also sent via email as a backup
- Briefing includes data from the previous day

**US-1.2**: As an analyst, I want to see a 7-day vs. 7-day comparison so that I can identify trends without day-of-week noise.

**Acceptance Criteria**:
- Briefing shows metrics for the last 7 days (days 1-7)
- Briefing shows metrics for the previous 7 days (days 8-14)
- Comparison includes: spend, revenue, ROAS, CPA, CTR, CVR
- Percentage change is calculated and displayed

**US-1.3**: As an analyst, I want to see a channel-by-channel breakdown for the top 3 channels by spend so that I can understand which platforms are driving performance.

**Acceptance Criteria**:
- Top 3 channels are identified by total spend in the last 7 days
- Each channel shows: spend, revenue, ROAS, CPA
- Channels are ranked by spend (highest first)
- Supported channels: Meta, Google Ads, Shopify (if applicable), GA4

**US-1.4**: As an analyst, I want to see trend indicators (up/down arrows) so that I can quickly scan which metrics are improving or declining.

**Acceptance Criteria**:
- Green up arrow for positive changes (>5% improvement)
- Red down arrow for negative changes (>5% decline)
- Gray horizontal arrow for stable metrics (within ±5%)
- Arrows appear next to each metric in the channel breakdown

**US-1.5**: As an analyst, I want to see a one-sentence narrative explaining the most notable change so that I understand the context without digging into data.

**Acceptance Criteria**:
- One sentence identifies the largest percentage change
- Sentence includes: metric name, percentage change, and likely cause (if detectable)
- Example: "ROAS dropped 15% on Meta due to a CPM spike"
- If no notable changes, sentence says: "Performance stable across all channels"

**US-1.6**: As an analyst, I want to see anomaly flags when metrics move beyond expected thresholds so that I can investigate issues immediately.

**Acceptance Criteria**:
- Flag appears when spend changes by >50% day-over-day
- Flag appears when ROAS drops below 1.0
- Flag appears when a channel has zero spend for 24+ hours
- Flag includes metric name, current value, and threshold breached
- Example: "ANOMALY: Meta spend is $0 (expected ~$5,000). Possible cause: campaign paused"

**US-1.7**: As an analyst, I want to see a data provenance note so that I know when the data was last updated and where it came from.

**Acceptance Criteria**:
- Note shows: "Data as of [timestamp in ISO 8601 format]"
- Note shows source for each metric type:
  - Spend: Meta/Google Ads API
  - Revenue: Shopify API
  - Clicks: Meta/Google Ads API
  - Sessions: GA4 API
- Note states: "These numbers will not match across platforms due to attribution differences"

**US-1.8**: As an analyst, I want to verify any metric by querying the underlying BigQuery table so that I can audit the data if needed.

**Acceptance Criteria**:
- Briefing includes a link to the BigQuery table: `marketing_metrics_daily`
- Briefing includes example query: `SELECT * FROM marketing_metrics_daily WHERE date = '[yesterday]' AND channel = 'meta'`
- Table is partitioned by date and clustered by client_id for fast queries
- Documentation explains how to query the table

**US-1.9**: As an analyst, I want the tool to handle API downtime gracefully so that I know when data is incomplete rather than seeing zeros.

**Acceptance Criteria**:
- If Meta API is unavailable, briefing shows: "Meta data incomplete - retrying"
- If Google Ads API is unavailable, briefing shows: "Google Ads data incomplete - retrying"
- Briefing is still sent with available data
- Incomplete channels are clearly marked
- Retry logic attempts 3 times with exponential backoff

**US-1.10**: As an analyst, I want to add a new client by updating a configuration file so that I don't need engineering support to onboard a new account.

**Acceptance Criteria**:
- Configuration file exists: `clients.yaml`
- File includes: client_id, client_name, currency, timezone, enabled channels
- Adding a new client requires only editing the YAML file
- New client appears in the next day's briefing
- Documentation explains the YAML format

**US-1.11**: As an analyst, I want all metrics to use standardized definitions so that every analyst gets the same numbers.

**Acceptance Criteria**:
- Glossary document exists with definitions for all metrics
- Definitions are consistent across all clients and channels
- Glossary is accessible via a link in the briefing
- Example definitions:
  - Revenue: "Shopify purchases attributed to the campaign within a 7-day click window"
  - ROAS: "Revenue divided by spend, expressed as a ratio (e.g., 4.0 means $4 revenue per $1 spent)"
  - CPA: "Spend divided by conversions, expressed in dollars"

**US-1.12**: As an analyst, I want to see currency-normalized metrics so that I can compare performance across clients in different countries.

**Acceptance Criteria**:
- All spend and revenue are converted to a base currency (default: USD)
- Configuration file allows changing the base currency
- Original currency is stored in the raw table
- Conversion rate is logged for audit purposes

### v2: Client-Facing Brand Manager

**US-2.1**: As a brand manager, I want to receive a weekly client-ready report so that I can use it in client meetings without modification.

**Acceptance Criteria**:
- Report is generated every Monday at 8 AM
- Report includes the previous week's performance
- Report has a clean, branded format (PDF)
- Report includes charts showing trends over the last 4 weeks
- Report excludes internal-only fields (e.g., raw BigQuery queries)

**US-2.2**: As a brand manager, I want to see a high-level summary with recommendations so that I can answer "what should we do next?"

**Acceptance Criteria**:
- Summary includes: "Top performing channel" and "Underperforming channel"
- Recommendations are rule-based (e.g., "Consider increasing spend on Meta given strong ROAS")
- Recommendations are conservative and data-backed
- Summary avoids technical jargon

### v3: Internal Leadership

**US-3.1**: As leadership, I want to see a monthly rollup across all clients so that I can understand overall portfolio performance.

**Acceptance Criteria**:
- Rollup report is generated on the 1st of each month
- Report shows total spend, revenue, and ROAS across all clients
- Report identifies top 3 and bottom 3 performing clients
- Report includes month-over-month trend

**US-3.2**: As leadership, I want to identify underperforming accounts early so that I can allocate resources proactively.

**Acceptance Criteria**:
- Alert is sent when a client's ROAS drops below 2.0 for 14 consecutive days
- Alert includes: client name, current ROAS, trend direction
- Alert is sent to a designated leadership Slack channel

## 4. Functional Requirements

### 4.1 Data Ingestion

**FR-1.1**: The system shall pull data from Meta Marketing API daily at 6:00 AM UTC.

**FR-1.2**: The system shall pull data from Google Ads API daily at 6:00 AM UTC.

**FR-1.3**: The system shall pull data from Shopify API daily at 6:00 AM UTC.

**FR-1.4**: The system shall pull data from GA4 API daily at 6:00 AM UTC.

**FR-1.5**: The system shall implement exponential backoff retry logic (3 attempts with 1min, 5min, 15min delays).

**FR-1.6**: The system shall store raw API responses in BigQuery raw tables without modification.

**FR-1.7**: The system shall log all API calls, including success/failure status and response time.

**FR-1.8**: The system shall handle API rate limits by respecting rate limit headers and queuing requests.

### 4.2 Data Transformation

**FR-2.1**: The system shall clean and normalize raw data in staging tables (e.g., standardize date formats, convert currencies).

**FR-2.2**: The system shall calculate derived metrics in mart tables using SQL transformations:
- ROAS = revenue / spend
- CPA = spend / conversions
- CTR = clicks / impressions
- CVR = conversions / clicks

**FR-2.3**: The system shall handle division-by-zero errors by setting derived metrics to NULL when denominators are zero.

**FR-2.4**: The system shall align all timestamps to a canonical timezone (UTC) before aggregation.

**FR-2.5**: The system shall use idempotent loads (re-running yesterday's job overwrites rather than appends).

**FR-2.6**: The system shall validate data quality before loading into mart tables (e.g., spend should not be negative, ROAS should not exceed 100).

### 4.3 Briefing Generation

**FR-3.1**: The system shall generate a daily briefing at 9:00 AM local time.

**FR-3.2**: The system shall use a Jinja2 template to format the briefing message.

**FR-3.3**: The system shall calculate 7-day vs. 7-day comparisons using the mart table.

**FR-3.4**: The system shall identify the top 3 channels by spend for each client.

**FR-3.5**: The system shall generate trend indicators based on percentage change thresholds (±5%).

**FR-3.6**: The system shall generate a one-sentence narrative using rule-based logic to identify the largest percentage change.

**FR-3.7**: The system shall flag anomalies when metrics breach predefined thresholds.

**FR-3.8**: The system shall include a data provenance note with update timestamp and source of truth.

### 4.4 Delivery

**FR-4.1**: The system shall send the briefing to a designated Slack channel via Slack API.

**FR-4.2**: The system shall send the briefing via email to a distribution list as a backup.

**FR-4.3**: The system shall support Microsoft Teams as an alternative delivery channel (configuration-based).

**FR-4.4**: The system shall log delivery success/failure for audit purposes.

**FR-4.5**: The system shall retry failed deliveries up to 3 times with 5-minute delays.

### 4.5 Configuration and Onboarding

**FR-5.1**: The system shall use a YAML configuration file (`clients.yaml`) to define client settings.

**FR-5.2**: The configuration file shall include: client_id, client_name, currency, timezone, enabled channels, and delivery preferences.

**FR-5.3**: The system shall validate the configuration file on startup and reject invalid entries.

**FR-5.4**: The system shall support adding new clients without code changes.

**FR-5.5**: The system shall support enabling/disabling channels per client.

### 4.6 Monitoring and Alerting

**FR-6.1**: The system shall log all ingestion, transformation, and delivery activities to a centralized log file.

**FR-6.2**: The system shall send an alert to a designated Slack channel when a data source is unavailable for 24+ hours.

**FR-6.3**: The system shall send an alert when data quality checks fail (e.g., negative spend, ROAS > 100).

**FR-6.4**: The system shall expose a health check endpoint that returns the status of the last run.

## 5. Non-Functional Requirements

### 5.1 Performance

**NFR-1.1**: Data ingestion shall complete within 30 minutes for up to 50 clients.

**NFR-1.2**: Data transformation shall complete within 10 minutes for 30 days of data.

**NFR-1.3**: Briefing generation shall complete within 2 minutes.

**NFR-1.4**: Briefing delivery shall complete within 1 minute.

### 5.2 Reliability

**NFR-2.1**: The system shall achieve 99% uptime during business hours (9 AM - 6 PM local time).

**NFR-2.2**: The system shall handle API failures gracefully without crashing.

**NFR-2.3**: The system shall recover automatically from transient errors (e.g., network timeouts).

### 5.3 Scalability

**NFR-3.1**: The system shall support up to 50 clients without performance degradation.

**NFR-3.2**: The system shall support up to 10 channels per client.

**NFR-3.3**: The system shall handle 30 days of historical data without manual cleanup.

### 5.4 Security

**NFR-4.1**: API credentials shall be stored in environment variables, not in code or configuration files.

**NFR-4.2**: BigQuery access shall be restricted to authorized service accounts.

**NFR-4.3**: Slack API tokens shall be rotated every 90 days.

**NFR-4.4**: All API calls shall use HTTPS.

### 5.5 Maintainability

**NFR-5.1**: Code shall follow PEP 8 style guidelines.

**NFR-5.2**: SQL transformations shall be version-controlled and compatible with dbt.

**NFR-5.3**: Documentation shall be updated whenever configuration or logic changes.

**NFR-5.4**: The system shall include unit tests for all transformation logic.

## 6. Success Metrics

### 6.1 Adoption

- 80% of analysts open and reference the daily briefing within the first month
- 90% of analysts report the briefing saves them time in a post-launch survey

### 6.2 Efficiency

- Analysts spend less than 5 minutes reviewing the daily briefing instead of 30+ minutes pulling data manually
- Time-to-answer for "how is marketing performing?" drops from 2-4 hours to under 10 minutes

### 6.3 Consistency

- 100% of analysts get the same numbers for the same time period
- Zero discrepancies between briefings sent to different analysts

### 6.4 Trust

- 90% of analysts report they trust the numbers enough to use them in client meetings
- Analysts can verify any metric by querying BigQuery within 2 minutes

### 6.5 Reliability

- Briefing is delivered by 9:00 AM on 95% of weekdays
- Incomplete data is flagged rather than showing zeros

## 7. Risks and Mitigations

### 7.1 Data Quality Risks

**Risk**: API responses contain errors or missing data.

**Mitigation**: Implement data quality checks before loading into mart tables. Flag incomplete data in the briefing.

### 7.2 Adoption Risks

**Risk**: Analysts don't trust the numbers and continue using manual processes.

**Mitigation**: Provide clear documentation, data provenance, and BigQuery access for verification. Run the tool in parallel with manual processes for 2 weeks to build trust.

### 7.3 Technical Risks

**Risk**: API changes break the ingestion pipeline.

**Mitigation**: Monitor API changelogs. Implement schema validation. Break loudly and notify the team when fields are deprecated.

### 7.4 Scalability Risks

**Risk**: Adding more clients causes performance degradation.

**Mitigation**: Use BigQuery partitioning and clustering. Optimize queries. Monitor query costs and performance.

## 8. Dependencies

### 8.1 External Dependencies

- Meta Marketing API access with read permissions
- Google Ads API access with read permissions
- Shopify API access with read permissions
- GA4 API access with read permissions
- BigQuery project with write access
- Slack workspace with API bot token
- Email service (e.g., SendGrid, SMTP server)

### 8.2 Internal Dependencies

- Analyst team agreement on metric definitions
- Client configuration data (client_id, currency, timezone)
- API credentials for all data sources
- Slack channel designation for briefing delivery
- Email distribution list for briefing delivery

## 9. Out of Scope

The following features are valuable but excluded from v1:

- Predictive modeling or ML recommendations (requires established data quality)
- Real-time streaming data (daily batches are sufficient for marketing decisions)
- Self-service report builder (reintroduces inconsistency)
- Multi-touch attribution modeling (research project, not a v1 feature)
- Client-facing branded reports (v2 feature once analysts trust the data)
- Custom dashboard UI (v2 feature for on-demand drill-downs)
- Advanced anomaly detection using ML (rule-based detection is sufficient for v1)
- Automated recommendations (v1 provides data, not advice)

## 10. Future Enhancements (v2+)

- Simple Metabase or Looker Studio dashboard for on-demand drill-downs
- Client-facing PDF reports with charts and branding
- Data quality monitoring using Soda Core or Great Expectations
- Incremental refresh logic for attribution window restatements
- Alerting when a data source is down for 24+ hours
- Multi-touch attribution modeling (research phase)
- Predictive recommendations based on historical performance
- Support for additional channels (TikTok, LinkedIn, Twitter)
- Mobile app for viewing briefings on-the-go
