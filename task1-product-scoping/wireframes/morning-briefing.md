# Wireframe Concepts: Morning Briefing Formats

This document contains low-fidelity wireframes showing the layout and structure of daily briefings across different delivery channels and scenarios.

---

## Wireframe 1: Slack Briefing - Standard Format

```
┌─────────────────────────────────────────────────────────────────────────┐
│ #marketing-performance                                            9:00 AM│
├─────────────────────────────────────────────────────────────────────────┤
│ Marketing Reporter Bot  9:00 AM                                         │
│                                                                         │
│ 📊 Daily Marketing Briefing for Acme Corporation                       │
│ Data as of 2024-01-15 09:00:00 UTC                                     │
│                                                                         │
│ Last 7 Days vs. Previous 7 Days:                                       │
│ • Total Spend: $45,230 (↑ 12%)                                         │
│ • Total Revenue: $180,920 (↑ 8%)                                       │
│ • Overall ROAS: 4.0 (↓ 4%)                                             │
│                                                                         │
│ Channel Breakdown (Top 3 by Spend):                                    │
│                                                                         │
│ 1. Meta                                                                │
│    • Spend: $22,500 ↑ 15%                                              │
│    • Revenue: $101,250 ↑ 10%                                           │
│    • ROAS: 4.5 ↓ 4%                                                    │
│    • CPA: $18.50 ↑ 8%                                                  │
│                                                                         │
│ 2. Google Ads                                                          │
│    • Spend: $15,800 ↑ 8%                                               │
│    • Revenue: $63,200 ↑ 5%                                             │
│    • ROAS: 4.0 ↓ 3%                                                    │
│    • CPA: $22.00 ↑ 5%                                                  │
│                                                                         │
│ 3. Shopify (Direct)                                                    │
│    • Spend: $6,930 ↑ 10%                                               │
│    • Revenue: $16,470 ↑ 12%                                            │
│    • ROAS: 2.4 ↑ 2%                                                    │
│    • CPA: $25.00 ↑ 3%                                                  │
│                                                                         │
│ 💡 ROAS dropped 4% overall due to increased Meta spend with lower      │
│ conversion rates on new campaigns.                                      │
│                                                                         │
│ Data Sources:                                                          │
│ • Spend: Meta/Google Ads API                                           │
│ • Revenue: Shopify API                                                 │
│ • Clicks: Meta/Google Ads API                                          │
│ • Sessions: GA4 API                                                    │
│                                                                         │
│ Note: These numbers will not match across platforms due to attribution │
│ differences.                                                            │
│                                                                         │
│ To verify any metric, query BigQuery:                                  │
│ SELECT * FROM marketing_metrics_daily                                  │
│ WHERE date = '2024-01-14' AND channel = 'meta'                         │
│                                                                         │
│ [View in BigQuery]                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe 2: Slack Briefing - With Anomalies

```
┌─────────────────────────────────────────────────────────────────────────┐
│ #marketing-performance                                            9:00 AM│
├─────────────────────────────────────────────────────────────────────────┤
│ Marketing Reporter Bot  9:00 AM                                         │
│                                                                         │
│ 📊 Daily Marketing Briefing for Acme Corporation                       │
│ Data as of 2024-01-15 09:00:00 UTC                                     │
│                                                                         │
│ Last 7 Days vs. Previous 7 Days:                                       │
│ • Total Spend: $38,450 (↓ 22%)                                         │
│ • Total Revenue: $165,200 (↓ 8%)                                       │
│ • Overall ROAS: 4.3 (↑ 18%)                                            │
│                                                                         │
│ Channel Breakdown (Top 3 by Spend):                                    │
│                                                                         │
│ 1. Meta                                                                │
│    • Spend: $12,500 ↓ 65%                                              │
│    • Revenue: $75,000 ↓ 15%                                            │
│    • ROAS: 6.0 ↑ 147%                                                  │
│    • CPA: $12.50 ↓ 42%                                                 │
│                                                                         │
│ 2. Google Ads                                                          │
│    • Spend: $18,200 ↑ 5%                                               │
│    • Revenue: $72,800 ↑ 3%                                             │
│    • ROAS: 4.0 → 0%                                                    │
│    • CPA: $24.00 ↑ 2%                                                  │
│                                                                         │
│ 3. Shopify (Direct)                                                    │
│    • Spend: $7,750 ↑ 8%                                                │
│    • Revenue: $17,400 ↑ 10%                                            │
│    • ROAS: 2.2 ↑ 2%                                                    │
│    • CPA: $28.00 ↑ 4%                                                  │
│                                                                         │
│ 💡 Meta spend dropped 65% week-over-week, improving overall ROAS       │
│ despite lower revenue.                                                  │
│                                                                         │
│ ⚠️  Anomalies Detected:                                                │
│ • Meta spend is $1,800 (expected ~$5,200). Possible cause: campaign    │
│   paused or budget reduced.                                             │
│ • Meta ROAS is 6.0 (threshold: >5.0). Unusually high performance.      │
│                                                                         │
│ Data Sources:                                                          │
│ • Spend: Meta/Google Ads API                                           │
│ • Revenue: Shopify API                                                 │
│ • Clicks: Meta/Google Ads API                                          │
│ • Sessions: GA4 API                                                    │
│                                                                         │
│ Note: These numbers will not match across platforms due to attribution │
│ differences.                                                            │
│                                                                         │
│ To verify any metric, query BigQuery:                                  │
│ SELECT * FROM marketing_metrics_daily                                  │
│ WHERE date = '2024-01-14' AND channel = 'meta'                         │
│                                                                         │
│ [View in BigQuery]                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe 3: Slack Briefing - Incomplete Data

