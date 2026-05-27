-- Daily price trends for top 10 coins by market cap (last 30 days)
WITH top_coins AS (
    SELECT DISTINCT id, symbol, name
    FROM `crypto_market.coin_snapshots`
    WHERE snapshot_date = CURRENT_DATE()
    ORDER BY market_cap_rank
    LIMIT 10
)
SELECT
    s.snapshot_date,
    s.symbol,
    s.name,
    s.current_price,
    s.price_change_percentage_24h,
    AVG(s.current_price) OVER (
        PARTITION BY s.id
        ORDER BY s.snapshot_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d,
    s.price_to_ath_ratio,
    s.volatility_flag
FROM `crypto_market.coin_snapshots` s
INNER JOIN top_coins tc ON s.id = tc.id
WHERE s.snapshot_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY s.symbol, s.snapshot_date DESC;
