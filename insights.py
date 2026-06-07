"""
modules/insights.py
===================
Generates rule-based "AI-like" textual insights about the uploaded dataset.

Insight categories:
  ✅ Dataset shape & completeness
  📈 Highest / lowest values
  🔗 Strong correlations
  ⚠️  Missing data observations
  🚨 Outlier warnings
  📊 Skewness / distribution shape
  🔁 Duplicate rows
  🏷️  High-cardinality categorical columns
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from modules.data_analysis import compute_correlations, detect_outliers_iqr


def generate_insights(df: pd.DataFrame, col_types: dict) -> list[dict]:
    """
    Analyse the DataFrame and return a list of insight dicts.

    Each dict has the keys:
      - 'message' : str   – human-readable insight text
      - 'level'   : str   – 'info' | 'warning' | 'success' | 'error'
      - 'icon'    : str   – emoji prefix

    Parameters
    ----------
    df        : pd.DataFrame
    col_types : dict  – output of detect_column_types()

    Returns
    -------
    list[dict]
    """
    insights: list[dict] = []
    numeric_cols: list[str] = col_types.get("numeric", [])
    cat_cols: list[str] = col_types.get("categorical", [])

    # ── 1. Dataset overview ──────────────────────────────────────────────────
    insights.append(
        {
            "icon": "📋",
            "level": "info",
            "message": (
                f"Dataset contains **{df.shape[0]:,} rows** and **{df.shape[1]} columns** "
                f"({len(numeric_cols)} numeric, {len(cat_cols)} categorical)."
            ),
        }
    )

    # ── 2. Missing data ──────────────────────────────────────────────────────
    total_cells = df.size
    missing_cells = int(df.isnull().sum().sum())
    missing_pct = missing_cells / total_cells * 100

    if missing_cells == 0:
        insights.append(
            {
                "icon": "✅",
                "level": "success",
                "message": "No missing values detected — the dataset is complete.",
            }
        )
    else:
        most_missing_col = df.isnull().sum().idxmax()
        most_missing_n = int(df[most_missing_col].isnull().sum())
        insights.append(
            {
                "icon": "⚠️",
                "level": "warning",
                "message": (
                    f"**{missing_cells:,} missing values** found across the dataset "
                    f"({missing_pct:.1f}% of all cells). "
                    f"Column **'{most_missing_col}'** has the most missing values ({most_missing_n:,})."
                ),
            }
        )

    # ── 3. Duplicates ────────────────────────────────────────────────────────
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        insights.append(
            {
                "icon": "🔁",
                "level": "warning",
                "message": (
                    f"**{dup_count:,} duplicate rows** detected "
                    f"({dup_count / len(df) * 100:.1f}% of total). "
                    "Consider removing them before analysis."
                ),
            }
        )

    # ── 4. Highest & lowest values per numeric column ────────────────────────
    for col in numeric_cols[:5]:  # cap at 5 to avoid flooding
        series = df[col].dropna()
        if series.empty:
            continue
        max_val = series.max()
        min_val = series.min()
        max_idx = series.idxmax()
        min_idx = series.idxmin()
        insights.append(
            {
                "icon": "📈",
                "level": "info",
                "message": (
                    f"**{col}** — highest value: **{max_val:,.4g}** (row {max_idx}), "
                    f"lowest value: **{min_val:,.4g}** (row {min_idx})."
                ),
            }
        )

    # ── 5. Strong correlations ───────────────────────────────────────────────
    if len(numeric_cols) >= 2:
        corr = compute_correlations(df, numeric_cols)
        strong_pairs: list[tuple[str, str, float]] = []

        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                r = corr.iloc[i, j]
                if abs(r) >= 0.7 and not np.isnan(r):
                    strong_pairs.append((corr.columns[i], corr.columns[j], round(r, 3)))

        if strong_pairs:
            for col_a, col_b, r in strong_pairs[:5]:  # top 5 pairs
                direction = "positive" if r > 0 else "negative"
                emoji = "📈" if r > 0 else "📉"
                insights.append(
                    {
                        "icon": "🔗",
                        "level": "info",
                        "message": (
                            f"**Strong {direction} correlation** between **'{col_a}'** and "
                            f"**'{col_b}'**: r = {r} {emoji}"
                        ),
                    }
                )
        else:
            insights.append(
                {
                    "icon": "🔗",
                    "level": "info",
                    "message": "No strong correlations (|r| ≥ 0.7) found between numeric columns.",
                }
            )

    # ── 6. Outlier warnings ──────────────────────────────────────────────────
    for col in numeric_cols[:8]:  # cap at 8 columns
        outs = detect_outliers_iqr(df, col)
        if outs["count"] > 0:
            severity = "error" if outs["pct"] > 10 else "warning"
            insights.append(
                {
                    "icon": "🚨",
                    "level": severity,
                    "message": (
                        f"**'{col}'** has **{outs['count']:,} outlier(s)** "
                        f"({outs['pct']:.1f}% of values) outside the IQR fence "
                        f"[{outs['lower_fence']:,.4g}, {outs['upper_fence']:,.4g}]."
                    ),
                }
            )

    # ── 7. Skewness ──────────────────────────────────────────────────────────
    for col in numeric_cols[:5]:
        series = df[col].dropna()
        if series.empty or series.std() == 0:
            continue
        skew = series.skew()
        if abs(skew) > 1.5:
            direction = "right (positively)" if skew > 0 else "left (negatively)"
            insights.append(
                {
                    "icon": "📊",
                    "level": "info",
                    "message": (
                        f"**'{col}'** is heavily skewed {direction} (skewness = {skew:.2f}). "
                        "A log transform may improve analysis."
                    ),
                }
            )

    # ── 8. High-cardinality categorical columns ──────────────────────────────
    for col in cat_cols:
        n_unique = df[col].nunique()
        if n_unique > 50:
            insights.append(
                {
                    "icon": "🏷️",
                    "level": "info",
                    "message": (
                        f"Categorical column **'{col}'** has **{n_unique:,} unique values** — "
                        "consider grouping or encoding for modelling."
                    ),
                }
            )

    # ── 9. Constant columns ──────────────────────────────────────────────────
    for col in df.columns:
        if df[col].nunique(dropna=True) <= 1:
            insights.append(
                {
                    "icon": "⚡",
                    "level": "warning",
                    "message": (
                        f"Column **'{col}'** has **only one unique value** — "
                        "it provides no predictive information and can be dropped."
                    ),
                }
            )

    return insights
