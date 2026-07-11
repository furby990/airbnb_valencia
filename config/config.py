"""
config.py
=========
Central configuration for the Valencia Airbnb Investment Analysis project.
All constants and paths are defined here — no hard-coded values in notebooks or src/.
"""

import os
from pathlib import Path

# ── PROJECT ROOT ─────────────────────────────────────────────────────────────
ROOT_DIR  = Path(__file__).resolve().parent.parent
DATA_RAW  = ROOT_DIR / "data" / "raw"
DATA_PROC = ROOT_DIR / "data" / "processed"
REPORTS   = ROOT_DIR / "reports" / "figures"
SQL_DIR   = ROOT_DIR / "sql"

# ── DATA FILES ────────────────────────────────────────────────────────────────
FILES = {
    "listings":       DATA_RAW / "listings.csv",
    "calendar":       DATA_RAW / "calendar.csv",
    "reviews":        DATA_RAW / "reviews.csv",
    "neighbourhoods": DATA_RAW / "neighbourhoods.csv",
    "geojson":        DATA_RAW / "neighbourhoods.geojson",
}

# ── PROCESSED FILES ───────────────────────────────────────────────────────────
PROCESSED = {
    "listings_clean":    DATA_PROC / "listings_clean.csv",
    "calendar_monthly":  DATA_PROC / "calendar_monthly.csv",
    "reviews_monthly":   DATA_PROC / "reviews_monthly.csv",
    "investment_score":  DATA_PROC / "investment_score.csv",
    "host_segments":     DATA_PROC / "host_segments.csv",
}

# ── DATABASE ──────────────────────────────────────────────────────────────────
DB_PATH = DATA_PROC / "airbnb_valencia.db"

# ── PRICE CLEANING ────────────────────────────────────────────────────────────
PRICE_MIN     = 10      # €/noche — outliers inferiores
PRICE_MAX     = 1000    # €/noche — outliers superiores
PRICE_COL     = "price"

# ── HOST SEGMENTATION ─────────────────────────────────────────────────────────
HOST_AMATEUR_MAX  = 1   # 1 listing
HOST_SEMIPRO_MAX  = 5   # 2-5 listings
# profesional = 6+

# ── INVESTMENT SCORE WEIGHTS (deben sumar 1.0) ────────────────────────────────
SCORE_WEIGHTS = {
    "revenue_score":     0.35,   # ingresos estimados reales
    "occupancy_score":   0.25,   # ocupación estimada
    "demand_growth":     0.20,   # crecimiento de reviews YoY
    "competition_score": 0.10,   # inverso de densidad
    "price_score":       0.10,   # precio relativo al mercado
}

# ── VISUALISATION ─────────────────────────────────────────────────────────────
COLOR_PRIMARY   = "#E8163B"   # Airbnb red
COLOR_SECONDARY = "#484848"   # dark grey
COLOR_ACCENT    = "#00A699"   # teal
COLOR_GOOD      = "#27AE60"
COLOR_WARN      = "#F39C12"
COLOR_BAD       = "#E74C3C"
FIG_DPI         = 150
FIG_SIZE_WIDE   = (14, 6)
FIG_SIZE_SQ     = (10, 8)

# ── STATISTICAL TESTS ────────────────────────────────────────────────────────
ALPHA = 0.05   # significance level for hypothesis testing

# ── CALENDAR ─────────────────────────────────────────────────────────────────
CALENDAR_START = "2025-09-23"
CALENDAR_END   = "2026-09-23"
HIGH_SEASON_MONTHS = [6, 7, 8, 9]  # Jun-Sep

# ── REVIEW COLUMNS ───────────────────────────────────────────────────────────
SCORE_COLS = [
    "review_scores_rating",
    "review_scores_accuracy",
    "review_scores_cleanliness",
    "review_scores_checkin",
    "review_scores_communication",
    "review_scores_location",
    "review_scores_value",
]

# ── NEIGHBOURHOOD MAPPING ─────────────────────────────────────────────────────
# Barrios agrupados por zona para análisis macro
ZONE_MAP = {
    "CENTRE":    ["CIUTAT VELLA", "L'EIXAMPLE", "EXTRAMURS"],
    "SEAFRONT":  ["POBLATS MARITIMS", "CAMINS AL GRAU"],
    "NORTH":     ["LA SAIDIA", "RASCANYA", "BENICALAP", "POBLATS DEL NORD"],
    "SOUTH":     ["QUATRE CARRERES", "POBLATS DEL SUD", "JESUS", "L'OLIVERETA"],
    "WEST":      ["PATRAIX", "CAMPANAR", "POBLATS DE L'OEST"],
    "EAST":      ["ALGIROS", "BENIMACLET", "EL PLA DEL REAL"],
}
