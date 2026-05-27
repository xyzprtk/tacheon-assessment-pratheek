# Product Brief: Marketing Performance Reporter

## What

The Marketing Performance Reporter is an internal tool that automatically aggregates marketing data from multiple platforms and delivers a daily performance summary to analysts managing client brands.

## Why

### The problem

Analysts currently spend significant time each day logging into Meta Ads Manager, Google Ads, Google Analytics, Shopify, and other platforms to answer a single question: "How is our marketing performing across channels, and where should we focus?"

This manual process creates three issues:

1. **Inconsistency**: Different analysts pull data differently, use different definitions, and produce different answers to the same question.

2. **Latency**: The process takes longer than it should, creating a bottleneck when clients or leadership need answers quickly.

3. **Key-person dependency**: When the analyst who usually handles this is unavailable, the question goes unanswered.

### The opportunity

By automating data ingestion and standardizing metric definitions, the tool eliminates manual work and ensures every team member gets the same answer. The daily briefing format pushes insights to analysts rather than requiring them to log into a dashboard, reducing friction and ensuring consistent cadence.

## Who

**Primary user (v1)**: Internal analysts and account managers who manage multiple client brands and need to understand cross-channel marketing performance.

**Secondary users (v2)**: Client-facing brand managers who need high-level summaries for client meetings.

**Tertiary users (v3)**: Internal leadership who need rollup views across all clients to allocate resources.

## How It Works

1. **Data ingestion**: Python scripts pull data from Meta Marketing API, Google Ads API, Shopify API, and GA4 API on a daily schedule (6:00 AM).

2. **Storage and transformation**: Raw data lands in BigQuery, then flows through staging and mart layers where metrics like ROAS, CPA, CTR, and CVR are calculated using standardized definitions.

3. **Delivery**: At 9:00 AM daily, a morning briefing is sent via Slack or email containing:
   - Last 7 days vs. previous 7 days comparison
   - Channel-by-channel breakdown for top 3 channels
   - Trend indicators (up/down arrows)
   - One-sentence narrative explaining the most notable change
   - Anomaly flags for unusual metric movements
   - Data provenance note

## Key Principles

1. **Additive, not substitutive**: The tool does not replace existing platforms. It aggregates and narrates on top of them.

2. **Push-based delivery**: Insights come to the analyst via Slack or email rather than requiring dashboard login.

3. **Standardized definitions**: Every metric has a documented definition and source of truth. Revenue means the same thing to every analyst.

4. **Transparency over perfection**: The tool explicitly states data sources, update times, and known discrepancies rather than hiding them.

5. **Graceful degradation**: When a data source is unavailable, the briefing flags incomplete data rather than showing zeros or failing silently.

## Success Metrics

- **Time saved**: Analysts spend less than 5 minutes reviewing the daily briefing instead of 30+ minutes pulling data manually.

- **Consistency**: Every analyst gets the same numbers for the same time period, regardless of who pulls the report.

- **Adoption**: 80% of analysts open and reference the daily briefing within the first month.

- **Trust**: Analysts can verify any metric by querying the underlying BigQuery table, and the tool provides clear documentation for doing so.

## What's Not in v1

- Predictive modeling or ML recommendations
- Real-time streaming data
- Self-service report builder
- Multi-touch attribution modeling
- Client-facing branded reports
- Custom dashboard UI

These features are valuable but require established data quality and user trust before implementation.
