-- queries_basic.sql
-- ============================================================
-- Basic SQL queries for the Valencia Airbnb Analysis
-- ============================================================

-- 1. Price statistics by neighbourhood
SELECT
    neighbourhood_group_cleansed,
    COUNT(*)                            AS n_listings,
    ROUND(AVG(price_eur), 2)            AS avg_price,
    ROUND(MIN(price_eur), 2)            AS min_price,
    ROUND(MAX(price_eur), 2)            AS max_price
FROM listings
GROUP BY neighbourhood_group_cleansed
ORDER BY avg_price DESC;


-- 2. Revenue by room type
SELECT
    room_type,
    COUNT(*)                                        AS n_listings,
    ROUND(AVG(estimated_revenue_l365d), 2)          AS avg_revenue,
    ROUND(AVG(estimated_occupancy_l365d), 1)        AS avg_occupancy_days
FROM listings
WHERE estimated_revenue_l365d IS NOT NULL
GROUP BY room_type
ORDER BY avg_revenue DESC;


-- 3. Superhost vs Regular host performance
SELECT
    host_is_superhost,
    COUNT(*)                                        AS n_listings,
    ROUND(AVG(price_eur), 2)                        AS avg_price,
    ROUND(AVG(estimated_revenue_l365d), 2)          AS avg_revenue,
    ROUND(AVG(review_scores_rating), 3)             AS avg_rating,
    ROUND(AVG(estimated_occupancy_l365d), 1)        AS avg_occupancy
FROM listings
GROUP BY host_is_superhost;


-- 4. Top 10 most profitable listings
SELECT
    id,
    name,
    neighbourhood_group_cleansed,
    room_type,
    price_eur,
    estimated_revenue_l365d,
    estimated_occupancy_l365d,
    review_scores_rating
FROM listings
WHERE estimated_revenue_l365d IS NOT NULL
ORDER BY estimated_revenue_l365d DESC
LIMIT 10;


-- 5. Availability analysis
SELECT
    neighbourhood_group_cleansed,
    ROUND(AVG(availability_365), 1)     AS avg_days_available,
    ROUND(AVG(365 - availability_365), 1) AS avg_days_booked,
    ROUND(AVG(365 - availability_365) * 100.0 / 365, 1) AS occupancy_pct
FROM listings
GROUP BY neighbourhood_group_cleansed
ORDER BY occupancy_pct DESC;


-- 6. Host segmentation summary
SELECT
    host_segment,
    COUNT(DISTINCT host_id)                         AS n_hosts,
    COUNT(*)                                        AS n_listings,
    ROUND(AVG(price_eur), 2)                        AS avg_price,
    ROUND(AVG(estimated_revenue_l365d), 2)          AS avg_revenue,
    ROUND(SUM(CASE WHEN host_is_superhost THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
                                                    AS pct_superhost
FROM listings
GROUP BY host_segment
ORDER BY avg_revenue DESC;


-- 7. Investment score ranking
SELECT
    rank,
    neighbourhood_group_cleansed,
    investment_score,
    median_revenue,
    ROUND(median_occupancy, 1)          AS median_occupancy_days,
    n_listings,
    median_price
FROM investment_scores
ORDER BY rank;


-- 8. Review volume by year (demand trend)
SELECT
    year,
    COUNT(*)                AS total_reviews,
    COUNT(DISTINCT listing_id) AS active_listings
FROM reviews
GROUP BY year
ORDER BY year;
