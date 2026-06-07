"""
Smart Analytics Assistant - Main Application Entry Point
=========================================================
A production-grade Streamlit application for automated CSV analysis,
dynamic visualizations, and AI-like data insights.

Author: Smart Analytics Team
Version: 1.0.0
"""

import streamlit as st
from pathlib import Path

# ─── Page Configuration (must be first Streamlit call) ───────────────────────
st.set_page_config(
    page_title="Smart Analytics Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/smart-analytics-assistant",
        "Report a bug": "https://github.com/your-repo/smart-analytics-assistant/issues",
        "About": "# Smart Analytics Assistant\nAutomatic CSV Analysis & Insights Platform",
    },
)

# ─── Internal Module Imports ──────────────────────────────────────────────────
from modules.ui_components import apply_custom_css, render_header, render_sidebar
from modules.data_loader import load_csv, detect_column_types
from modules.data_analysis import (
    compute_statistics,
    detect_missing_values,
    detect_duplicates,
    compute_correlations,
)
from modules.visualizations import (
    plot_histogram,
    plot_boxplot,
    plot_scatter,
    plot_correlation_heatmap,
    plot_pie_chart,
    plot_line_chart,
    recommend_charts,
)
from modules.insights import generate_insights
from modules.export import download_cleaned_csv, download_summary_report


# ─── Apply Custom Styling ─────────────────────────────────────────────────────
apply_custom_css()


# ─── Sidebar ──────────────────────────────────────────────────────────────────
theme, uploaded_file = render_sidebar()


# ─── Main Application Flow ───────────────────────────────────────────────────
render_header()