```
┌─────────────────────────────────────────────────────────────────────────┐
│ #marketing-performance                                            9:00 AM│
├─────────────────────────────────────────────────────────────────────────┤
│ Marketing Reporter Bot  9:00 AM                                         │
│                                                                         │
│ 📊 Daily Marketing Briefing for Acme Corporation                       │
│ Data as of 2024-01-15 09:00:00 UTC                                     │
│                                                                         │
│ ⚠️  Incomplete Data:                                                   │
│ Meta data is unavailable (API error at 6:15 AM UTC)                    │
│ Retry scheduled for 10:00 AM UTC                                       │
│                                                                         │
│ Available channels:                                                    │
│ ✓ Google Ads                                                           │
│ ✓ Shopify                                                              │
│ ✓ GA4                                                                  │
│ ✗ Meta (incomplete)                                                    │
│                                                                         │
│ Last 7 Days vs. Previous 7 Days (Partial Data):                        │
│ • Total Spend: $22,730 (↓ 35%) [Meta excluded]                         │
│ • Total Revenue: $79,670 (↓ 28%) [Meta excluded]                       │
│ • Overall ROAS: 3.5 (↑ 11%) [Meta excluded]                            │
│                                                                         │
│ Channel Breakdown (Available Channels):                                │
│                                                                         │
│ 1. Google Ads                                                          │
│    • Spend: $15,800 ↑ 8%                                               │
│    • Revenue: $63,200 ↑ 5%                                             │
│    • ROAS: 4.0 ↓ 3%                                                    │
│    • CPA: $22.00 ↑ 5%                                                  │
│                                                                         │
│ 2. Shopify (Direct)                                                    │
│    • Spend: $6,930 ↑ 10%                                               │
│    • Revenue: $16,470 ↑ 12%                                            │
│    • ROAS: 2.4 ↑ 2%                                                    │
│    • CPA: $25.00 ↑ 3%                                                  │
│                                                                         │
│ 💡 Performance stable across available channels. Awaiting Meta data    │
│ for complete picture.                                                   │
│                                                                         │
│ Data Sources:                                                          │
│ • Spend: Google Ads API                                                │
│ • Revenue: Shopify API                                                 │
│ • Clicks: Google Ads API                                               │
│ • Sessions: GA4 API                                                    │
│                                                                         │
│ Note: These numbers will not match across platforms due to attribution │
│ differences.                                                            │
│                                                                         │
│ To verify any metric, query BigQuery:                                  │
│ SELECT * FROM marketing_metrics_daily                                  │
│ WHERE date = '2024-01-14' AND channel = 'google_ads'                   │
│                                                                         │
│ [View in BigQuery]                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe 4: Email Briefing - HTML Format

```
┌─────────────────────────────────────────────────────────────────────────┐
│ From: marketing-reporter@company.com                                    │
│ To: analyst1@company.com, analyst2@company.com                         │
│ Subject: Daily Marketing Briefing - Acme Corporation - Jan 15, 2024    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │                                                                     ││
│ │  Daily Marketing Briefing                                           ││
│ │  Acme Corporation                                                   ││
│ │  January 15, 2024                                                   ││
│ │                                                                     ││
│ │  Data as of: 2024-01-15 09:00:00 UTC                               ││
│ │                                                                     ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │  Last 7 Days vs. Previous 7 Days                                   ││
│ │                                                                     ││
│ │  ┌──────────────────────────────────────────────────────────────┐  ││
│ │  │ Metric       │ Current   │ Previous  │ Change               │  ││
│ │  ├──────────────────────────────────────────────────────────────┤  ││
│ │  │ Total Spend  │ $45,230   │ $40,384   │ ↑ 12%                │  ││
│ │  │ Revenue      │ $180,920  │ $167,519  │ ↑ 8%                 │  ││
│ │  │ ROAS         │ 4.0       │ 4.15      │ ↓ 4%                 │  ││
│ │  │ CPA          │ $21.50    │ $19.90    │ ↑ 8%                 │  ││
│ │  └──────────────────────────────────────────────────────────────┘  ││
│ │                                                                     ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │  Channel Breakdown (Top 3 by Spend)                                ││
│ │                                                                     ││
│ │  1. Meta                                                            ││
│ │     Spend: $22,500 (↑ 15%)  Revenue: $101,250 (↑ 10%)             ││
│ │     ROAS: 4.5 (↓ 4%)       CPA: $18.50 (↑ 8%)                     ││
│ │                                                                     ││
│ │  2. Google Ads                                                      ││
│ │     Spend: $15,800 (↑ 8%)   Revenue: $63,200 (↑ 5%)               ││
│ │     ROAS: 4.0 (↓ 3%)       CPA: $22.00 (↑ 5%)                     ││
│ │                                                                     ││
│ │  3. Shopify (Direct)                                                ││
│ │     Spend: $6,930 (↑ 10%)   Revenue: $16,470 (↑ 12%)              ││
│ │     ROAS: 2.4 (↑ 2%)       CPA: $25.00 (↑ 3%)                     ││
│ │                                                                     ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │  💡 Insight                                                         ││
│ │                                                                     ││
│ │  ROAS dropped 4% overall due to increased Meta spend with lower    ││
│ │  conversion rates on new campaigns.                                 ││
│ │                                                                     ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │  Data Sources                                                       ││
│ │                                                                     ││
│ │  • Spend: Meta/Google Ads API                                      ││
│ │  • Revenue: Shopify API                                            ││
│ │  • Clicks: Meta/Google Ads API                                     ││
│ │  • Sessions: GA4 API                                               ││
│ │                                                                     ││
│ │  Note: These numbers will not match across platforms due to        ││
│ │  attribution differences.                                           ││
│ │                                                                     ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │  Verify in BigQuery                                                 ││
│ │                                                                     ││
│ │  SELECT * FROM marketing_metrics_daily                             ││
│ │  WHERE date = '2024-01-14' AND channel = 'meta'                    ││
│ │                                                                     ││
│ │  [View in BigQuery]                                                 ││
│ │                                                                     ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ Attachment: acme_daily_metrics_2024-01-15.csv                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe 5: Microsoft Teams Briefing (Adaptive Card)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ #marketing-performance                                            9:00 AM│
├─────────────────────────────────────────────────────────────────────────┤
│ Marketing Reporter Bot  9:00 AM                                         │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │  📊 Daily Marketing Briefing                                       ││
│ │  Acme Corporation                                                   ││
│ │  Data as of 2024-01-15 09:00:00 UTC                                ││
│ │                                                                     ││
│ │  Last 7 Days vs. Previous 7 Days:                                  ││
│ │  • Total Spend: $45,230 (↑ 12%)                                    ││
│ │  • Total Revenue: $180,920 (↑ 8%)                                  ││
│ │  • Overall ROAS: 4.0 (↓ 4%)                                        ││
│ │                                                                     ││
│ │  [View Channel Details]  [View in BigQuery]  [Export CSV]          ││
│ │                                                                     ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │  Channel Breakdown (Top 3)                                         ││
│ │                                                                     ││
│ │  ┌───────────────────────────────────────────────────────────────┐ ││
│ │  │ 1. Meta                                                       │ ││
│ │  │    Spend: $22,500 ↑ 15%    Revenue: $101,250 ↑ 10%           │ ││
│ │  │    ROAS: 4.5 ↓ 4%          CPA: $18.50 ↑ 8%                  │ ││
│ │  └───────────────────────────────────────────────────────────────┘ ││
│ │                                                                     ││
│ │  ┌───────────────────────────────────────────────────────────────┐ ││
│ │  │ 2. Google Ads                                                 │ ││
│ │  │    Spend: $15,800 ↑ 8%     Revenue: $63,200 ↑ 5%             │ ││
│ │  │    ROAS: 4.0 ↓ 3%          CPA: $22.00 ↑ 5%                  │ ││
│ │  └───────────────────────────────────────────────────────────────┘ ││
│ │                                                                     ││
│ │  ┌───────────────────────────────────────────────────────────────┐ ││
│ │  │ 3. Shopify (Direct)                                           │ ││
│ │  │    Spend: $6,930 ↑ 10%     Revenue: $16,470 ↑ 12%            │ ││
│ │  │    ROAS: 2.4 ↑ 2%          CPA: $25.00 ↑ 3%                  │ ││
│ │  └───────────────────────────────────────────────────────────────┘ ││
│ │                                                                     ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ 💡 ROAS dropped 4% overall due to increased Meta spend with lower      │
│ conversion rates on new campaigns.                                      │
│                                                                         │
│ [View Full Report]  [Dismiss]                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe 6: Weekly Client Report (v2) - PDF Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                                                                   │ │
│  │  [CLIENT LOGO]                                                    │ │
│  │                                                                   │ │
│  │  Weekly Marketing Performance Report                              │ │
│  │  Acme Corporation                                                 │ │
│  │  Week of January 8-14, 2024                                       │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  EXECUTIVE SUMMARY                                                      │
│                                                                         │
│  Overall marketing performance improved this week with a 12% increase  │
│  in spend driving an 8% increase in revenue. ROAS remains strong at    │
│  4.0, though slightly lower than the previous week due to new campaign │
│  testing on Meta.                                                       │
│                                                                         │
│  Key Highlights:                                                        │
│  • Total spend increased 12% to $45,230                                │
│  • Revenue increased 8% to $180,920                                    │
│  • Meta remains the top-performing channel with 4.5 ROAS               │
│  • Google Ads performance stable with 4.0 ROAS                         │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  PERFORMANCE OVERVIEW                                                   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Metric           This Week    Last Week    Change               │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │  Total Spend      $45,230      $40,384      ↑ 12%                │  │
│  │  Total Revenue    $180,920     $167,519     ↑ 8%                 │  │
│  │  ROAS             4.0          4.15         ↓ 4%                 │  │
│  │  Total CPA        $21.50       $19.90       ↑ 8%                 │  │
│  │  Conversions      2,103        2,012        ↑ 5%                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  4-WEEK TREND                                                           │
│                                                                         │
│  Revenue Trend:                                                         │
│  $200k │                                              •                │
│        │                              •                                │
│  $180k │                    •                                          │
│        │          •                                                      │
│  $160k │                                                                │
│        └──────┬──────────┬──────────┬──────────┬──────                │
│             Week 1     Week 2     Week 3     Week 4                   │
│             Dec 18     Dec 25     Jan 1      Jan 8                    │
│                                                                         │
│  ROAS Trend:                                                            │
│  4.5  │                              •                                │
│       │          •                                                      │
│  4.0  │                    •          •                                │
│       │                                                                │
│  3.5  │                                                                │
│       └──────┬──────────┬──────────┬──────────┬──────                │
│            Week 1     Week 2     Week 3     Week 4                   │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  CHANNEL PERFORMANCE                                                    │
│                                                                         │
│  Meta (Top Performer)                                                   │
│  • Spend: $22,500 (↑ 15%)                                              │
│  • Revenue: $101,250 (↑ 10%)                                           │
│  • ROAS: 4.5 (↓ 4%)                                                    │
│  • CPA: $18.50 (↑ 8%)                                                  │
│                                                                         │
│  Meta continues to drive the highest ROAS despite increased spend.     │
│  New campaigns launched this week are still optimizing.                │
│                                                                         │
│  Google Ads                                                             │
│  • Spend: $15,800 (↑ 8%)                                               │
│  • Revenue: $63,200 (↑ 5%)                                             │
│  • ROAS: 4.0 (↓ 3%)                                                    │
│  • CPA: $22.00 (↑ 5%)                                                  │
│                                                                         │
│  Google Ads performance stable with consistent results.                │
│                                                                         │
│  Shopify (Direct)                                                       │
│  • Spend: $6,930 (↑ 10%)                                               │
│  • Revenue: $16,470 (↑ 12%)                                            │
│  • ROAS: 2.4 (↑ 2%)                                                    │
│  • CPA: $25.00 (↑ 3%)                                                  │
│                                                                         │
│  Direct traffic showing steady improvement.                            │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  RECOMMENDATIONS                                                        │
│                                                                         │
│  1. Increase Meta Budget                                                │
│     Meta ROAS of 4.5 indicates strong performance. Consider increasing │
│     budget by 10-15% to capture additional high-intent traffic.        │
│                                                                         │
│  2. Monitor New Meta Campaigns                                          │
│     New campaigns launched this week are still in learning phase.      │
│     Monitor performance over the next 7 days before making changes.    │
│                                                                         │
│  3. Optimize Google Ads CPA                                             │
│     Google Ads CPA increased 5%. Review keyword performance and        │
│     consider pausing underperforming ad groups.                        │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  NEXT STEPS                                                             │
│                                                                         │
│  • Review Meta campaign performance in 7 days                          │
│  • Analyze Google Ads keyword performance                              │
│  • Prepare budget increase proposal for Meta                           │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  Questions? Contact your account manager.                               │
│                                                                         │
│  Report generated by Marketing Performance Reporter                    │
│  Data as of January 15, 2024 09:00 UTC                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe 7: Mobile View - Slack Briefing

