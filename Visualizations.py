"""
modules/visualizations.py
==========================
All Plotly-based chart generators and an automatic chart recommender.

Chart types:
  1. Histogram
  2. Box Plot
  3. Scatter Plot
  4. Correlation Heatmap
  5. Pie Chart
  6. Line Chart
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─── Shared chart config ──────────────────────────────────────────────────────
_TEMPLATE_LIGHT = "plotly_white"
_TEMPLATE_DARK = "plotly_dark"
_FONT_FAMILY = "Space Grotesk, sans-serif"
_ACCENT_SEQ = px.colors.sequential.Plasma
_QUALITATIVE_SEQ = px.colors.qualitative.Vivid


def _get_template() -> str:
    """Return Plotly template based on the sidebar theme selection."""
    # Read from session state set by sidebar; default to light
    return _TEMPLATE_DARK if st.session_state.get("theme") == "Dark" else _TEMPLATE_LIGHT


def _base_layout(fig: go.Figure, title: str) -> go.Figure:
    """Apply consistent layout settings to any figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(family=_FONT_FAMILY, size=16, weight="bold")),
        font=dict(family=_FONT_FAMILY),
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor="rgba(150,150,150,0.3)",
            borderwidth=1,
        ),
    )
    return fig


# ─── 1. Histogram ─────────────────────────────────────────────────────────────
def plot_histogram(df: pd.DataFrame, col: str, bins: int = 30) -> go.Figure:
    """
    Generate an interactive histogram for a single numeric column.

    Parameters
    ----------
    df   : pd.DataFrame
    col  : str   – numeric column name
    bins : int   – number of histogram bins

    Returns
    -------
    plotly.graph_objects.Figure
    """
    fig = px.histogram(
        df,
        x=col,
        nbins=bins,
        template=_get_template(),
        color_discrete_sequence=[_QUALITATIVE_SEQ[0]],
        opacity=0.85,
        marginal="box",  # add a box plot on the margin
        title=f"Distribution of {col}",
    )
    fig.update_traces(marker_line_width=0.8, marker_line_color="white")
    return _base_layout(fig, f"Distribution of <b>{col}</b>")


# ─── 2. Box Plot ──────────────────────────────────────────────────────────────
def plot_boxplot(
    df: pd.DataFrame,
    num_col: str,
    group_col: str | None = None,
) -> go.Figure:
    """
    Generate an interactive box plot, optionally grouped by a categorical column.

    Parameters
    ----------
    df        : pd.DataFrame
    num_col   : str   – numeric column for the Y-axis
    group_col : str | None – categorical column to group/color by

    Returns
    -------
    plotly.graph_objects.Figure
    """
    title = f"Box Plot of {num_col}"
    if group_col:
        title += f" by {group_col}"

    fig = px.box(
        df,
        y=num_col,
        x=group_col,
        color=group_col,
        template=_get_template(),
        color_discrete_sequence=_QUALITATIVE_SEQ,
        points="outliers",
        notched=True,
        title=title,
    )
    return _base_layout(fig, title)


# ─── 3. Scatter Plot ──────────────────────────────────────────────────────────
def plot_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str | None = None,
) -> go.Figure:
    """
    Generate an interactive scatter plot with optional OLS trendline.

    Parameters
    ----------
    df        : pd.DataFrame
    x_col     : str
    y_col     : str
    color_col : str | None

    Returns
    -------
    plotly.graph_objects.Figure
    """
    title = f"{y_col} vs {x_col}"
    kwargs = dict(
        x=x_col,
        y=y_col,
        template=_get_template(),
        opacity=0.75,
        color_discrete_sequence=_QUALITATIVE_SEQ,
        trendline="ols",  # Ordinary Least Squares trend line
        title=title,
    )
    if color_col:
        kwargs["color"] = color_col

    try:
        fig = px.scatter(df, **kwargs)
    except Exception:
        # Fallback without trendline (e.g. missing statsmodels)
        kwargs.pop("trendline", None)
        fig = px.scatter(df, **kwargs)

    fig.update_traces(marker=dict(size=6, line=dict(width=0.5, color="white")))
    return _base_layout(fig, title)


