"""
features.py
===========
Feature engineering functions for the Valencia Airbnb Investment Analysis.
Builds the Investment Score and all derived features.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import SCORE_WEIGHTS


def normalize_series(s: pd.Series) -> pd.Series:
    """
    Min-max normalize a series to [0, 1] range.

    Parameters
    ----------
    s : pd.Series  Input series.

    Returns
    -------
    pd.Series  Normalized series.
    """
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - mn) / (mx - mn)


def build_investment_score(df: pd.DataFrame,
                           df_reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Build the Investment Score by neighbourhood.

    The score is a weighted composite of 5 normalized metrics:
    1. revenue_score     (35%) — median estimated annual revenue
    2. occupancy_score   (25%) — median estimated occupancy
    3. demand_growth     (20%) — YoY growth in review count (proxy for demand)
    4. competition_score (10%) — inverse of listing density
    5. price_score       (10%) — median price relative to Valencia average

    Weights defined in config.SCORE_WEIGHTS.

    Parameters
    ----------
    df         : pd.DataFrame  Cleaned listings DataFrame.
    df_reviews : pd.DataFrame  Cleaned reviews DataFrame.

    Returns
    -------
    pd.DataFrame  One row per neighbourhood with score and components.
    """
    hood_col = "neighbourhood_group_cleansed"

    # ── Component 1: Revenue ─────────────────────────────────────────────────
    revenue = df.groupby(hood_col)["estimated_revenue_l365d"].median()

    # ── Component 2: Occupancy ───────────────────────────────────────────────
    occupancy = df.groupby(hood_col)["estimated_occupancy_l365d"].median()

    # ── Component 3: Demand growth (YoY reviews) ─────────────────────────────
    rev_by_year = (
        df_reviews.merge(
            df[[hood_col, "id"]].rename(columns={"id": "listing_id"}),
            on="listing_id", how="left"
        )
        .groupby([hood_col, "year"])
        .size()
        .reset_index(name="review_count")
    )
    recent = rev_by_year[rev_by_year["year"] == rev_by_year["year"].max()]
    prev   = rev_by_year[rev_by_year["year"] == rev_by_year["year"].max() - 1]
    merged_rev = recent.merge(prev, on=hood_col, suffixes=("_now", "_prev"))
    merged_rev["demand_growth"] = (
        (merged_rev["review_count_now"] - merged_rev["review_count_prev"])
        / merged_rev["review_count_prev"].replace(0, np.nan)
    ).fillna(0)
    demand_growth = merged_rev.set_index(hood_col)["demand_growth"]

    # ── Component 4: Competition (inverse density) ────────────────────────────
    listing_count = df.groupby(hood_col)["id"].count()
    competition   = 1 / listing_count  # fewer listings = less competition = better

    # ── Component 5: Price relative to market ─────────────────────────────────
    global_median = df["price_eur"].median()
    price_by_hood = df.groupby(hood_col)["price_eur"].median()
    price_score   = price_by_hood / global_median  # > 1 = premium market

    # ── Assemble and normalize ────────────────────────────────────────────────
    score_df = pd.DataFrame({
        "revenue_score":     revenue,
        "occupancy_score":   occupancy,
        "demand_growth":     demand_growth,
        "competition_score": competition,
        "price_score":       price_score,
        "n_listings":        listing_count,
        "median_price":      price_by_hood,
        "median_revenue":    revenue,
        "median_occupancy":  occupancy,
    }).fillna(0)

    # Normalize each component
    for col in ["revenue_score","occupancy_score","demand_growth",
                "competition_score","price_score"]:
        score_df[f"{col}_norm"] = normalize_series(score_df[col])

    # Weighted composite score
    score_df["investment_score"] = (
        score_df["revenue_score_norm"]     * SCORE_WEIGHTS["revenue_score"]     +
        score_df["occupancy_score_norm"]   * SCORE_WEIGHTS["occupancy_score"]   +
        score_df["demand_growth_norm"]     * SCORE_WEIGHTS["demand_growth"]     +
        score_df["competition_score_norm"] * SCORE_WEIGHTS["competition_score"] +
        score_df["price_score_norm"]       * SCORE_WEIGHTS["price_score"]
    )
    score_df["investment_score"] = (score_df["investment_score"] * 100).round(1)
    score_df = score_df.sort_values("investment_score", ascending=False)
    score_df["rank"] = range(1, len(score_df) + 1)

    print(f"✅ Investment score built for {len(score_df)} neighbourhoods")
    print(score_df[["rank","investment_score","median_revenue","median_occupancy","n_listings"]].to_string())
    return score_df.reset_index()