if uploaded_file is None:
    # ── Landing / Upload Prompt ──────────────────────────────────────────────
    st.markdown(
        """
        <div class="upload-prompt">
            <div class="upload-icon">📂</div>
            <h2>Upload a CSV File to Begin</h2>
            <p>Drop any CSV dataset into the sidebar uploader and instantly receive
            automated statistical analysis, dynamic visualizations, and AI-powered insights.</p>
            <div class="feature-grid">
                <div class="feature-card">🔍 <strong>Auto Detection</strong><br/>Column types & data shapes</div>
                <div class="feature-card">📈 <strong>6 Chart Types</strong><br/>Histogram, Box, Scatter & more</div>
                <div class="feature-card">🧠 <strong>AI Insights</strong><br/>Correlations, outliers & trends</div>
                <div class="feature-card">⬇️ <strong>Export</strong><br/>Cleaned data & summary reports</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # ── Load & Validate Data ─────────────────────────────────────────────────
    df, load_error = load_csv(uploaded_file)

    if load_error:
        st.error(f"❌ Failed to load file: {load_error}")
        st.stop()

    col_types = detect_column_types(df)

    # ── Success Banner ───────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="success-banner">
            ✅ <strong>{uploaded_file.name}</strong> loaded — 
            <strong>{df.shape[0]:,}</strong> rows × <strong>{df.shape[1]}</strong> columns
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 1 – Dataset Preview
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("🗂️  Dataset Preview", expanded=True):
        preview_rows = st.slider("Rows to preview", 5, min(100, len(df)), 10, key="preview_slider")
        st.dataframe(df.head(preview_rows), use_container_width=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows", f"{df.shape[0]:,}")
        c2.metric("Total Columns", df.shape[1])
        c3.metric("Numeric Cols", len(col_types["numeric"]))
        c4.metric("Categorical Cols", len(col_types["categorical"]))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 2 – Data Type Identification
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("🏷️  Data Type Identification"):
        type_df = detect_column_types(df, as_dataframe=True)
        st.dataframe(type_df, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 3 – Missing Value Analysis
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("🔎  Missing Value Analysis"):
        missing_df = detect_missing_values(df)
        if missing_df["Missing Count"].sum() == 0:
            st.success("✅ No missing values found in this dataset.")
        else:
            st.warning(f"⚠️  {int(missing_df['Missing Count'].sum()):,} missing values detected.")
            st.dataframe(missing_df[missing_df["Missing Count"] > 0], use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 4 – Duplicate Detection
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("🔁  Duplicate Detection"):
        dup_count, dup_df = detect_duplicates(df)
        if dup_count == 0:
            st.success("✅ No duplicate rows found.")
        else:
            st.warning(f"⚠️  {dup_count:,} duplicate rows found.")
            if st.checkbox("Show duplicate rows"):
                st.dataframe(dup_df, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 5 – Statistical Summary
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("📊  Statistical Summary"):
        stats_df = compute_statistics(df)
        st.dataframe(stats_df.style.format(precision=4), use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 6 – Correlation Analysis
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("🔗  Correlation Analysis"):
        if len(col_types["numeric"]) < 2:
            st.info("ℹ️  Need at least 2 numeric columns for correlation analysis.")
        else:
            corr_matrix = compute_correlations(df, col_types["numeric"])
            fig_corr = plot_correlation_heatmap(corr_matrix)
            st.plotly_chart(fig_corr, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 7 – Dynamic Visualizations
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("📈  Dynamic Visualizations", expanded=True):
        st.markdown("### Chart Builder")

        recommended = recommend_charts(col_types)
        if recommended:
            st.info(f"💡 **Recommended charts** for this dataset: {', '.join(recommended)}")

        chart_type = st.selectbox(
            "Select Chart Type",
            ["Histogram", "Box Plot", "Scatter Plot", "Pie Chart", "Line Chart"],
            key="chart_selector",
        )

        # ── Histogram ───────────────────────────────────────────────────────
        if chart_type == "Histogram":
            col = st.selectbox("Select numeric column", col_types["numeric"], key="hist_col")
            bins = st.slider("Number of bins", 5, 100, 30, key="hist_bins")
            if col:
                fig = plot_histogram(df, col, bins)
                st.plotly_chart(fig, use_container_width=True)

        # ── Box Plot ────────────────────────────────────────────────────────
        elif chart_type == "Box Plot":
            num_col = st.selectbox("Numeric column", col_types["numeric"], key="box_num")
            cat_col = st.selectbox(
                "Group by (optional)",
                ["None"] + col_types["categorical"],
                key="box_cat",
            )
            group = None if cat_col == "None" else cat_col
            if num_col:
                fig = plot_boxplot(df, num_col, group)
                st.plotly_chart(fig, use_container_width=True)

        # ── Scatter Plot ─────────────────────────────────────────────────────
        elif chart_type == "Scatter Plot":
            if len(col_types["numeric"]) < 2:
                st.warning("Need at least 2 numeric columns.")
            else:
                x_col = st.selectbox("X-axis", col_types["numeric"], key="scatter_x")
                y_col = st.selectbox(
                    "Y-axis",
                    [c for c in col_types["numeric"] if c != x_col],
                    key="scatter_y",
                )
                color_col = st.selectbox(
                    "Color by (optional)",
                    ["None"] + col_types["categorical"],
                    key="scatter_color",
                )
                color = None if color_col == "None" else color_col
                fig = plot_scatter(df, x_col, y_col, color)
                st.plotly_chart(fig, use_container_width=True)

        # ── Pie Chart ────────────────────────────────────────────────────────
        elif chart_type == "Pie Chart":
            if not col_types["categorical"]:
                st.warning("No categorical columns found for Pie Chart.")
            else:
                cat_col = st.selectbox("Category column", col_types["categorical"], key="pie_col")
                top_n = st.slider("Show top N categories", 3, 20, 10, key="pie_n")
                fig = plot_pie_chart(df, cat_col, top_n)
                st.plotly_chart(fig, use_container_width=True)

        # ── Line Chart ───────────────────────────────────────────────────────
        elif chart_type == "Line Chart":
            x_col = st.selectbox(
                "X-axis (index or column)",
                ["Index"] + list(df.columns),
                key="line_x",
            )
            y_cols = st.multiselect(
                "Y-axis columns (numeric)",
                col_types["numeric"],
                default=col_types["numeric"][:2],
                key="line_y",
            )
            if y_cols:
                x = None if x_col == "Index" else x_col
                fig = plot_line_chart(df, x, y_cols)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select at least one Y-axis column.")

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 8 – AI-Like Insights
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("🧠  AI-Like Insights", expanded=True):
        insights = generate_insights(df, col_types)
        for insight in insights:
            icon = insight.get("icon", "💡")
            level = insight.get("level", "info")
            msg = insight.get("message", "")
            if level == "warning":
                st.warning(f"{icon} {msg}")
            elif level == "success":
                st.success(f"{icon} {msg}")
            elif level == "error":
                st.error(f"{icon} {msg}")
            else:
                st.info(f"{icon} {msg}")

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 9 – Export
    # ════════════════════════════════════════════════════════════════════════
    with st.expander("⬇️  Export & Download"):
        st.markdown("### Download Cleaned Dataset")
        st.markdown(
            "The cleaned dataset removes duplicate rows and rows with all-null values."
        )
        cleaned_csv = download_cleaned_csv(df)
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=cleaned_csv,
            file_name=f"cleaned_{uploaded_file.name}",
            mime="text/csv",
        )

        st.markdown("---")
        st.markdown("### Download Summary Report")
        report_bytes = download_summary_report(df, col_types, uploaded_file.name)
        st.download_button(
            label="⬇️ Download Summary Report (.txt)",
            data=report_bytes,
            file_name=f"report_{Path(uploaded_file.name).stem}.txt",
            mime="text/plain",
        )
