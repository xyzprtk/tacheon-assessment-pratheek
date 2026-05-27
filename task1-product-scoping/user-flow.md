# User Flow Documentation: Marketing Performance Reporter

## Overview

This document describes how different users interact with the Marketing Performance Reporter tool in their daily workflows. The primary focus is on the internal analyst persona (v1), with secondary flows for brand managers (v2) and leadership (v3).

---

## Flow 1: Analyst Daily Workflow

### Context
An analyst starts their workday and needs to understand how marketing is performing across their client accounts. Previously, this required logging into 4-6 different platforms and manually compiling data.

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Morning: Analyst opens Slack                            │
│     Time: 9:05 AM                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Analyst sees briefing message in #marketing-performance │
│     The message includes:                                   │
│     - 7-day vs 7-day comparison                             │
│     - Channel breakdown for top 3 channels                  │
│     - Trend indicators (arrows)                             │
│     - One-sentence narrative                                │
│     - Anomaly flags (if any)                                │
│     - Data provenance note                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Analyst scans the briefing (2-3 minutes)                │
│     - Reads the narrative summary                           │
│     - Checks trend arrows for quick scan                    │
│     - Notes any anomaly flags                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Decision: Does the analyst need to investigate further? │
└────────────────────┬────────────────────────────────────────┘
                     │
            ┌────────┴────────┐
            │                 │
            ▼                 ▼
      ┌──────────┐    ┌──────────────┐
      │    No    │    │     Yes      │
      └──────────┘    └──────────────┘
            │                 │
            │                 ▼
            │         ┌──────────────────────────────────────┐
            │         │  5. Analyst clicks "View in BigQuery" │
            │         │     Pre-filtered query opens with:    │
            │         │     - Specific date range             │
            │         │     - Specific channel                │
            │         │     - Raw metric values               │
            │         └──────────────┬───────────────────────┘
            │                        │
            │                        ▼
            │         ┌──────────────────────────────────────┐
            │         │  6. Analyst queries BigQuery directly │
            │         │     to investigate the anomaly or     │
            │         │     get more granular data            │
            │         └──────────────┬───────────────────────┘
            │                        │
            │                        ▼
            │         ┌──────────────────────────────────────┐
            │         │  7. Analyst identifies root cause     │
            │         │     Example: Meta spend dropped       │
            │         │     because campaign was paused       │
            │         └──────────────┬───────────────────────┘
            │                        │
            ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│  8. Analyst uses insights in client meeting or report       │
│     - Confident in the numbers (same source of truth)       │
│     - Can explain anomalies with context                    │
│     - Saves 30+ minutes vs. manual data pulling             │
└─────────────────────────────────────────────────────────────┘
```

### Time Saved
- **Before**: 30-60 minutes of manual data pulling
- **After**: 5 minutes to review briefing + 10-15 minutes if investigating anomalies
- **Total time saved**: 15-45 minutes per day

---

## Flow 2: Analyst Verifies a Suspicious Metric

### Context
An analyst sees that Meta ROAS dropped 40% in the briefing and wants to verify this number before mentioning it in a client meeting.

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Analyst sees in briefing:                               │
│     "Meta ROAS: 2.1 ↓ (was 3.5, -40%)"                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Analyst clicks "View in BigQuery" link in briefing      │
│     Opens pre-filtered query:                               │
│     SELECT * FROM marketing_metrics_daily                   │
│     WHERE date >= '2024-01-08' AND date <= '2024-01-14'    │
│     AND channel = 'meta'                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Analyst sees raw data:                                  │
│     - Current period spend: $5,000                          │
│     - Current period revenue: $10,500                       │
│     - ROAS: 2.1                                             │
│     - Previous period spend: $4,800                         │
│     - Previous period revenue: $16,800                      │
│     - ROAS: 3.5                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Analyst notices spend increased but revenue dropped     │
│     Queries for more detail:                                │
│     SELECT date, spend, revenue, conversions                │
│     FROM marketing_metrics_daily                            │
│     WHERE date >= '2024-01-01' AND date <= '2024-01-14'    │
│     AND channel = 'meta'                                    │
│     ORDER BY date                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Analyst identifies the issue:                           │
│     - On Jan 10, a new campaign launched with high spend    │
│     - But the campaign had low conversion rate              │
│     - This dragged down overall ROAS                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Analyst logs into Meta Ads Manager to confirm           │
│     - Sees the new campaign in Meta UI                      │
│     - Confirms the numbers match                            │
│     - Notes: "Numbers are correct, issue is campaign perf"  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Analyst prepares for client meeting:                    │
│     - "ROAS dropped due to new campaign underperformance"   │
│     - "Recommend pausing or optimizing the new campaign"    │
│     - Confident in the data (verified in BigQuery + Meta)   │
└─────────────────────────────────────────────────────────────┘
```

