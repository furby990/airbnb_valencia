-- queries_advanced.sql
-- ============================================================
-- Advanced SQL queries — window functions & subqueries
-- ============================================================


-- 1. WINDOW FUNCTION: Price percentile ranking within each neighbourhood
--    Identifies where each listing sits relative to its local market
SELECT
    id,
    name,
    neighbourhood_group_cleansed,
    room_type,
    price_eur,
    ROUND(
        PERCENT_RANK() OVER (
            PARTITION BY neighbourhood_group_cleansed
            ORDER BY price_eur
        ) * 100, 1
    )                                               AS price_percentile,
    ROUND(AVG(price_eur) OVER (
        PARTITION BY neighbourhood_group_cleansed
    ), 2)                                           AS hood_avg_price
FROM listings
WHERE price_eur IS NOT NULL
ORDER BY neighbourhood_group_cleansed, price_percentile DESC;


-- 2. WINDOW FUNCTION: Running total of reviews by year (demand growth)
--    Shows cumulative growth in platform activity over time
SELECT
    year,
    COUNT(*)                                        AS reviews_this_year,
    SUM(COUNT(*)) OVER (ORDER BY year ROWS UNBOUNDED PRECEDING)
                                                    AS cumulative_reviews,
    LAG(COUNT(*)) OVER (ORDER BY year)              AS reviews_prev_year,
    ROUND(
        (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY year)) * 100.0
        / LAG(COUNT(*)) OVER (ORDER BY year), 1
    )                                               AS yoy_growth_pct
FROM reviews
GROUP BY year
ORDER BY year;


-- 3. WINDOW FUNCTION: Rank listings by revenue within room type
--    Useful to identify top performers within each category
SELECT
    id,
    name,
    room_type,
    neighbourhood_group_cleansed,
    estimated_revenue_l365d,
    RANK() OVER (
        PARTITION BY room_type
        ORDER BY estimated_revenue_l365d DESC
    )                                               AS revenue_rank_in_type,
    ROUND(AVG(estimated_revenue_l365d) OVER (
        PARTITION BY room_type
    ), 2)                                           AS type_avg_revenue
FROM listings
WHERE estimated_revenue_l365d IS NOT NULL
ORDER BY room_type, revenue_rank_in_type
LIMIT 50;


-- 4. SUBQUERY: Neighbourhoods above Valencia median revenue
--    Filters to only high-performing areas
SELECT
    neighbourhood_group_cleansed,
    ROUND(AVG(estimated_revenue_l365d), 2)          AS avg_revenue,
    COUNT(*)                                        AS n_listings
FROM listings
WHERE estimated_revenue_l365d > (
    SELECT AVG(estimated_revenue_l365d)
    FROM listings
    WHERE estimated_revenue_l365d IS NOT NULL
)
GROUP BY neighbourhood_group_cleansed
ORDER BY avg_revenue DESC;


-- 5. SUBQUERY + WINDOW: Host performance vs neighbourhood average
--    Identifies hosts outperforming their local market
SELECT
    host_id,
    host_name,
    host_segment,
    neighbourhood_group_cleansed,
    ROUND(AVG(estimated_revenue_l365d), 2)          AS host_avg_revenue,
    hood_stats.hood_avg_revenue,
    ROUND(
        (AVG(estimated_revenue_l365d) - hood_stats.hood_avg_revenue)
        / hood_stats.hood_avg_revenue * 100, 1
    )                                               AS pct_above_hood_avg
FROM listings
JOIN (
    SELECT
        neighbourhood_group_cleansed,
        AVG(estimated_revenue_l365d)                AS hood_avg_revenue
    FROM listings
    WHERE estimated_revenue_l365d IS NOT NULL
    GROUP BY neighbourhood_group_cleansed
) AS hood_stats USING (neighbourhood_group_cleansed)
WHERE estimated_revenue_l365d IS NOT NULL
GROUP BY host_id, host_name, host_segment, neighbourhood_group_cleansed, hood_stats.hood_avg_revenue
HAVING COUNT(*) >= 3
ORDER BY pct_above_hood_avg DESC
LIMIT 20;


-- 6. WINDOW FUNCTION: Monthly occupancy trend per neighbourhood
--    Core query for the seasonality analysis
SELECT
    neighbourhood,
    month,
    season,
    SUM(CASE WHEN available = 0 THEN 1 ELSE 0 END)     AS booked_days,
    COUNT(*)                                             AS total_days,
    ROUND(
        SUM(CASE WHEN available = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        1
    )                                                    AS occupancy_rate,
    ROUND(AVG(
        ROUND(
            SUM(CASE WHEN available = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            1
        )
    ) OVER (PARTITION BY neighbourhood), 1)              AS annual_avg_occupancy
FROM calendar
LEFT JOIN listings ON calendar.listing_id = listings.id
GROUP BY neighbourhood, month, season
ORDER BY neighbourhood, month;


-- 7. SUBQUERY: Listings that are priced above median but have below-average
--    occupancy — these are overpriced relative to demand
SELECT
    id,
    name,
    neighbourhood_group_cleansed,
    price_eur,
    estimated_occupancy_l365d,
    ROUND(price_eur - market.median_price, 2)           AS price_premium,
    ROUND(estimated_occupancy_l365d - market.median_occ, 1) AS occ_deficit
FROM listings
JOIN (
    SELECT
        neighbourhood_group_cleansed,
        AVG(price_eur)                  AS median_price,
        AVG(estimated_occupancy_l365d)  AS median_occ
    FROM listings
    GROUP BY neighbourhood_group_cleansed
) AS market USING (neighbourhood_group_cleansed)
WHERE
    price_eur > market.median_price
    AND estimated_occupancy_l365d < market.median_occ
ORDER BY price_premium DESC
LIMIT 20;


-- 8. WINDOW FUNCTION: Moving average of review count (3-month window)
--    Smooths out noise to reveal underlying demand trend
SELECT
    year,
    month,
    COUNT(*)                                    AS monthly_reviews,
    ROUND(AVG(COUNT(*)) OVER (
        ORDER BY year, month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1)                                       AS moving_avg_3m
FROM reviews
GROUP BY year, month
ORDER BY year, month;
