"""
cleaning.py
===========
Data cleaning and wrangling functions for the Airbnb Valencia dataset.
Each function documents the quality issue it addresses and why.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import (
    PRICE_MIN, PRICE_MAX, PRICE_COL,
    HOST_AMATEUR_MAX, HOST_SEMIPRO_MAX, SCORE_COLS
)


def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the price column.

    Issue: price stored as string with '$' and ',' (e.g. '$1,200.00').
    Also removes extreme outliers below PRICE_MIN and above PRICE_MAX.

    Parameters
    ----------
    df : pd.DataFrame  Input listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with 'price_eur' column added (float, €/night).
    """
    df = df.copy()
    df["price_eur"] = (
        df[PRICE_COL]
        .astype(str)
        .str.replace(r"[\$,]", "", regex=True)
        .replace("nan", np.nan)
        .astype(float)
    )
    before = len(df)
    df = df[(df["price_eur"] >= PRICE_MIN) | (df["price_eur"].isna())]
    df = df[(df["price_eur"] <= PRICE_MAX) | (df["price_eur"].isna())]
    removed = before - len(df)
    print(f"  price_eur: {removed} outliers removed (< {PRICE_MIN}€ or > {PRICE_MAX}€)")
    return df


def impute_missing_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing prices with neighbourhood median.

    Strategy: median by neighbourhood_group_cleansed + room_type.
    Justified because price varies significantly by location and type.

    Parameters
    ----------
    df : pd.DataFrame  Listings with 'price_eur' column.

    Returns
    -------
    pd.DataFrame  DataFrame with missing prices imputed.
    """
    df = df.copy()
    null_before = df["price_eur"].isna().sum()
    group_median = df.groupby(
        ["neighbourhood_group_cleansed", "room_type"]
    )["price_eur"].transform("median")
    df["price_eur"] = df["price_eur"].fillna(group_median)
    # Remaining nulls filled with global median
    df["price_eur"] = df["price_eur"].fillna(df["price_eur"].median())
    print(f"  price imputed: {null_before} nulls → {df['price_eur'].isna().sum()} remaining")
    return df


def drop_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns with >80% null values or no analytical value.

    Columns dropped:
    - calendar_updated: 100% null
    - host_neighbourhood: 77% null, duplicated by neighbourhood_cleansed
    - neighborhood_overview: 58% null, free text not used in analysis
    - scrape_id, last_scraped: scraping metadata, not analytical
    - listing_url, picture_url, host_url, host_thumbnail_url,
      host_picture_url: URLs, not analytical

    Parameters
    ----------
    df : pd.DataFrame  Raw listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with irrelevant columns removed.
    """
    cols_to_drop = [
        "calendar_updated",       # 100% null
        "host_neighbourhood",     # 77% null
        "neighborhood_overview",  # 58% null, free text
        "scrape_id",              # metadata
        "last_scraped",           # metadata
        "listing_url",            # URL
        "picture_url",            # URL
        "host_url",               # URL
        "host_thumbnail_url",     # URL
        "host_picture_url",       # URL
        "host_verifications",     # complex list, not used
        "neighbourhood",          # 58% null, superseded by _cleansed version
    ]
    existing = [c for c in cols_to_drop if c in df.columns]
    df = df.drop(columns=existing)
    print(f"  dropped {len(existing)} irrelevant columns")
    return df


def fix_boolean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert boolean-like string columns ('t'/'f') to proper bool.

    Affected columns: host_is_superhost, host_has_profile_pic,
    host_identity_verified, instant_bookable.

    Parameters
    ----------
    df : pd.DataFrame  Listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with boolean columns fixed.
    """
    df = df.copy()
    bool_cols = [
        "host_is_superhost", "host_has_profile_pic",
        "host_identity_verified", "instant_bookable",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].map({"t": True, "f": False})
    print(f"  boolean columns converted: {[c for c in bool_cols if c in df.columns]}")
    return df


def fix_percentage_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert percentage string columns to float (0–1 scale).

    e.g. '95%' → 0.95
    Affected: host_response_rate, host_acceptance_rate.

    Parameters
    ----------
    df : pd.DataFrame  Listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with percentage columns as float.
    """
    df = df.copy()
    pct_cols = ["host_response_rate", "host_acceptance_rate"]
    for col in pct_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace("%", "", regex=False)
                .replace("nan", np.nan)
                .astype(float) / 100
            )
    print(f"  percentage columns fixed: {pct_cols}")
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse date columns to datetime.

    Affected: host_since, first_review, last_review.

    Parameters
    ----------
    df : pd.DataFrame  Listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with date columns parsed.
    """
    df = df.copy()
    date_cols = ["host_since", "first_review", "last_review"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    print(f"  date columns parsed: {date_cols}")
    return df


def impute_review_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing review scores with neighbourhood median.

    ~12% of listings have no reviews yet → scores are null.
    Strategy: median by neighbourhood_group_cleansed.
    These listings are new and not penalized with a 0.

    Parameters
    ----------
    df : pd.DataFrame  Listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with review scores imputed.
    """
    df = df.copy()
    for col in SCORE_COLS:
        if col in df.columns:
            n_before = df[col].isna().sum()
            group_med = df.groupby(
                "neighbourhood_group_cleansed"
            )[col].transform("median")
            df[col] = df[col].fillna(group_med)
            df[col] = df[col].fillna(df[col].median())
            print(f"  {col}: {n_before} nulls imputed")
    return df


