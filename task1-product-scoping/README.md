# Marketing Performance Reporter (Task 1: Product Scoping)

## Problem

Marketing teams managing multiple client brands face a daily challenge: answering "How is our marketing performing across channels, and where should we focus?" requires logging into Meta Ads Manager, Google Ads, Google Analytics, Shopify, and other platforms, then manually stitching numbers together into a coherent narrative.

This process is slow, inconsistent across team members, and creates key-person dependency. When the analyst who usually pulls the report is unavailable, the question goes unanswered.

## Solution

The Marketing Performance Reporter is an internal tool that automatically ingests data from marketing platforms, calculates standardized metrics, and delivers a daily summary to analysts. The tool does not replace existing platforms. It aggregates and narrates on top of them.

### Why analysts first

The primary user is the internal analyst or account manager. This choice is deliberate:

- Analysts feel the pain most directly since they do the manual work every day.
- They tolerate rough edges in a v1 tool better than external clients would.
- Once analyst workflows are smooth, generating client-facing reports becomes a natural extension.
- Building for clients first leads to customization requests and scope creep that undermine the core value.

### What the v1 tool delivers

A daily morning briefing (sent via Slack or email) containing:

- Marketing spend, revenue, and ROAS for the last 7 days compared to the previous 7 days.
- Channel-by-channel breakdown for the top 3 channels by spend.
- Trend indicators showing which channels are improving and which are declining.
- One-sentence narrative explaining the most notable change (for example: "ROAS dropped 15 percent on Meta due to a CPM spike").
- Anomaly flags when metrics move beyond expected thresholds.
- Data provenance note showing the last update time and source of truth for each metric.

## Architecture

The system follows an ELT (Extract, Load, Transform) pattern:

```
Data Sources            Ingestion              Warehouse              Presentation
(Meta, Google,    -->   (Python scripts  -->   (BigQuery)       -->   (Slack / Email)
 Shopify, GA4)          with API calls)        Raw, Staging,
                                               and Mart layers
```

### Components

1. **Ingestion Layer**: Python scripts that pull data from Meta Marketing API, Google Ads API, Shopify API, and GA4 API on a daily schedule. Implements exponential backoff for retries and handles API rate limits.

2. **Data Warehouse (BigQuery)**: Three layers of tables:
   - Raw: Unmodified API responses stored as-is.
   - Staging: Cleaned and normalized data with consistent schemas.
   - Mart: Aggregated business metrics (`marketing_metrics_daily` at one row per client per channel per day).

3. **Transformation Layer**: SQL-based transformations (compatible with dbt) that calculate derived metrics like ROAS, CPA, CTR, and CVR using standardized definitions.

4. **Delivery Layer**: Template-based message generation with pluggable delivery to Slack, email, or Microsoft Teams. Uses Jinja2 templates so the format can be adjusted without code changes.

### Data model

The core mart table `marketing_metrics_daily`:

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | The reporting date |
| client_id | STRING | Client identifier |
| channel | STRING | Marketing channel (meta, google_ads, etc.) |
| spend | FLOAT64 | Total spend in base currency |
| impressions | INT64 | Total impressions |
| clicks | INT64 | Total clicks |
| conversions | INT64 | Total conversions |
| revenue | FLOAT64 | Revenue attributed to the channel |
| roas | FLOAT64 | Return on ad spend (revenue / spend) |
| cpa | FLOAT64 | Cost per acquisition (spend / conversions) |
| ctr | FLOAT64 | Click-through rate (clicks / impressions) |
| cvr | FLOAT64 | Conversion rate (conversions / clicks) |

The table is partitioned by `date` and clustered by `client_id` for query efficiency.

## Edge Cases Handled

### Data ingestion
- **API downtime**: Retry with exponential backoff. The briefing flags incomplete data rather than showing zeros.
- **Schema drift**: Pipeline breaks loudly and notifies the team when an API field is deprecated.
- **Historical restatements**: Loads are idempotent. Re-running yesterday's job overwrites rather than appends.

### Data quality
- **Platform discrepancies**: The tool picks a source of truth per metric and documents it. Meta reports clicks, GA4 reports sessions, Shopify reports revenue. These numbers will not match, and the briefing states this explicitly.
- **Currency normalization**: All spend and revenue are converted to a configurable base currency.
- **Timezone alignment**: All timestamps are normalized to a canonical timezone (UTC or client local time) before aggregation.
- **Weekend and holiday patterns**: Comparisons use week-over-week or year-over-year windows to avoid false alarms from day-of-week effects.

### User experience
- **New client onboarding**: Adding a client is a configuration change, not a code change.
- **Zero data scenarios**: Shows "No spend detected" instead of division-by-zero errors in ROAS/CPA.
- **Drill-down path**: Every metric links to the raw warehouse table for verification.

## Out of Scope for v1

| Feature | Reason |
|---------|--------|
| Predictive modeling and ML | Data quality is not yet established enough for reliable predictions. Trust must be built with descriptive data first. |
| Real-time streaming | Marketing decisions do not require sub-minute latency. Daily batches are sufficient and simpler to maintain. |
| Self-service report builder | A report builder lets users create any view, which reintroduces the inconsistency problem this tool solves. |
| Multi-touch attribution | Attribution modeling is a research project. v1 uses platform default attribution windows and documents them. |
| Replacing existing tools | The constraint is explicit: the team keeps their current workflows. |

## Deliverables

This repository contains:

- `README.md`: This file. Narrative overview and project context.
- `product-brief.md`: The "what" and "why" of the tool in a concise format.
- `prd.md`: Detailed product requirements, user stories, and acceptance criteria.
- `architecture.md`: System design and data flow documentation.
- `user-flow.md`: How an analyst interacts with the tool day-to-day.
- `data-model.md`: Schema proposals for the warehouse with partitioning and clustering details.
- `wireframes/`: Low-fidelity mockups of the morning briefing format.

## Assumptions

- The team uses Slack as their primary communication tool. If they use Microsoft Teams, the delivery layer template changes but the rest of the architecture remains the same.
- BigQuery is available as the data warehouse. If no warehouse exists, Google Sheets could serve as a pragmatic v0.
- The team manages multiple clients (10 to 50), so multi-tenancy is built in from day one via `client_id`.
- The team has basic Python and SQL skills. The pipeline avoids complex frameworks in favor of straightforward scripts and SQL transforms.
- Budget allows for API access to Meta, Google, and Shopify. All three offer free API tiers sufficient for this scale.

## What I Would Add With More Time

- A data quality monitoring layer (for example, Soda Core or Great Expectations) to catch anomalies automatically.
- A simple Metabase or Looker Studio dashboard for on-demand drill-downs beyond the daily briefing.
- Client-facing report generation as a v2 feature, once analysts trust the underlying data.
- Incremental refresh logic to handle attribution window restatements more elegantly.
- Alerting when a data source goes down for more than 24 hours.
