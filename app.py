"""
Page d'accueil du Dashboard Financier.
Navigation vers les 4 modules + gestion de la watchlist.
"""

import streamlit as st
from utils.styles import apply_custom_css
from utils.topbar import render_ticker_tape, render_topnav
import utils.watchlist as wl

st.set_page_config(
    page_title="Dashboard Financier",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()
render_ticker_tape()
render_topnav("home")

# ---------------------------------------------------------------------------
# Session state initial
# ---------------------------------------------------------------------------
st.session_state.setdefault("selected_ticker", "AAPL")
wl.init_session_state()

# ---------------------------------------------------------------------------
# Sidebar — Watchlist persistante
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<p class="section-label">Watchlist</p>', unsafe_allow_html=True)
    ticker_add = st.text_input(
        "Ticker",
        placeholder="AAPL  OR.PA  SAP.DE",
        key="sidebar_add_ticker",
    ).strip().upper()

    if st.button("+ ADD TO WATCHLIST", use_container_width=True):
        if ticker_add:
            if wl.add(ticker_add):
                st.rerun()
            else:
                st.info("Already in watchlist.")

    if st.session_state["watchlist"]:
        for wt in list(st.session_state["watchlist"]):
            col1, col2 = st.columns([3, 1])
            if col1.button(wt, key=f"home_wl_{wt}", use_container_width=True):
                st.session_state["selected_ticker"] = wt
                st.switch_page("pages/2_Analyse_Entreprise.py")
            if col2.button("X", key=f"home_rm_{wt}"):
                wl.remove(wt)
                st.rerun()
    else:
        st.caption("NO TICKERS LOADED")

# ---------------------------------------------------------------------------
# Contenu principal
# ---------------------------------------------------------------------------
st.markdown("""
<div style="margin-bottom:0.25rem">
  <span style="font-size:1.4rem;font-weight:700;color:#F0F0F0;letter-spacing:0.03em;text-transform:uppercase;">Financial Dashboard</span>
</div>
<div style="color:#555555;font-size:10px;margin-bottom:1.5rem;letter-spacing:0.1em;text-transform:uppercase;">
  Fundamental Analysis · Analyst Consensus · US &amp; Europe
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Navigation rapide — 4 modules
# ---------------------------------------------------------------------------
st.markdown('<p class="section-label">Modules</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("""
        <div style="margin-bottom:0.6rem">
          <span style="color:#FF6600;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">SCREENER</span>
        </div>
        <div style="color:#CCCCCC;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">
          Multi-Ratio Stock Screener
        </div>
        <p style="color:#666666;font-size:11px;line-height:1.6;margin:0 0 0.75rem 0;">
          Filter by PE · Fwd PE · PS · PEG · P/B · EV/EBITDA · Dividend · Sector.
          Parallel scan across 6 universes — CSV export.
        </p>
        """, unsafe_allow_html=True)
        if st.button("OPEN SCREENER", key="nav_screener", type="primary", use_container_width=True):
            st.switch_page("pages/1_Screener.py")

    with st.container(border=True):
        st.markdown("""
        <div style="margin-bottom:0.6rem">
          <span style="color:#FF6600;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">CONSENSUS</span>
        </div>
        <div style="color:#CCCCCC;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">
          Analyst Recommendations
        </div>
        <p style="color:#666666;font-size:11px;line-height:1.6;margin:0 0 0.75rem 0;">
          Strong Buy → Strong Sell breakdown · Price targets (low/mean/high) ·
          Upside potential · Upgrades/downgrades history.
        </p>
        """, unsafe_allow_html=True)
        if st.button("OPEN CONSENSUS", key="nav_consensus", type="primary", use_container_width=True):
            st.switch_page("pages/3_Consensus_Analystes.py")

with col2:
    with st.container(border=True):
        st.markdown("""
        <div style="margin-bottom:0.6rem">
          <span style="color:#FF6600;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">DEEP DIVE</span>
        </div>
        <div style="color:#CCCCCC;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">
          Company Analysis
        </div>
        <p style="color:#666666;font-size:11px;line-height:1.6;margin:0 0 0.75rem 0;">
          Sector-relative valuation · DCF 3 scenarios · Financial health ·
          4-year financials · Contextual analysis · Growth regime.
        </p>
        """, unsafe_allow_html=True)
        if st.button("OPEN ANALYSIS", key="nav_analyse", type="primary", use_container_width=True):
            st.switch_page("pages/2_Analyse_Entreprise.py")

    with st.container(border=True):
        st.markdown("""
        <div style="margin-bottom:0.6rem">
          <span style="color:#FF6600;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">RANKING</span>
        </div>
        <div style="color:#CCCCCC;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">
          Composite Score
        </div>
        <p style="color:#666666;font-size:11px;line-height:1.6;margin:0 0 0.75rem 0;">
          Rank a universe on 100-pt composite score (valuation · DCF · growth ·
          analysts · quality). Divergence detection : forgotten opportunities, value traps.
        </p>
        """, unsafe_allow_html=True)
        if st.button("OPEN RANKING", key="nav_score", type="primary", use_container_width=True):
            st.switch_page("pages/4_Score_Composite.py")

st.divider()

# ---------------------------------------------------------------------------
# Accès rapide ticker
# ---------------------------------------------------------------------------
st.markdown('<p class="section-label">Quick Lookup</p>', unsafe_allow_html=True)
col_t, col_b1, col_b2 = st.columns([3, 1, 1])
quick_ticker = col_t.text_input(
    "Ticker",
    value=st.session_state["selected_ticker"],
    label_visibility="collapsed",
    placeholder="AAPL   OR.PA   SAP.DE   HSBA.L",
).strip().upper()

if quick_ticker:
    st.session_state["selected_ticker"] = quick_ticker

if col_b1.button("ANALYZE", use_container_width=True, type="primary"):
    st.switch_page("pages/2_Analyse_Entreprise.py")
if col_b2.button("CONSENSUS", use_container_width=True):
    st.switch_page("pages/3_Consensus_Analystes.py")

st.divider()

# ---------------------------------------------------------------------------
# Info marchés couverts
# ---------------------------------------------------------------------------
with st.expander("MARKET COVERAGE — TICKER CONVENTIONS"):
    st.markdown("""
    | MARKET | SUFFIX | EXAMPLE |
    |--------|--------|---------|
    | US NYSE / Nasdaq | *(none)* | `AAPL` |
    | Paris Euronext | `.PA` | `OR.PA` |
    | Frankfurt Xetra | `.DE` | `SAP.DE` |
    | London LSE | `.L` | `HSBA.L` |
    | Amsterdam | `.AS` | `ASML.AS` |
    | Milan | `.MI` | `ENEL.MI` |
    | Madrid | `.MC` | `IBE.MC` |
    | Copenhagen | `.CO` | `NOVO-B.CO` |

    Data source: **Yahoo Finance** via yfinance · Cache TTL: **1 hour**
    """)

# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------
st.divider()
st.caption("""
DISCLAIMER: This terminal is a research tool only. It does not constitute investment advice.
Data sourced from Yahoo Finance (free tier, no SLA). Valuation ratios are most meaningful
in relative context (vs peers, vs sector medians). User is solely responsible for investment decisions.
""")
