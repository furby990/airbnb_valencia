-- schema.sql
-- ============================================================
-- Database schema for Valencia Airbnb Investment Analysis
-- ============================================================

-- Drop tables if they exist (for re-runs)
DROP TABLE IF EXISTS listings;
DROP TABLE IF EXISTS calendar;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS neighbourhoods;
DROP TABLE IF EXISTS investment_scores;

-- ── LISTINGS ─────────────────────────────────────────────────
CREATE TABLE listings (
    id                              INTEGER PRIMARY KEY,
    name                            TEXT,
    host_id                         INTEGER,
    host_name                       TEXT,
    host_since                      DATE,
    host_is_superhost               BOOLEAN,
    host_listings_count             INTEGER,
    host_response_rate              REAL,
    host_acceptance_rate            REAL,
    neighbourhood_group_cleansed    TEXT,
    neighbourhood_cleansed          TEXT,
    zone                            TEXT,
    latitude                        REAL,
    longitude                       REAL,
    room_type                       TEXT,
    property_type                   TEXT,
    accommodates                    INTEGER,
    bedrooms                        REAL,
    beds                            REAL,
    price_eur                       REAL,
    minimum_nights                  INTEGER,
    availability_365                INTEGER,
    number_of_reviews               INTEGER,
    reviews_per_month               REAL,
    review_scores_rating            REAL,
    review_scores_cleanliness       REAL,
    review_scores_location          REAL,
    review_scores_value             REAL,
    estimated_revenue_l365d         REAL,
    estimated_occupancy_l365d       REAL,
    instant_bookable                BOOLEAN,
    host_segment                    TEXT,
    log_price                       REAL,
    revenue_per_night               REAL
);

-- ── CALENDAR ─────────────────────────────────────────────────
CREATE TABLE calendar (
    listing_id      INTEGER,
    date            DATE,
    available       BOOLEAN,
    month           INTEGER,
    year            INTEGER,
    season          TEXT,
    FOREIGN KEY (listing_id) REFERENCES listings(id)
);

-- ── REVIEWS ──────────────────────────────────────────────────
CREATE TABLE reviews (
    id              INTEGER PRIMARY KEY,
    listing_id      INTEGER,
    date            DATE,
    reviewer_id     INTEGER,
    reviewer_name   TEXT,
    comments        TEXT,
    year            INTEGER,
    month           INTEGER,
    FOREIGN KEY (listing_id) REFERENCES listings(id)
);

-- ── NEIGHBOURHOODS ────────────────────────────────────────────
CREATE TABLE neighbourhoods (
    neighbourhood_group     TEXT,
    neighbourhood           TEXT
);

-- ── INVESTMENT SCORES ─────────────────────────────────────────
CREATE TABLE investment_scores (
    neighbourhood_group_cleansed    TEXT PRIMARY KEY,
    investment_score                REAL,
    rank                            INTEGER,
    median_revenue                  REAL,
    median_occupancy                REAL,
    n_listings                      INTEGER,
    median_price                    REAL,
    revenue_score_norm              REAL,
    occupancy_score_norm            REAL,
    demand_growth_norm              REAL,
    competition_score_norm          REAL,
    price_score_norm                REAL
);