# ─── 4. Correlation Heatmap ───────────────────────────────────────────────────
def plot_correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """
    Render a Plotly heatmap of a square correlation matrix.

    Parameters
    ----------
    corr_matrix : pd.DataFrame – output of compute_correlations()

    Returns
    -------
    plotly.graph_objects.Figure
    """
    labels = corr_matrix.columns.tolist()
    z = corr_matrix.values
    text = np.round(z, 2).astype(str)

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=labels,
            y=labels,
            text=text,
            texttemplate="%{text}",
            colorscale="RdBu_r",
            zmid=0,
            zmin=-1,
            zmax=1,
            colorbar=dict(title="r", tickformat=".1f"),
        )
    )
    fig.update_layout(
        template=_get_template(),
        xaxis=dict(tickangle=-35),
        height=max(350, 60 * len(labels)),
    )
    return _base_layout(fig, "Correlation Heatmap")


# ─── 5. Pie Chart ─────────────────────────────────────────────────────────────
def plot_pie_chart(df: pd.DataFrame, col: str, top_n: int = 10) -> go.Figure:
    """
    Generate a donut/pie chart from the value counts of a categorical column.

    Parameters
    ----------
    df    : pd.DataFrame
    col   : str  – categorical column
    top_n : int  – show only the top N categories; others are grouped as 'Other'

    Returns
    -------
    plotly.graph_objects.Figure
    """
    counts = df[col].value_counts()

    if len(counts) > top_n:
        top = counts.head(top_n)
        other_val = counts.iloc[top_n:].sum()
        top["Other"] = other_val
        counts = top

    fig = px.pie(
        names=counts.index,
        values=counts.values,
        template=_get_template(),
        color_discrete_sequence=_QUALITATIVE_SEQ,
        hole=0.42,  # donut style
        title=f"Distribution of {col}",
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        pull=[0.03] * len(counts),
    )
    return _base_layout(fig, f"Distribution of <b>{col}</b>")


# ─── 6. Line Chart ────────────────────────────────────────────────────────────
def plot_line_chart(
    df: pd.DataFrame,
    x_col: str | None,
    y_cols: list[str],
) -> go.Figure:
    """
    Generate a multi-line chart.

    Parameters
    ----------
    df     : pd.DataFrame
    x_col  : str | None  – X-axis column; if None the row index is used
    y_cols : list[str]   – one or more numeric Y-axis columns

    Returns
    -------
    plotly.graph_objects.Figure
    """
    plot_df = df.copy()

    if x_col is None:
        plot_df["__index__"] = range(len(df))
        x_col = "__index__"
        x_label = "Row Index"
    else:
        x_label = x_col

    fig = go.Figure()
    colors = _QUALITATIVE_SEQ

    for i, col in enumerate(y_cols):
        fig.add_trace(
            go.Scatter(
                x=plot_df[x_col],
                y=plot_df[col],
                name=col,
                mode="lines",
                line=dict(color=colors[i % len(colors)], width=2),
            )
        )

    title = f"Line Chart: {', '.join(y_cols)}"
    fig.update_layout(
        xaxis_title=x_label,
        template=_get_template(),
        hovermode="x unified",
    )
    return _base_layout(fig, title)


# ─── Chart Recommender ────────────────────────────────────────────────────────
def recommend_charts(col_types: dict) -> list[str]:
    """
    Recommend chart types based on the detected column types.

    Parameters
    ----------
    col_types : dict  – output of detect_column_types()

    Returns
    -------
    list[str]  – ordered list of recommended chart names
    """
    recommendations: list[str] = []
    n_numeric = len(col_types.get("numeric", []))
    n_cat = len(col_types.get("categorical", []))

    if n_numeric >= 1:
        recommendations.append("Histogram")
        recommendations.append("Box Plot")

    if n_numeric >= 2:
        recommendations.append("Scatter Plot")
        recommendations.append("Correlation Heatmap")
        recommendations.append("Line Chart")

    if n_cat >= 1:
        recommendations.append("Pie Chart")

    return recommendations
