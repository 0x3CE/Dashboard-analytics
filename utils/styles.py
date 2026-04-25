"""
Design system — Terminal Terminal style.
Noir pur, orange signature, police monospace, layout dense.
Importer apply_custom_css() dans chaque page après set_page_config().
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Palette Terminal
# ---------------------------------------------------------------------------

COLORS = {
    "bg":           "#000000",
    "surface":      "#0D0D0D",
    "card":         "#111111",
    "border":       "#2A2A2A",
    "border_accent":"#FF6600",
    "text":         "#F0F0F0",
    "text_muted":   "#999999",
    "text_dim":     "#555555",
    "primary":      "#FF6600",   # Terminal orange
    "primary_dark": "#CC5200",
    "success":      "#00CC44",
    "warning":      "#FFAA00",
    "danger":       "#FF3333",
    "blue":         "#00A8E0",   # Terminal info blue
    "purple":       "#BB86FC",
    "cyan":         "#00BCD4",
}

CHART_COLORS = {
    "primary":  "#FF6600",
    "success":  "#00CC44",
    "warning":  "#FFAA00",
    "danger":   "#FF3333",
    "blue":     "#00A8E0",
    "purple":   "#BB86FC",
    "cyan":     "#00BCD4",
    "muted":    "#555555",
    "scale_categorical": [
        "#FF6600", "#00A8E0", "#00CC44",
        "#FFAA00", "#BB86FC", "#FF3333",
        "#00BCD4", "#FF9944", "#66DD88",
    ],
}

GAUGE_STEPS = [
    {"range": [0, 35],   "color": "#1A0800"},
    {"range": [35, 65],  "color": "#1A1000"},
    {"range": [65, 100], "color": "#001A08"},
]

PLOTLY_DARK_LAYOUT = {
    "paper_bgcolor": "#111111",
    "plot_bgcolor":  "#0D0D0D",
    "font": {
        "family": "'IBM Plex Mono', 'Consolas', 'Courier New', monospace",
        "color":  "#999999",
        "size":   11,
    },
    "xaxis": {
        "gridcolor":     "#1A1A1A",
        "linecolor":     "#2A2A2A",
        "zerolinecolor": "#2A2A2A",
        "tickfont":      {"color": "#555555", "size": 10},
        "title":         {"font": {"color": "#777777", "size": 11}},
    },
    "yaxis": {
        "gridcolor":     "#1A1A1A",
        "linecolor":     "#2A2A2A",
        "zerolinecolor": "#2A2A2A",
        "tickfont":      {"color": "#555555", "size": 10},
        "title":         {"font": {"color": "#777777", "size": 11}},
    },
    "legend": {
        "bgcolor":     "rgba(0,0,0,0.8)",
        "bordercolor": "#2A2A2A",
        "borderwidth": 1,
        "font":        {"color": "#999999", "size": 10},
    },
    "hoverlabel": {
        "bgcolor":     "#0D0D0D",
        "bordercolor": "#FF6600",
        "font":        {"color": "#F0F0F0",
                        "family": "'IBM Plex Mono', 'Consolas', monospace",
                        "size": 11},
    },
    "margin": {"t": 45, "b": 35, "l": 50, "r": 20},
    "colorway": [
        "#FF6600", "#00A8E0", "#00CC44",
        "#FFAA00", "#BB86FC", "#FF3333",
    ],
}


def bloomberg_layout(title: str = "", **kwargs) -> dict:
    """Return PLOTLY_DARK_LAYOUT merged with a Terminal-styled title and any overrides."""
    title_dict = {
        "text": title.upper() if title else "",
        "font": {
            "family": "'IBM Plex Mono', 'Consolas', monospace",
            "color":  "#999999",
            "size":   11,
        },
        "x": 0.0,
        "xanchor": "left",
    }
    return {**PLOTLY_DARK_LAYOUT, "title": title_dict, **kwargs}


# ---------------------------------------------------------------------------
# CSS Terminal Terminal
# ---------------------------------------------------------------------------

_CSS = """
<style>
/* ── Fonts — IBM Plex Mono (Google Fonts) ── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* ── Global reset ── */
*, *::before, *::after {
    font-family: 'IBM Plex Mono', 'Consolas', 'Courier New', monospace !important;
}

/* ── App background ── */
.stApp {
    background-color: #000000;
}
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1600px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0D0D0D !important;
    border-right: 1px solid #FF6600 !important;
}
[data-testid="stSidebar"] * {
    color: #999999 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stSubheader {
    color: #FF6600 !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] caption {
    color: #444444 !important;
    font-size: 10px !important;
}
[data-testid="stSidebarNavLink"] {
    border-radius: 0 !important;
    border-left: 2px solid transparent;
    margin: 1px 0 !important;
    padding: 0.3rem 0.75rem !important;
    transition: all 0.1s;
}
[data-testid="stSidebarNavLink"]:hover {
    background-color: #1A0800 !important;
    border-left-color: #FF6600 !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background-color: #1A0800 !important;
    border-left: 2px solid #FF6600 !important;
}

