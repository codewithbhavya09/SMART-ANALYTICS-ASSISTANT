"""
modules/ui_components.py
========================
All UI-related helpers: custom CSS injection, page header, and sidebar rendering.
Supports both Light and Dark mode via Streamlit's theme system plus manual overrides.
"""

import streamlit as st


# ─── Custom CSS ───────────────────────────────────────────────────────────────
def apply_custom_css() -> None:
    """
    Inject custom CSS for a modern analytics platform aesthetic.
    Uses CSS variables so both light and dark modes remain coherent.
    """
    st.markdown(
        """
        <style>
        /* ── Google Fonts ─────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── Root variables ────────────────────────────────────────────── */
        :root {
            --accent:       #6366f1;
            --accent-light: #818cf8;
            --accent-dark:  #4f46e5;
            --success:      #10b981;
            --warning:      #f59e0b;
            --danger:       #ef4444;
            --radius:       12px;
            --shadow:       0 4px 24px rgba(0,0,0,0.08);
        }

        /* ── Global typography ─────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Space Grotesk', sans-serif !important;
        }

        /* ── Streamlit main block padding ──────────────────────────────── */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
        }

        /* ── App Header ────────────────────────────────────────────────── */
        .app-header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
            border-radius: var(--radius);
            padding: 2rem 2.5rem;
            margin-bottom: 2rem;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .app-header::before {
            content: '';
            position: absolute;
            top: -60%;
            right: -10%;
            width: 400px;
            height: 400px;
            background: rgba(255,255,255,0.06);
            border-radius: 50%;
        }
        .app-header h1 {
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0 0 0.3rem 0;
            letter-spacing: -0.5px;
        }
        .app-header p {
            font-size: 1rem;
            opacity: 0.88;
            margin: 0;
        }
        .app-header .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 20px;
            padding: 3px 12px;
            font-size: 0.78rem;
            font-weight: 500;
            margin-top: 0.7rem;
        }

        /* ── Upload prompt ─────────────────────────────────────────────── */
        .upload-prompt {
            text-align: center;
            padding: 4rem 2rem;
            border: 2px dashed rgba(99,102,241,0.35);
            border-radius: var(--radius);
            margin-top: 1rem;
            background: rgba(99,102,241,0.03);
        }
        .upload-prompt .upload-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .upload-prompt h2 {
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .upload-prompt p {
            opacity: 0.7;
            max-width: 480px;
            margin: 0 auto 2rem;
            line-height: 1.6;
        }

        /* ── Feature grid ──────────────────────────────────────────────── */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 1rem;
            max-width: 700px;
            margin: 0 auto;
        }
        .feature-card {
            background: rgba(99,102,241,0.07);
            border: 1px solid rgba(99,102,241,0.2);
            border-radius: var(--radius);
            padding: 1rem;
            font-size: 0.88rem;
            line-height: 1.5;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(99,102,241,0.15);
        }

        /* ── Success banner ────────────────────────────────────────────── */
        .success-banner {
            background: linear-gradient(90deg, rgba(16,185,129,0.12), rgba(16,185,129,0.04));
            border-left: 4px solid var(--success);
            border-radius: 0 var(--radius) var(--radius) 0;
            padding: 0.85rem 1.25rem;
            margin-bottom: 1.5rem;
            font-size: 0.95rem;
        }

        /* ── Expander styling ──────────────────────────────────────────── */
        .streamlit-expanderHeader {
            font-size: 1rem !important;
            font-weight: 600 !important;
            border-radius: var(--radius) !important;
        }
        .streamlit-expanderContent {
            border-radius: 0 0 var(--radius) var(--radius) !important;
        }

        /* ── Metric cards ──────────────────────────────────────────────── */
        [data-testid="metric-container"] {
            background: rgba(99,102,241,0.06);
            border: 1px solid rgba(99,102,241,0.15);
            border-radius: var(--radius);
            padding: 1rem !important;
        }
        [data-testid="metric-container"] label {
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ── Download buttons ──────────────────────────────────────────── */
        .stDownloadButton > button {
            background: linear-gradient(135deg, var(--accent), var(--accent-dark)) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.4rem !important;
            transition: opacity 0.2s, transform 0.2s !important;
        }
        .stDownloadButton > button:hover {
            opacity: 0.9 !important;
            transform: translateY(-1px) !important;
        }

        /* ── Selectbox & Slider labels ─────────────────────────────────── */
        .stSelectbox label, .stSlider label, .stMultiSelect label {
            font-weight: 500 !important;
            font-size: 0.88rem !important;
        }

        /* ── Sidebar ───────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(99,102,241,0.15);
        }
        .sidebar-brand {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .sidebar-section {
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.5;
            margin: 1.5rem 0 0.5rem;
        }

        /* ── Code / mono font ──────────────────────────────────────────── */
        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* ── Dataframe ─────────────────────────────────────────────────── */
        .stDataFrame {
            border-radius: var(--radius) !important;
            overflow: hidden !important;
        }

        /* ── Plotly chart container ─────────────────────────────────────── */
        .js-plotly-plot {
            border-radius: var(--radius);
        }

        /* ── Info / Warning / Success boxes ────────────────────────────── */
        .stAlert {
            border-radius: var(--radius) !important;
            border-left-width: 4px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─── Page Header ─────────────────────────────────────────────────────────────
def render_header() -> None:
    """Render the top hero header banner."""
    st.markdown(
        """
        <div class="app-header">
            <h1>📊 Smart Analytics Assistant</h1>
            <p>Upload any CSV — get instant statistics, visualizations & AI-like insights.</p>
            <span class="badge">⚡ Powered by Pandas · Plotly · NumPy</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Sidebar ─────────────────────────────────────────────────────────────────
def render_sidebar():
    """
    Render the sidebar with branding, file uploader, and theme toggle.

    Returns
    -------
    theme : str
        'Light' or 'Dark'
    uploaded_file : UploadedFile | None
        The file uploaded by the user, or None.
    """
    with st.sidebar:
        # Brand
        st.markdown(
            '<div class="sidebar-brand">📊 Smart Analytics</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Upload section
        st.markdown('<div class="sidebar-section">📁 Data Source</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=["csv"],
            help="Drag and drop or browse for a CSV file to analyze.",
        )

        # Theme
        st.markdown('<div class="sidebar-section">🎨 Appearance</div>', unsafe_allow_html=True)
        theme = st.radio(
            "Color Theme",
            ["Light", "Dark"],
            horizontal=True,
            help="Switch between light and dark chart themes.",
        )

        # Info
        st.markdown("---")
        st.markdown(
            """
            <div style="font-size:0.78rem; opacity:0.6; line-height:1.6;">
            <strong>Smart Analytics Assistant</strong><br/>
            v1.0.0 · MIT License<br/><br/>
            Supports CSV files up to 200 MB.<br/>
            All processing is done locally.
            </div>
            """,
            unsafe_allow_html=True,
        )

    return theme, uploaded_file