### Key Benefit
- Analyst can verify any number in under 5 minutes
- No "black box" feeling - full transparency into data sources
- Builds trust in the tool

---

## Flow 3: Analyst Onboards a New Client

### Context
A new client (Globex Inc.) is signed, and the analyst needs to add them to the daily briefing.

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Analyst receives new client information:                │
│     - Client name: Globex Inc.                              │
│     - Currency: EUR                                         │
│     - Timezone: Europe/London                               │
│     - Channels: Meta, Google Ads                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Analyst opens clients.yaml configuration file           │
│     Located at: config/clients.yaml                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Analyst adds new client entry:                          │
│                                                             │
│  clients:                                                   │
│    - client_id: "globex_inc"                                │
│      client_name: "Globex Inc."                             │
│      currency: "EUR"                                        │
│      timezone: "Europe/London"                              │
│      enabled_channels:                                      │
│        - meta                                               │
│        - google_ads                                         │
│      delivery:                                              │
│        slack:                                               │
│          enabled: true                                      │
│          channel: "#globex-marketing"                       │
│        email:                                               │
│          enabled: true                                      │
│          recipients:                                        │
│            - "analyst@globex.com"                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Analyst commits the change to Git                       │
│     git add config/clients.yaml                             │
│     git commit -m "Add Globex Inc. client"                  │
│     git push                                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. CI/CD pipeline automatically:                           │
│     - Validates the YAML syntax                             │
│     - Deploys the updated configuration                     │
│     - Restarts the ingestion service                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Next morning (6:00 AM UTC):                             │
│     - Ingestion pulls data for Globex Inc.                  │
│     - Data flows through staging and mart layers            │
│     - Briefing is generated for Globex Inc.                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  7. At 9:00 AM London time:                                 │
│     - Briefing appears in #globex-marketing Slack channel   │
│     - Email is sent to analyst@globex.com                   │
│     - Analyst reviews and confirms data looks correct       │
└─────────────────────────────────────────────────────────────┘
```

### Time to Onboard
- **Before**: Required engineering support to set up new client (1-2 days)
- **After**: Analyst can onboard in 5 minutes by editing YAML
- **First briefing**: Available the next morning

---

## Flow 4: Analyst Handles Incomplete Data

### Context
The Meta API was down during the 6:00 AM ingestion window. The analyst needs to understand what data is available and when it will be complete.

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. At 9:00 AM, analyst opens Slack                         │
│     Briefing shows:                                         │
│                                                             │
│  ⚠️  Incomplete Data:                                       │
│     Meta data is unavailable (API error at 6:15 AM UTC)     │
│     Retry scheduled for 10:00 AM UTC                        │
│                                                             │
│     Available channels:                                     │
│     ✓ Google Ads                                            │
│     ✓ Shopify                                               │
│     ✓ GA4                                                   │
│     ✗ Meta (incomplete)                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Analyst reviews available data:                         │
│     - Google Ads, Shopify, GA4 numbers are present          │
│     - Meta numbers are missing                              │
│     - Analyst knows not to make decisions based on this     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Analyst checks #marketing-reporter-ops Slack channel    │
│     Sees alert:                                             │
│                                                             │
│  🔴 Alert: Meta API Ingestion Failed                        │
│     Client: acme_corp                                       │
│     Error: 503 Service Unavailable                          │
│     Retry 1: Failed at 6:16 AM                              │
│     Retry 2: Failed at 6:21 AM                              │
│     Retry 3: Failed at 6:36 AM                              │
│     Next retry: 10:00 AM UTC                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Analyst decides:                                        │
│     - Option A: Wait for 10:00 AM retry                     │
│     - Option B: Use Google Ads + Shopify data for now       │
│     - Option C: Log into Meta Ads Manager manually          │
│                                                             │
│     Analyst chooses Option A (wait for retry)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. At 10:15 AM, analyst receives Slack notification:       │
│                                                             │
│  ✅ Meta API Ingestion Successful                           │
│     Client: acme_corp                                       │
│     Data as of: 2024-01-15 10:10 AM UTC                     │
│     Briefing updated with complete data                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Analyst reviews updated briefing:                       │
│     - All channels now have data                            │
│     - Can make confident decisions                          │
│     - No manual work required                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Benefit
- Analyst knows when data is incomplete (no false zeros)
- Automatic retry reduces manual intervention
- Transparency builds trust

---

## Flow 5: Brand Manager Prepares for Client Meeting (v2)

### Context
A brand manager has a weekly client meeting and needs a summary of marketing performance. Previously, they relied on analysts to pull this data.

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Monday at 8:00 AM, brand manager receives email:        │
│     Subject: "Weekly Marketing Performance Report - Acme"   │
│     Attachment: acme_weekly_report_2024-01-15.pdf           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Brand manager opens the PDF report:                     │
│     - Clean, branded format with client logo                │
│     - Executive summary with key metrics                    │
│     - Charts showing 4-week trends                          │
│     - Channel-by-channel breakdown                          │
│     - Recommendations (rule-based)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Brand manager reviews the report (5 minutes):           │
│     - "ROAS improved 12% this week"                         │
│     - "Meta is the top-performing channel"                  │
│     - "Recommendation: Increase Meta spend by 10%"          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Brand manager prepares talking points for meeting:      │
│     - "Overall performance is strong, ROAS up 12%"          │
│     - "Meta is driving the best results"                    │
│     - "We recommend increasing Meta budget"                 │
│     - "Here's the detailed report for your records"         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Brand manager presents to client:                       │
│     - Shares the PDF report                                 │
│     - Confident in the numbers (same source as analysts)    │
│     - Client asks follow-up questions                       │
│     - Brand manager can answer using the report             │
└─────────────────────────────────────────────────────────────┘
```