/* ── Headings ── */
h1 {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #F0F0F0 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border-bottom: 1px solid #FF6600 !important;
    padding-bottom: 0.4rem !important;
    margin-bottom: 1rem !important;
}
h2 {
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #FF6600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
h3 {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #CCCCCC !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
p, li { color: #AAAAAA; font-size: 12px; line-height: 1.6; }

/* ── Dividers ── */
hr {
    border: none !important;
    border-top: 1px solid #1E1E1E !important;
    margin: 1rem 0 !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background-color: #111111;
    border: 1px solid #2A2A2A;
    border-top: 2px solid #FF6600;
    border-radius: 0 !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.1s;
}
[data-testid="stMetric"]:hover {
    border-color: #FF6600;
    background-color: #1A0800;
}
[data-testid="stMetricLabel"] > div {
    color: #555555 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] > div {
    color: #F0F0F0 !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em;
}
[data-testid="stMetricDelta"] {
    font-size: 11px !important;
    font-weight: 500 !important;
}
[data-testid="stMetricDeltaIcon--up"] svg { fill: #00CC44 !important; }
[data-testid="stMetricDeltaIcon--down"] svg { fill: #FF3333 !important; }

/* ── Buttons ── */
.stButton > button {
    background-color: #000000 !important;
    color: #999999 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 0 !important;
    font-weight: 500 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.1s ease !important;
}
.stButton > button:hover {
    background-color: #1A0800 !important;
    border-color: #FF6600 !important;
    color: #FF6600 !important;
}
.stButton > button[kind="primary"] {
    background-color: #FF6600 !important;
    border-color: #FF6600 !important;
    color: #000000 !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #CC5200 !important;
    border-color: #CC5200 !important;
    box-shadow: 0 0 12px rgba(255,102,0,0.4);
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #2A2A2A;
    gap: 0;
    background: #0D0D0D;
}
[data-testid="stTabs"] [role="tab"] {
    color: #444444 !important;
    font-weight: 600 !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    padding: 0.5rem 1rem !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    background: transparent !important;
    transition: all 0.1s;
}
[data-testid="stTabs"] [role="tab"]:hover {
    color: #FF6600 !important;
    background: rgba(255,102,0,0.05) !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #FF6600 !important;
    border-bottom-color: #FF6600 !important;
    background: rgba(255,102,0,0.05) !important;
}

/* ── Bordered containers ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #111111 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 0 !important;
    padding: 1rem !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background-color: #111111 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 0 !important;
}
[data-testid="stExpander"] summary {
    color: #666666 !important;
    font-weight: 600 !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stExpander"] summary:hover {
    color: #FF6600 !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    border: 1px solid #2A2A2A;
    border-radius: 0;
    overflow: hidden;
}
[data-testid="stDataFrame"] thead tr th {
    background-color: #0D0D0D !important;
    color: #FF6600 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    border-bottom: 1px solid #FF6600 !important;
    padding: 8px 10px !important;
}
[data-testid="stDataFrame"] tbody tr {
    border-bottom: 1px solid #1A1A1A !important;
}
[data-testid="stDataFrame"] tbody tr td {
    font-size: 11px !important;
    color: #CCCCCC !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: #1A0800 !important;
    color: #F0F0F0 !important;
}

/* ── Alert boxes ── */
[data-testid="stAlert"] {
    border-radius: 0 !important;
    border: none !important;
    font-size: 11px !important;
}
[data-testid="stInfo"] {
    background-color: rgba(0,168,224,0.07) !important;
    border-left: 3px solid #00A8E0 !important;
    color: #AAAAAA !important;
}
[data-testid="stWarning"] {
    background-color: rgba(255,170,0,0.07) !important;
    border-left: 3px solid #FFAA00 !important;
}
[data-testid="stSuccess"] {
    background-color: rgba(0,204,68,0.07) !important;
    border-left: 3px solid #00CC44 !important;
}
[data-testid="stException"], [data-testid="stError"] {
    background-color: rgba(255,51,51,0.07) !important;
    border-left: 3px solid #FF3333 !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #111111 !important;
    color: #F0F0F0 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 0 !important;
    font-size: 12px !important;
    caret-color: #FF6600;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #FF6600 !important;
    box-shadow: 0 0 0 1px rgba(255,102,0,0.3) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label {
    color: #555555 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── Selectbox / Multiselect ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background-color: #111111 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 0 !important;
    color: #F0F0F0 !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: rgba(255,102,0,0.2) !important;
    color: #FF9944 !important;
    border-radius: 0 !important;
    font-size: 10px !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div {
    background-color: #1A1A1A !important;
    border-radius: 0 !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #FF6600, #FFAA00) !important;
    border-radius: 0 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] > div {
    border-top-color: #FF6600 !important;
}

/* ── Caption ── */
.stCaption, small {
    color: #444444 !important;
    font-size: 10px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #000000; }
::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 0; }
::-webkit-scrollbar-thumb:hover { background: #FF6600; }

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 0;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: 1px solid;
}
.badge-orange { background: rgba(255,102,0,0.12); color: #FF9944; border-color: rgba(255,102,0,0.4); }
.badge-blue   { background: rgba(0,168,224,0.10); color: #44CCEE; border-color: rgba(0,168,224,0.3); }
.badge-green  { background: rgba(0,204,68,0.10);  color: #44EE77; border-color: rgba(0,204,68,0.3); }
.badge-yellow { background: rgba(255,170,0,0.10); color: #FFCC44; border-color: rgba(255,170,0,0.3); }
.badge-red    { background: rgba(255,51,51,0.10);  color: #FF6666; border-color: rgba(255,51,51,0.3); }
.badge-gray   { background: rgba(80,80,80,0.15);   color: #888888; border-color: rgba(80,80,80,0.3); }

/* ── KPI card ── */
.kpi-card {
    background: #111111;
    border: 1px solid #2A2A2A;
    border-top: 2px solid #FF6600;
    border-radius: 0;
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
}
.kpi-card:hover { border-color: #FF6600; background: #1A0800; }
.kpi-card .kpi-label {
    color: #555555;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}
.kpi-card .kpi-value {
    color: #F0F0F0;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    line-height: 1;
}
.kpi-card .kpi-delta { font-size: 11px; font-weight: 500; margin-top: 4px; }
.kpi-card .kpi-delta.up     { color: #00CC44; }
.kpi-card .kpi-delta.down   { color: #FF3333; }
.kpi-card .kpi-delta.neutral { color: #555555; }

/* ── Section label ── */
.section-label {
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #FF6600;
    margin-bottom: 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1E1E1E;
}

/* ── Terminal header bar ── */
.term-bar {
    background: #FF6600;
    color: #000000;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 4px 12px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.term-bar .dot {
    width: 6px; height: 6px;
    background: #000000;
    border-radius: 50%;
    display: inline-block;
}

/* ── Blockquote (verdict) ── */
blockquote {
    border-left: 3px solid #FF6600 !important;
    background: rgba(255,102,0,0.05) !important;
    padding: 0.6rem 1rem !important;
    border-radius: 0 !important;
    color: #AAAAAA !important;
    font-style: normal !important;
    margin: 0.5rem 0 !important;
    font-size: 12px !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background-color: transparent !important;
    border: 1px solid #2A2A2A !important;
    color: #666666 !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    border-radius: 0 !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: #00CC44 !important;
    color: #00CC44 !important;
}

/* ── Hide Streamlit chrome + sidebar nav links ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
[data-testid="stSidebarNavItems"]     { display: none !important; }
[data-testid="stSidebarNavSeparator"] { display: none !important; }
[data-testid="stSidebarNavLink"]      { display: none !important; }

/* ── Ticker tape ── */
.ticker-tape {
    background: #0D0D0D;
    border-bottom: 1px solid #FF6600;
    overflow: hidden;
    height: 26px;
    display: flex;
    align-items: center;
    margin: -1rem -1rem 1rem -1rem;
    padding: 0;
}
.tape-track {
    display: inline-flex;
    align-items: center;
    white-space: nowrap;
    animation: tape-scroll 55s linear infinite;
    will-change: transform;
}
.tape-track:hover { animation-play-state: paused; }
@keyframes tape-scroll {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
.tape-item {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 0 14px;
}
.tape-lbl {
    color: #FF6600;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.tape-px {
    color: #F0F0F0;
    font-size: 11px;
    font-weight: 600;
}
.tape-chg {
    font-size: 10px;
    font-weight: 500;
}
.tape-dot {
    color: #2A2A2A;
    font-size: 16px;
    line-height: 1;
}

/* ── Top navigation bar ── */
.topnav {
    display: flex;
    align-items: center;
    background: #111111;
    border-bottom: 1px solid #2A2A2A;
    padding: 0 0 0 0;
    margin: 0 -1rem 1.25rem -1rem;
    height: 38px;
    gap: 0;
}
.topnav-brand {
    background: #FF6600;
    height: 100%;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 18px;
    flex-shrink: 0;
}
.brand-tag {
    color: #000;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}
.brand-sub {
    color: rgba(0,0,0,0.55);
    font-size: 8px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.nav-links {
    display: flex;
    align-items: center;
    height: 100%;
    margin-left: 4px;
}
.nav-item {
    display: inline-flex;
    align-items: center;
    height: 100%;
    padding: 0 16px;
    color: #555555 !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    text-decoration: none !important;
    border-bottom: 2px solid transparent;
    transition: all 0.1s;
}
.nav-item:hover {
    color: #FF6600 !important;
    background: rgba(255,102,0,0.06);
    border-bottom-color: #FF6600;
}
.nav-active {
    color: #FF6600 !important;
    border-bottom: 2px solid #FF6600 !important;
    background: rgba(255,102,0,0.05);
}
.topnav-right {
    margin-left: auto;
    padding-right: 16px;
}
.data-tag {
    color: #2A2A2A;
    font-size: 8px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Number input arrows ── */
[data-testid="stNumberInput"] button {
    border-radius: 0 !important;
    border-color: #2A2A2A !important;
    background: #111111 !important;
    color: #FF6600 !important;
}
</style>
"""


def apply_custom_css():
    """Injecter le design system Terminal Terminal dans la page courante."""
    st.markdown(_CSS, unsafe_allow_html=True)
