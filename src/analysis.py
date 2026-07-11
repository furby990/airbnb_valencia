"""
analysis.py
===========
Statistical analysis functions for the Valencia Airbnb Investment Analysis.
Includes hypothesis testing, correlation analysis, and descriptive statistics.
All tests use significance level defined in config.ALPHA.
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import ALPHA


def test_normality(series: pd.Series, name: str = "") -> dict:
    """
    Test normality using Shapiro-Wilk test (sample ≤ 5000) or
    D'Agostino-Pearson test (larger samples).

    Parameters
    ----------
    series : pd.Series  Data to test.
    name   : str        Variable name for display.

    Returns
    -------
    dict  {statistic, p_value, is_normal, test_used}
    """
    data = series.dropna()
    if len(data) <= 5000:
        stat, p = stats.shapiro(data.sample(min(5000, len(data)), random_state=42))
        test = "Shapiro-Wilk"
    else:
        stat, p = stats.normaltest(data)
        test = "D'Agostino-Pearson"

    is_normal = p > ALPHA
    print(f"  Normality ({name}) — {test}: stat={stat:.4f}, p={p:.4f} → "
          f"{'NORMAL ✅' if is_normal else 'NOT NORMAL ⚠️'} (α={ALPHA})")
    return {"statistic": stat, "p_value": p, "is_normal": is_normal, "test": test}


def test_superhost_revenue(df: pd.DataFrame) -> dict:
    """
    H0: There is no significant difference in estimated revenue between
        Superhosts and regular hosts.
    H1: Superhosts generate significantly higher revenue.

    Uses Mann-Whitney U test (non-parametric) since revenue is not normally
    distributed (right-skewed).

    Parameters
    ----------
    df : pd.DataFrame  Cleaned listings with 'host_is_superhost' and
                       'estimated_revenue_l365d'.

    Returns
    -------
    dict  Test results with interpretation.
    """
    superhost  = df[df["host_is_superhost"] == True]["estimated_revenue_l365d"].dropna()
    regular    = df[df["host_is_superhost"] == False]["estimated_revenue_l365d"].dropna()

    stat, p = stats.mannwhitneyu(superhost, regular, alternative="greater")

    result = {
        "test":           "Mann-Whitney U",
        "h0":             "No difference in revenue between Superhosts and regular hosts",
        "h1":             "Superhosts generate higher revenue",
        "statistic":      stat,
        "p_value":        p,
        "reject_h0":      p < ALPHA,
        "superhost_median": superhost.median(),
        "regular_median": regular.median(),
        "n_superhost":    len(superhost),
        "n_regular":      len(regular),
    }

    print(f"\n{'='*60}")
    print(f"HYPOTHESIS TEST: Superhost vs Regular Revenue")
    print(f"  H0: {result['h0']}")
    print(f"  H1: {result['h1']}")
    print(f"  Test: {result['test']}")
    print(f"  Statistic: {stat:.2f} | p-value: {p:.6f}")
    print(f"  Superhost median revenue:  €{superhost.median():,.0f}/year")
    print(f"  Regular host median revenue: €{regular.median():,.0f}/year")
    if result["reject_h0"]:
        print(f"  ✅ REJECT H0 (p={p:.4f} < α={ALPHA}): Superhosts earn significantly more")
    else:
        print(f"  ❌ FAIL TO REJECT H0 (p={p:.4f} ≥ α={ALPHA})")
    print(f"{'='*60}")
    return result


def test_room_type_price(df: pd.DataFrame) -> dict:
    """
    H0: Price is equal across all room types.
    H1: At least one room type has a significantly different price.

    Uses Kruskal-Wallis test (non-parametric ANOVA equivalent).

    Parameters
    ----------
    df : pd.DataFrame  Cleaned listings with 'room_type' and 'price_eur'.

    Returns
    -------
    dict  Test results with group medians.
    """
    groups = [
        df[df["room_type"] == rt]["price_eur"].dropna().values
        for rt in df["room_type"].unique()
    ]
    stat, p = stats.kruskal(*groups)

    group_medians = df.groupby("room_type")["price_eur"].median().to_dict()

    result = {
        "test":          "Kruskal-Wallis",
        "h0":            "Price is equal across all room types",
        "h1":            "At least one room type has different price",
        "statistic":     stat,
        "p_value":       p,
        "reject_h0":     p < ALPHA,
        "group_medians": group_medians,
    }

    print(f"\n{'='*60}")
    print(f"HYPOTHESIS TEST: Price by Room Type")
    print(f"  Test: Kruskal-Wallis | stat={stat:.2f} | p={p:.6f}")
    print(f"  Group medians: {group_medians}")
    print(f"  {'✅ REJECT H0' if result['reject_h0'] else '❌ FAIL TO REJECT H0'} (α={ALPHA})")
    print(f"{'='*60}")
    return result


def test_neighbourhood_price(df: pd.DataFrame) -> dict:
    """
    H0: Price is equal across all neighbourhoods.
    H1: At least one neighbourhood has a significantly different price.

    Uses Kruskal-Wallis test.

    Parameters
    ----------
    df : pd.DataFrame  Cleaned listings.

    Returns
    -------
    dict  Test results.
    """
    col = "neighbourhood_group_cleansed"
    groups = [
        df[df[col] == nh]["price_eur"].dropna().values
        for nh in df[col].unique()
    ]
    stat, p = stats.kruskal(*[g for g in groups if len(g) > 0])

    result = {
        "test":      "Kruskal-Wallis",
        "h0":        "Price is equal across all neighbourhoods",
        "h1":        "At least one neighbourhood has different price",
        "statistic": stat,
        "p_value":   p,
        "reject_h0": p < ALPHA,
    }

    print(f"\n{'='*60}")
    print(f"HYPOTHESIS TEST: Price by Neighbourhood")
    print(f"  Test: Kruskal-Wallis | stat={stat:.2f} | p={p:.6f}")
    print(f"  {'✅ REJECT H0' if result['reject_h0'] else '❌ FAIL TO REJECT H0'} (α={ALPHA})")
    print(f"{'='*60}")
    return result


def correlation_matrix(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """
    Compute Spearman correlation matrix for selected columns.

    Spearman chosen because price and revenue are not normally distributed.

    Parameters
    ----------
    df   : pd.DataFrame  Cleaned listings.
    cols : list          Columns to include in the matrix.

    Returns
    -------
    pd.DataFrame  Spearman correlation matrix.
    """
    data = df[cols].dropna()
    corr = data.corr(method="spearman")
    print(f"✅ Spearman correlation matrix computed ({len(data):,} rows, {len(cols)} variables)")
    return corr


def price_drivers_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Spearman correlation of numeric features with price.

    Used to identify the most important price drivers.

    Parameters
    ----------
    df : pd.DataFrame  Cleaned listings with 'price_eur'.

    Returns
    -------
    pd.DataFrame  Sorted correlation values with p-values.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    exclude = ["id", "host_id", "latitude", "longitude",
               "price_eur", "log_price"]
    cols = [c for c in numeric_cols if c not in exclude]

    results = []
    for col in cols:
        data = df[["price_eur", col]].dropna()
        if len(data) < 10:
            continue
        rho, p = stats.spearmanr(data["price_eur"], data[col])
        results.append({
            "feature":     col,
            "spearman_rho": round(rho, 4),
            "p_value":     round(p, 6),
            "significant": p < ALPHA,
        })

    result_df = (
        pd.DataFrame(results)
        .sort_values("spearman_rho", key=abs, ascending=False)
        .reset_index(drop=True)
    )
    print(f"✅ Price drivers identified — top 5:")
    print(result_df.head(5)[["feature","spearman_rho","p_value","significant"]].to_string(index=False))
    return result_df


def descriptive_stats(df: pd.DataFrame, group_col: str,
                      value_col: str) -> pd.DataFrame:
    """
    Compute descriptive statistics for a value column grouped by a category.

    Parameters
    ----------
    df        : pd.DataFrame  Input DataFrame.
    group_col : str           Column to group by.
    value_col : str           Numeric column to describe.

    Returns
    -------
    pd.DataFrame  Descriptive stats (count, mean, median, std, min, max).
    """
    return (
        df.groupby(group_col)[value_col]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .round(2)
        .sort_values("median", ascending=False)
    )
