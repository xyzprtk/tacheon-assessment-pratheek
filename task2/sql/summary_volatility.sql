-- Top 20 most volatile coins in the last 7 days
SELECT
    symbol,
    name,
    AVG(current_price) AS avg_price_usd,
    AVG(price_change_percentage_24h) AS avg_daily_change_pct,
    STDDEV(price_change_percentage_24h) AS volatility_stddev,
    COUNTIF(volatility_flag = TRUE) AS volatile_days,
    COUNT(*) AS total_days,
    SAFE_DIVIDE(COUNTIF(volatility_flag = TRUE), COUNT(*)) AS volatility_ratio
FROM `crypto_market.coin_snapshots`
WHERE snapshot_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY symbol, name
HAVING total_days >= 3
ORDER BY volatility_stddev DESC
LIMIT 20;
