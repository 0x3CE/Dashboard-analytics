"""
Top bar : ticker tape + navigation horizontale.
render_ticker_tape() — données marchés défilantes (cache 5 min)
render_topnav(current) — barre de navigation en haut de chaque page
"""

import streamlit as st
import yfinance as yf

# ---------------------------------------------------------------------------
# Instruments du ticker tape
# ---------------------------------------------------------------------------
_TAPE = [
    ("S&P 500",   "^GSPC"),
    ("NASDAQ",    "^IXIC"),
    ("DOW",       "^DJI"),
    ("CAC 40",    "^FCHI"),
    ("DAX",       "^GDAXI"),
    ("FTSE 100",  "^FTSE"),
    ("EUR/USD",   "EURUSD=X"),
    ("GBP/USD",   "GBPUSD=X"),
    ("USD/JPY",   "USDJPY=X"),
    ("GOLD",      "GC=F"),
    ("CRUDE",     "CL=F"),
    ("BTC",       "BTC-USD"),
]

# ---------------------------------------------------------------------------
# Pages — URLs Streamlit (dérivées des noms de fichiers)
# ---------------------------------------------------------------------------
_PAGES = [
    ("HOME",      "/",                        "home"),
    ("SCREENER",  "/Screener",                "screener"),
    ("ANALYSE",   "/Analyse_Entreprise",      "analyse"),
    ("CONSENSUS", "/Consensus_Analystes",     "consensus"),
    ("RANKING",   "/Score_Composite",         "score"),
]


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_tape() -> list[dict]:
    """Récupère prix + variation pour chaque instrument. Cache 5 min."""
    results = []
    for label, symbol in _TAPE:
        try:
            fi = yf.Ticker(symbol).fast_info
            price = fi.last_price
            prev  = fi.previous_close
            if price is None or prev is None or prev == 0:
                continue
            change = price - prev
            pct    = change / prev * 100
            results.append({"label": label, "price": price,
                             "change": change, "pct": pct})
        except Exception:
            pass
    return results


def _fmt_price(price: float) -> str:
    if price >= 10_000:
        return f"{price:,.0f}"
    if price >= 100:
        return f"{price:,.2f}"
    return f"{price:.4f}"


def render_ticker_tape() -> None:
    """Injecte la barre de ticker défilante (HTML pur, CSS animation)."""
    data = _fetch_tape()
    if not data:
        return

    items_html = ""
    for d in data:
        color  = "#00CC44" if d["change"] >= 0 else "#FF3333"
        arrow  = "▲" if d["change"] >= 0 else "▼"
        sign   = "+" if d["change"] >= 0 else ""
        price  = _fmt_price(d["price"])
        items_html += f"""
<span class="tape-item">
  <span class="tape-lbl">{d['label']}</span>
  <span class="tape-px">{price}</span>
  <span class="tape-chg" style="color:{color}">{arrow} {sign}{d['pct']:.2f}%</span>
</span>
<span class="tape-dot">·</span>"""

    # Dupliquer pour loop seamless
    track = items_html * 2

    st.markdown(f"""
<div class="ticker-tape">
  <div class="tape-track">{track}</div>
</div>
""", unsafe_allow_html=True)


def render_topnav(current: str = "home") -> None:
    """
    Injecte la barre de navigation horizontale (HTML avec liens <a>).
    current : 'home' | 'screener' | 'analyse' | 'consensus' | 'score'
    """
    nav_items = ""
    for label, href, key in _PAGES:
        active_class = "nav-active" if key == current else ""
        nav_items += (
            f'<a href="{href}" class="nav-item {active_class}" target="_self">'
            f'{label}</a>'
        )

    st.markdown(f"""
<div class="topnav">
  <div class="topnav-brand">
    <span class="brand-tag">TERMINAL</span>
    <span class="brand-sub">EQUITY RESEARCH · US &amp; EUROPE</span>
  </div>
  <nav class="nav-links">{nav_items}</nav>
  <div class="topnav-right">
    <span class="data-tag">YAHOO FINANCE · CACHE 1H</span>
  </div>
</div>
""", unsafe_allow_html=True)
