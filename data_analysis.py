"""
modules/data_analysis.py
========================
Core analytical functions:
  - Statistical summary
  - Missing value analysis
  - Duplicate detection
  - Correlation matrix computation
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ─── Statistical Summary ──────────────────────────────────────────────────────
def compute_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute an enriched descriptive statistics table for all numeric columns.

    Extends pd.DataFrame.describe() with:
      - Median, Mode (first), Variance, Skewness, Kurtosis
      - IQR, 5th / 95th percentiles
      - Missing count & percentage

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame  – transposed so columns = statistics, rows = variables
    """
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return pd.DataFrame({"Note": ["No numeric columns found."]})

    desc = numeric_df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T

    # Rename percentile columns for clarity
    desc.rename(
        columns={
            "5%": "P5",
            "25%": "Q1",
            "50%": "Median",
            "75%": "Q3",
            "95%": "P95",
        },
        inplace=True,
    )

    # Additional statistics
    desc["Mode"] = numeric_df.mode().iloc[0]
    desc["Variance"] = numeric_df.var()
    desc["Skewness"] = numeric_df.skew()
    desc["Kurtosis"] = numeric_df.kurt()
    desc["IQR"] = desc["Q3"] - desc["Q1"]
    desc["Missing Count"] = numeric_df.isnull().sum()
    desc["Missing %"] = (desc["Missing Count"] / len(df) * 100).round(2)

    # Reorder columns for readability
    ordered_cols = [
        "count", "mean", "Mode", "Median",
        "std", "Variance", "Skewness", "Kurtosis",
        "min", "P5", "Q1", "Q3", "P95", "max",
        "IQR", "Missing Count", "Missing %",
    ]
    available = [c for c in ordered_cols if c in desc.columns]
    return desc[available]


# ─── Missing Value Analysis ───────────────────────────────────────────────────
def detect_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame summarising missing values for every column.

    Columns:
      - Missing Count
      - Missing %
      - Data Type
      - Completeness %

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame  sorted by Missing Count descending
    """
    total = len(df)
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / total * 100).round(2)
    completeness = (100 - missing_pct).round(2)

    result = pd.DataFrame(
        {
            "Missing Count": missing_count,
            "Missing %": missing_pct,
            "Completeness %": completeness,
            "Data Type": df.dtypes.astype(str),
        }
    )
    return result.sort_values("Missing Count", ascending=False)


# ─── Duplicate Detection ──────────────────────────────────────────────────────
def detect_duplicates(df: pd.DataFrame) -> tuple[int, pd.DataFrame]:
    """
    Find duplicate rows in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    dup_count : int
    dup_df    : pd.DataFrame  – the actual duplicate rows (empty if none)
    """
    mask = df.duplicated(keep=False)
    dup_df = df[mask].copy()
    return int(mask.sum()), dup_df


# ─── Correlation Matrix ───────────────────────────────────────────────────────
def compute_correlations(
    df: pd.DataFrame,
    numeric_cols: list[str],
    method: str = "pearson",
) -> pd.DataFrame:
    """
    Compute a pairwise correlation matrix for the supplied numeric columns.

    Parameters
    ----------
    df           : pd.DataFrame
    numeric_cols : list[str]   – subset of numeric column names
    method       : str         – 'pearson', 'kendall', or 'spearman'

    Returns
    -------
    pd.DataFrame  – square correlation matrix
    """
    if not numeric_cols:
        return pd.DataFrame()

    subset = df[numeric_cols].select_dtypes(include="number")
    corr = subset.corr(method=method)
    return corr


# ─── Outlier Detection (helper used by insights) ──────────────────────────────
def detect_outliers_iqr(df: pd.DataFrame, col: str) -> dict:
    """
    Detect outliers in a single numeric column using the IQR fence method.

    Parameters
    ----------
    df  : pd.DataFrame
    col : str  – numeric column name

    Returns
    -------
    dict with keys:
      - 'count'      : int   number of outlier rows
      - 'pct'        : float percentage of all non-null rows
      - 'lower_fence': float
      - 'upper_fence': float
    """
    series = df[col].dropna()
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = series[(series < lower) | (series > upper)]
    pct = (len(outliers) / len(series) * 100) if len(series) > 0 else 0.0

    return {
        "count": len(outliers),
        "pct": round(pct, 2),
        "lower_fence": round(lower, 4),
        "upper_fence": round(upper, 4),
    }