### Time Saved
- **Before**: Brand manager emails analyst, waits 1-2 days for report
- **After**: Report arrives automatically every Monday at 8:00 AM
- **Total time saved**: 1-2 days of latency eliminated

---

## Flow 6: Leadership Reviews Portfolio Performance (v3)

### Context
Internal leadership wants to understand how all client accounts are performing to allocate team resources.

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. On the 1st of each month, leadership receives email:    │
│     Subject: "Monthly Portfolio Performance Report"         │
│     Attachment: portfolio_report_2024-01.pdf                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Leadership opens the PDF report:                        │
│     - Total spend across all clients: $2.5M                 │
│     - Total revenue across all clients: $8.7M               │
│     - Overall portfolio ROAS: 3.5                           │
│     - Month-over-month change: +8%                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Leadership reviews top and bottom performers:           │
│                                                             │
│  Top 3 Clients by ROAS:                                     │
│  1. Acme Corp: ROAS 5.2                                     │
│  2. TechStart Inc: ROAS 4.8                                 │
│  3. RetailCo: ROAS 4.5                                      │
│                                                             │
│  Bottom 3 Clients by ROAS:                                  │
│  1. NewBrand: ROAS 1.8 (new client, still optimizing)      │
│  2. OldSchool: ROAS 2.1 (declining performance)            │
│  3. BudgetCo: ROAS 2.3 (limited budget)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Leadership identifies resource allocation needs:        │
│     - "OldSchool needs more attention, ROAS is declining"   │
│     - "Acme Corp is performing well, consider upselling"    │
│     - "NewBrand needs optimization support"                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Leadership takes action:                                │
│     - Assigns senior analyst to OldSchool account           │
│     - Schedules strategy meeting with Acme Corp             │
│     - Allocates optimization resources to NewBrand          │
└─────────────────────────────────────────────────────────────┘
```

### Key Benefit
- Single view of all client performance
- Data-driven resource allocation
- Early identification of underperforming accounts

---

## Flow 7: Analyst Investigates a Data Quality Issue

### Context
An analyst notices that Shopify revenue in the briefing doesn't match what they see in the Shopify admin panel. They need to investigate the discrepancy.

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Analyst sees in briefing:                               │
│     "Shopify Revenue: $45,000"                              │
│                                                             │
│     But in Shopify admin, they see:                         │
│     "Revenue: $50,000"                                      │
│                                                             │
│     Discrepancy: $5,000 (10%)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Analyst checks the data provenance note in briefing:    │
│     "Revenue: Shopify API, 7-day click attribution window"  │
│                                                             │
│     Analyst realizes:                                       │
│     - Briefing uses 7-day click attribution                 │
│     - Shopify admin uses last-click attribution             │
│     - This explains the discrepancy                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Analyst queries BigQuery to verify:                     │
│     SELECT date, revenue, attribution_model                 │
│     FROM stg_shopify                                        │
│     WHERE date >= '2024-01-08' AND date <= '2024-01-14'    │
│                                                             │
│     Result:                                                 │
│     - Total revenue (7-day click): $45,000                  │
│     - Total revenue (last-click): $50,000                   │
│     - Both numbers are correct, just different models       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Analyst understands the difference:                     │
│     - 7-day click: Attributes to ad click within 7 days     │
│     - Last-click: Attributes to the last touchpoint         │
│     - Both are valid, just different perspectives           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Analyst documents the finding:                          │
│     - Adds note to client deck: "Revenue uses 7-day click"  │
│     - Explains to client why numbers differ from Shopify    │
│     - Client understands and trusts the data                │
└─────────────────────────────────────────────────────────────┘
```

### Key Benefit
- Transparency about attribution models prevents confusion
- Analyst can verify and explain discrepancies
- Builds trust with clients

---

## Summary of User Flows

| Flow | User | Time Saved | Key Benefit |
|------|------|------------|-------------|
| 1. Daily Workflow | Analyst | 15-45 min/day | Consistent daily summary |
| 2. Verify Metric | Analyst | 5 min | Full transparency and auditability |
| 3. Onboard Client | Analyst | 1-2 days | Self-service client onboarding |
| 4. Handle Incomplete Data | Analyst | 30 min | Graceful degradation, no false zeros |
| 5. Client Meeting Prep | Brand Manager | 1-2 days | Automated weekly reports |
| 6. Portfolio Review | Leadership | 2-4 hours | Single view of all clients |
| 7. Data Quality Issue | Analyst | 15 min | Clear attribution documentation |

---

## Design Principles

1. **Push-based delivery**: Insights come to the user, not the other way around.
2. **Progressive disclosure**: Start with high-level summary, allow drill-down for details.
3. **Transparency**: Always show data sources, update times, and known limitations.
4. **Graceful degradation**: Flag incomplete data rather than showing zeros or failing silently.
5. **Auditability**: Every metric can be verified by querying the underlying data.