```
┌─────────────────────────┐
│ #marketing-performance  │
├─────────────────────────┤
│ Marketing Bot    9:00 AM│
│                         │
│ 📊 Daily Briefing      │
│ Acme Corp               │
│ Jan 15, 2024 09:00 UTC │
│                         │
│ Last 7 Days:           │
│ Spend: $45,230 ↑12%    │
│ Revenue: $180,920 ↑8%  │
│ ROAS: 4.0 ↓4%          │
│                         │
│ Top Channels:          │
│                         │
│ 1. Meta                │
│ Spend: $22,500 ↑15%    │
│ ROAS: 4.5 ↓4%          │
│                         │
│ 2. Google Ads          │
│ Spend: $15,800 ↑8%     │
│ ROAS: 4.0 ↓3%          │
│                         │
│ 3. Shopify             │
│ Spend: $6,930 ↑10%     │
│ ROAS: 2.4 ↑2%          │
│                         │
│ 💡 ROAS dropped 4% due │
│ to increased Meta      │
│ spend with lower CVR.  │
│                         │
│ [View in BigQuery]     │
└─────────────────────────┘
```

---

## Design Notes

### Color Coding (for visual implementations)
- **Green (↑)**: Positive change (>5% improvement)
- **Red (↓)**: Negative change (>5% decline)
- **Gray (→)**: Stable (within ±5%)
- **Yellow (⚠️)**: Warning or incomplete data
- **Blue (💡)**: Insight or recommendation

### Typography Hierarchy
1. **Client Name**: Bold, 16pt
2. **Section Headers**: Bold, 14pt
3. **Metrics**: Regular, 12pt
4. **Trend Indicators**: Bold, 12pt
5. **Footnotes**: Regular, 10pt, gray

### Spacing
- **Section spacing**: 16px vertical
- **Metric spacing**: 8px vertical
- **Channel spacing**: 12px vertical

### Accessibility
- All trend indicators include text labels (↑ 12%) not just symbols
- Color is not the only indicator (arrows and percentages also used)
- Minimum contrast ratio of 4.5:1 for all text
- Screen reader friendly markup in HTML email version
