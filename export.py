"""
modules/export.py
=================
Data export helpers:
  - download_cleaned_csv  : removes duplicates & all-null rows, returns CSV bytes
  - download_summary_report: generates a comprehensive plain-text analysis report
"""

from __future__ import annotations

import io
from datetime import datetime

import pandas as pd

from modules.data_analysis import compute_statistics, detect_missing_values, detect_duplicates
from modules.data_loader import detect_column_types


# ─── Cleaned CSV ──────────────────────────────────────────────────────────────
def download_cleaned_csv(df: pd.DataFrame) -> bytes:
    """
    Return a cleaned version of *df* as UTF-8 encoded CSV bytes.

    Cleaning steps applied:
      1. Drop fully duplicate rows (keep first occurrence)
      2. Drop rows where every value is null
      3. Strip leading/trailing whitespace from string columns

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    bytes  – UTF-8 CSV
    """
    cleaned = df.copy()

    # Step 1 – drop duplicates
    cleaned = cleaned.drop_duplicates()

    # Step 2 – drop all-null rows
    cleaned = cleaned.dropna(how="all")

    # Step 3 – strip whitespace from object columns
    str_cols = cleaned.select_dtypes(include="object").columns
    for col in str_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    buffer = io.StringIO()
    cleaned.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


# ─── Summary Report ───────────────────────────────────────────────────────────
def download_summary_report(
    df: pd.DataFrame,
    col_types: dict,
    filename: str,
) -> bytes:
    """
    Generate a human-readable plain-text summary report and return it as bytes.

    Sections:
      1. File & Dataset Info
      2. Column Types
      3. Missing Value Summary
      4. Duplicate Summary
      5. Statistical Summary (numeric columns)

    Parameters
    ----------
    df        : pd.DataFrame
    col_types : dict  – from detect_column_types()
    filename  : str   – original uploaded filename

    Returns
    -------
    bytes  – UTF-8 plain text
    """
    lines: list[str] = []
    sep = "=" * 70

    def h(title: str) -> None:
        lines.append("")
        lines.append(sep)
        lines.append(f"  {title.upper()}")
        lines.append(sep)

    def sub(title: str) -> None:
        lines.append(f"\n── {title} ──")

    # ── Header ───────────────────────────────────────────────────────────────
    lines.append(sep)
    lines.append("  SMART ANALYTICS ASSISTANT — DATA SUMMARY REPORT")
    lines.append(sep)
    lines.append(f"  Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Source File: {filename}")
    lines.append(sep)

    # ── 1. Dataset Info ───────────────────────────────────────────────────────
    h("1. Dataset Overview")
    lines.append(f"  Rows       : {df.shape[0]:,}")
    lines.append(f"  Columns    : {df.shape[1]}")
    lines.append(f"  Total Cells: {df.size:,}")
    lines.append(f"  Memory     : {df.memory_usage(deep=True).sum() / 1024:.1f} KB")

    # ── 2. Column Types ───────────────────────────────────────────────────────
    h("2. Column Types")
    for category, cols in col_types.items():
        if cols:
            lines.append(f"\n  {category.capitalize()} ({len(cols)})")
            for c in cols:
                lines.append(f"    • {c}")

    # ── 3. Missing Values ─────────────────────────────────────────────────────
    h("3. Missing Value Analysis")
    missing_df = detect_missing_values(df)
    has_missing = missing_df[missing_df["Missing Count"] > 0]

    if has_missing.empty:
        lines.append("  ✅ No missing values found.")
    else:
        lines.append(f"  Total missing cells : {int(missing_df['Missing Count'].sum()):,}")
        lines.append(
            f"  Missing cell %      : {missing_df['Missing Count'].sum() / df.size * 100:.2f}%"
        )
        lines.append("")
        lines.append(f"  {'Column':<30} {'Missing':>10} {'Missing %':>12} {'Completeness %':>16}")
        lines.append("  " + "-" * 68)
        for idx, row in has_missing.iterrows():
            lines.append(
                f"  {str(idx):<30} {int(row['Missing Count']):>10,} "
                f"{row['Missing %']:>11.1f}% {row['Completeness %']:>15.1f}%"
            )

    # ── 4. Duplicates ─────────────────────────────────────────────────────────
    h("4. Duplicate Row Detection")
    dup_count, _ = detect_duplicates(df)
    if dup_count == 0:
        lines.append("  ✅ No duplicate rows found.")
    else:
        lines.append(f"  ⚠️  Duplicate rows : {dup_count:,} ({dup_count / len(df) * 100:.1f}%)")

    # ── 5. Statistical Summary ────────────────────────────────────────────────
    h("5. Statistical Summary (Numeric Columns)")
    numeric_cols = col_types.get("numeric", [])

    if not numeric_cols:
        lines.append("  No numeric columns found.")
    else:
        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            sub(col)
            stats = {
                "Count"   : f"{len(series):,}",
                "Mean"    : f"{series.mean():.4g}",
                "Median"  : f"{series.median():.4g}",
                "Std Dev" : f"{series.std():.4g}",
                "Min"     : f"{series.min():.4g}",
                "Max"     : f"{series.max():.4g}",
                "Skewness": f"{series.skew():.4g}",
                "Kurtosis": f"{series.kurt():.4g}",
            }
            for k, v in stats.items():
                lines.append(f"    {k:<12}: {v}")

    # ── Footer ────────────────────────────────────────────────────────────────
    lines.append("")
    lines.append(sep)
    lines.append("  END OF REPORT — Smart Analytics Assistant v1.0.0")
    lines.append(sep)
    lines.append("")

    report_text = "\n".join(lines)
    return report_text.encode("utf-8")