def add_host_segment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify hosts into Amateur / Semi-pro / Profesional segments.

    Segmentation based on calculated_host_listings_count:
    - Amateur:    1 listing
    - Semi-pro:   2–5 listings
    - Profesional: 6+ listings

    Parameters
    ----------
    df : pd.DataFrame  Listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with 'host_segment' column added.
    """
    df = df.copy()

    def segment(n):
        if n <= HOST_AMATEUR_MAX:
            return "Amateur"
        elif n <= HOST_SEMIPRO_MAX:
            return "Semi-pro"
        else:
            return "Profesional"

    df["host_segment"] = df["calculated_host_listings_count"].apply(segment)
    print(f"  host_segment added: {df['host_segment'].value_counts().to_dict()}")
    return df


def add_zone(df: pd.DataFrame, zone_map: dict) -> pd.DataFrame:
    """
    Add macro zone column based on neighbourhood_group_cleansed.

    Groups the 19 neighbourhoods into 6 macro zones for higher-level analysis.

    Parameters
    ----------
    df       : pd.DataFrame  Listings DataFrame.
    zone_map : dict          Mapping from zone name to list of neighbourhoods.

    Returns
    -------
    pd.DataFrame  DataFrame with 'zone' column added.
    """
    df = df.copy()
    reverse_map = {}
    for zone, hoods in zone_map.items():
        for hood in hoods:
            reverse_map[hood] = zone
    df["zone"] = df["neighbourhood_group_cleansed"].map(reverse_map).fillna("OTHER")
    print(f"  zone added: {df['zone'].value_counts().to_dict()}")
    return df


def clean_calendar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the calendar dataset.

    Issues:
    - 'available' stored as 't'/'f' → bool
    - 'price' column is fully null in this dataset (known limitation)
    - Add month and season columns for seasonality analysis

    Parameters
    ----------
    df : pd.DataFrame  Raw calendar DataFrame.

    Returns
    -------
    pd.DataFrame  Cleaned calendar DataFrame.
    """
    df = df.copy()
    df["available"] = df["available"].map({"t": True, "f": False})
    df["month"]  = df["date"].dt.month
    df["year"]   = df["date"].dt.year
    df["season"] = df["month"].map({
        12: "Invierno", 1: "Invierno", 2: "Invierno",
        3: "Primavera", 4: "Primavera", 5: "Primavera",
        6: "Verano",    7: "Verano",    8: "Verano",
        9: "Otoño",    10: "Otoño",    11: "Otoño",
    })
    print(f"  calendar cleaned — available: {df['available'].value_counts().to_dict()}")
    return df


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the reviews dataset.

    Issues:
    - Add year and month columns for trend analysis
    - Drop rows with null comments

    Parameters
    ----------
    df : pd.DataFrame  Raw reviews DataFrame.

    Returns
    -------
    pd.DataFrame  Cleaned reviews DataFrame.
    """
    df = df.copy()
    df = df.dropna(subset=["comments"])
    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month
    print(f"  reviews cleaned — {len(df):,} rows remaining")
    return df


def run_full_pipeline(df_listings: pd.DataFrame,
                      df_calendar: pd.DataFrame,
                      df_reviews: pd.DataFrame,
                      zone_map: dict) -> tuple:
    """
    Run the full cleaning pipeline on all three datasets.

    Parameters
    ----------
    df_listings : pd.DataFrame  Raw listings.
    df_calendar : pd.DataFrame  Raw calendar.
    df_reviews  : pd.DataFrame  Raw reviews.
    zone_map    : dict          Zone mapping from config.

    Returns
    -------
    tuple  (listings_clean, calendar_clean, reviews_clean)
    """
    print("\n🔧 CLEANING LISTINGS ───────────────────────────────────")
    df_l = drop_irrelevant_columns(df_listings)
    df_l = fix_boolean_columns(df_l)
    df_l = fix_percentage_columns(df_l)
    df_l = parse_dates(df_l)
    df_l = clean_price(df_l)
    df_l = impute_missing_price(df_l)
    df_l = impute_review_scores(df_l)
    df_l = add_host_segment(df_l)
    df_l = add_zone(df_l, zone_map)
    print(f"  ✅ listings_clean: {df_l.shape}")

    print("\n🔧 CLEANING CALENDAR ───────────────────────────────────")
    df_c = clean_calendar(df_calendar)
    print(f"  ✅ calendar_clean: {df_c.shape}")

    print("\n🔧 CLEANING REVIEWS ────────────────────────────────────")
    df_r = clean_reviews(df_reviews)
    print(f"  ✅ reviews_clean: {df_r.shape}")

    return df_l, df_c, df_r
