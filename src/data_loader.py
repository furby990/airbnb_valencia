"""
data_loader.py
==============
Functions for loading raw Airbnb Valencia datasets.
All paths sourced from config.py — no hard-coded values.
"""

import pandas as pd
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import FILES


def load_listings(filepath: Path = FILES["listings"]) -> pd.DataFrame:
    """
    Load the detailed listings dataset.

    Parameters
    ----------
    filepath : Path
        Path to listings.csv (default from config).

    Returns
    -------
    pd.DataFrame
        Raw listings DataFrame with 79 columns.
    """
    df = pd.read_csv(filepath, low_memory=False)
    print(f"✅ listings.csv loaded — {len(df):,} rows × {df.shape[1]} cols")
    return df


def load_calendar(filepath: Path = FILES["calendar"]) -> pd.DataFrame:
    """
    Load the calendar dataset (availability and price by listing × date).

    Parameters
    ----------
    filepath : Path
        Path to calendar.csv (default from config).

    Returns
    -------
    pd.DataFrame
        Raw calendar DataFrame with date parsed as datetime.
    """
    df = pd.read_csv(filepath, parse_dates=["date"], low_memory=False)
    print(f"✅ calendar.csv loaded — {len(df):,} rows × {df.shape[1]} cols")
    print(f"   Period: {df['date'].min().date()} → {df['date'].max().date()}")
    return df


def load_reviews(filepath: Path = FILES["reviews"]) -> pd.DataFrame:
    """
    Load the reviews dataset with full comment text.

    Parameters
    ----------
    filepath : Path
        Path to reviews.csv (default from config).

    Returns
    -------
    pd.DataFrame
        Raw reviews DataFrame with date parsed as datetime.
    """
    df = pd.read_csv(filepath, parse_dates=["date"], low_memory=False)
    print(f"✅ reviews.csv loaded — {len(df):,} rows × {df.shape[1]} cols")
    print(f"   Period: {df['date'].min().date()} → {df['date'].max().date()}")
    return df


def load_neighbourhoods(filepath: Path = FILES["neighbourhoods"]) -> pd.DataFrame:
    """
    Load the neighbourhoods reference dataset.

    Parameters
    ----------
    filepath : Path
        Path to neighbourhoods.csv (default from config).

    Returns
    -------
    pd.DataFrame
        Neighbourhoods with group and name columns.
    """
    df = pd.read_csv(filepath)
    print(f"✅ neighbourhoods.csv loaded — {len(df):,} rows")
    return df


def load_geojson(filepath: Path = FILES["geojson"]) -> dict:
    """
    Load the GeoJSON file for choropleth maps.

    Parameters
    ----------
    filepath : Path
        Path to neighbourhoods.geojson (default from config).

    Returns
    -------
    dict
        GeoJSON dictionary for use with Plotly.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        geo = json.load(f)
    print(f"✅ geojson loaded — {len(geo['features'])} neighbourhoods")
    return geo


def load_all() -> dict:
    """
    Load all datasets at once.

    Returns
    -------
    dict
        Dictionary with keys: listings, calendar, reviews,
        neighbourhoods, geojson.
    """
    return {
        "listings":       load_listings(),
        "calendar":       load_calendar(),
        "reviews":        load_reviews(),
        "neighbourhoods": load_neighbourhoods(),
        "geojson":        load_geojson(),
    }
