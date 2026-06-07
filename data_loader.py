"""
modules/data_loader.py
======================
Handles CSV loading, encoding detection, and automatic column-type classification.
"""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd
import streamlit as st


# ─── CSV Loader ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_csv(uploaded_file) -> tuple[pd.DataFrame | None, str | None]:
    """
    Read an uploaded CSV file into a Pandas DataFrame.

    Tries UTF-8 first; falls back to latin-1 if a UnicodeDecodeError occurs.
    Uses caching so the file is not re-parsed on every Streamlit re-run.

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile

    Returns
    -------
    df : pd.DataFrame or None
    error : str or None  – error message if loading failed, else None
    """
    try:
        raw_bytes = uploaded_file.read()

        # Try UTF-8 first (most common)
        try:
            df = pd.read_csv(io.BytesIO(raw_bytes), encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(raw_bytes), encoding="latin-1")

        # Strip leading/trailing whitespace from string column headers
        df.columns = df.columns.str.strip()

        return df, None

    except Exception as exc:  # pragma: no cover
        return None, str(exc)


# ─── Column Type Detector ─────────────────────────────────────────────────────
def detect_column_types(
    df: pd.DataFrame,
    as_dataframe: bool = False,
) -> dict | pd.DataFrame:
    """
    Classify every column in *df* into one of four categories:
    numeric, categorical, datetime, or boolean.

    Parameters
    ----------
    df : pd.DataFrame
    as_dataframe : bool
        If True, return a tidy DataFrame suitable for display; otherwise return
        a dict with keys 'numeric', 'categorical', 'datetime', 'boolean'.

    Returns
    -------
    dict  OR  pd.DataFrame
    """
    numeric: list[str] = []
    categorical: list[str] = []
    datetime_cols: list[str] = []
    boolean: list[str] = []

    for col in df.columns:
        dtype = df[col].dtype

        if pd.api.types.is_bool_dtype(dtype):
            boolean.append(col)

        elif pd.api.types.is_numeric_dtype(dtype):
            # Low-cardinality integers *might* be categorical – flag them but
            # still add to numeric so charts remain available
            numeric.append(col)

        elif pd.api.types.is_datetime64_any_dtype(dtype):
            datetime_cols.append(col)

        else:
            # Attempt to parse as datetime if the column name hints at it
            if _looks_like_datetime(df[col]):
                datetime_cols.append(col)
            else:
                categorical.append(col)

    if not as_dataframe:
        return {
            "numeric": numeric,
            "categorical": categorical,
            "datetime": datetime_cols,
            "boolean": boolean,
        }

    # ── Build display DataFrame ──────────────────────────────────────────────
    rows = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique = df[col].nunique()
        sample = str(df[col].dropna().iloc[0]) if df[col].notna().any() else "N/A"

        if col in numeric:
            category = "🔢 Numeric"
        elif col in categorical:
            category = "🏷️ Categorical"
        elif col in datetime_cols:
            category = "📅 Datetime"
        elif col in boolean:
            category = "☑️ Boolean"
        else:
            category = "❓ Unknown"

        rows.append(
            {
                "Column": col,
                "Pandas Dtype": dtype,
                "Inferred Type": category,
                "Unique Values": unique,
                "Sample Value": sample,
            }
        )

    return pd.DataFrame(rows).set_index("Column")


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _looks_like_datetime(series: pd.Series, sample_size: int = 50) -> bool:
    """
    Heuristically decide if an object Series contains date/time strings.
    Tests a small sample to avoid parsing the whole column.
    """
    sample = series.dropna().head(sample_size).astype(str)
    if sample.empty:
        return False
    try:
        parsed = pd.to_datetime(sample, infer_datetime_format=True, errors="coerce")
        return parsed.notna().mean() > 0.7  # >70 % parseable ⟹ treat as datetime
    except Exception:
        return False
