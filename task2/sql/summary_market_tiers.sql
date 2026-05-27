-- Distribution of coins by market cap tier (latest snapshot)
SELECT
    market_cap_tier,
    COUNT(*) AS coin_count,
    SUM(market_cap) AS total_market_cap_usd,
    AVG(market_cap) AS avg_market_cap_usd,
    AVG(price_change_percentage_24h) AS avg_daily_change_pct,
    COUNTIF(volatility_flag = TRUE) AS volatile_coins
FROM `crypto_market.coin_snapshots`
WHERE snapshot_date = CURRENT_DATE()
GROUP BY market_cap_tier
ORDER BY
    CASE market_cap_tier
        WHEN 'Large Cap' THEN 1
        WHEN 'Mid Cap' THEN 2
        WHEN 'Small Cap' THEN 3
        WHEN 'Micro Cap' THEN 4
        ELSE 5
    END;