def add_log_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add log-transformed price column for regression analysis.

    Price is right-skewed — log transformation achieves near-normality,
    required for linear regression assumptions.

    Parameters
    ----------
    df : pd.DataFrame  Listings with 'price_eur'.

    Returns
    -------
    pd.DataFrame  DataFrame with 'log_price' column added.
    """
    df = df.copy()
    df["log_price"] = np.log1p(df["price_eur"])
    return df


def add_revenue_per_night(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add effective revenue per available night.

    Formula: estimated_revenue_l365d / (availability_365 + 1)
    This captures actual earning efficiency, not just headline revenue.

    Parameters
    ----------
    df : pd.DataFrame  Listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with 'revenue_per_night' column.
    """
    df = df.copy()
    df["revenue_per_night"] = (
        df["estimated_revenue_l365d"] /
        (df["availability_365"] + 1)
    ).round(2)
    return df


def build_seasonality_table(df_calendar: pd.DataFrame,
                             df_listings: pd.DataFrame) -> pd.DataFrame:
    """
    Build monthly occupancy table by neighbourhood.

    Merges calendar with listings to get neighbourhood info,
    then calculates occupancy rate (booked / total days) per month.

    Parameters
    ----------
    df_calendar : pd.DataFrame  Cleaned calendar DataFrame.
    df_listings : pd.DataFrame  Cleaned listings DataFrame.

    Returns
    -------
    pd.DataFrame  Monthly occupancy rate by neighbourhood.
    """
    hood_map = df_listings.set_index("id")["neighbourhood_group_cleansed"]
    df_cal = df_calendar.copy()
    df_cal["neighbourhood"] = df_cal["listing_id"].map(hood_map)
    df_cal = df_cal.dropna(subset=["neighbourhood"])

    seasonal = (
        df_cal.groupby(["neighbourhood", "month"])
        .agg(
            total_days = ("available", "count"),
            booked_days = ("available", lambda x: (~x).sum()),
        )
        .reset_index()
    )
    seasonal["occupancy_rate"] = (
        seasonal["booked_days"] / seasonal["total_days"] * 100
    ).round(1)
    print(f"✅ Seasonality table built: {seasonal.shape}")
    return seasonal


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode categorical columns for statistical analysis.

    - room_type → dummy variables
    - host_segment → ordinal encoding (Amateur=0, Semi-pro=1, Profesional=2)
    - host_is_superhost → int (True=1, False=0)

    Parameters
    ----------
    df : pd.DataFrame  Cleaned listings DataFrame.

    Returns
    -------
    pd.DataFrame  DataFrame with encoded columns added.
    """
    df = df.copy()
    # Room type dummies
    room_dummies = pd.get_dummies(df["room_type"], prefix="room", drop_first=True)
    df = pd.concat([df, room_dummies], axis=1)

    # Host segment ordinal
    segment_map = {"Amateur": 0, "Semi-pro": 1, "Profesional": 2}
    df["host_segment_enc"] = df["host_segment"].map(segment_map)

    # Superhost to int
    if "host_is_superhost" in df.columns:
        df["superhost_int"] = df["host_is_superhost"].astype(int)

    print(f"  categoricals encoded — columns added: room dummies, host_segment_enc, superhost_int")
    return df
