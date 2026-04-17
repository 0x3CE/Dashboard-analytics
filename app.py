"""
Page d'accueil du Dashboard Financier.
Navigation vers les 4 modules + gestion de la watchlist.
"""

import streamlit as st

st.set_page_config(
    page_title="Dashboard Financier",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state initial
# ---------------------------------------------------------------------------
st.session_state.setdefault("selected_ticker", "AAPL")
st.session_state.setdefault("watchlist", [])

# ---------------------------------------------------------------------------
# Sidebar — Watchlist persistante
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📈 Dashboard Financier")
    st.caption("Analyse de valeur & Consensus Analystes")
    st.divider()

    st.subheader("⭐ Watchlist rapide")
    ticker_add = st.text_input(
        "Ajouter un ticker",
        placeholder="ex: AAPL, OR.PA, SAP.DE",
        key="sidebar_add_ticker",
    ).strip().upper()

    if st.button("➕ Ajouter", use_container_width=True):
        if ticker_add and ticker_add not in st.session_state["watchlist"]:
            st.session_state["watchlist"].append(ticker_add)
        elif ticker_add in st.session_state["watchlist"]:
            st.info("Déjà dans la watchlist.")

    if st.session_state["watchlist"]:
        for wt in list(st.session_state["watchlist"]):
            col1, col2 = st.columns([3, 1])
            if col1.button(wt, key=f"home_wl_{wt}", use_container_width=True):
                st.session_state["selected_ticker"] = wt
                st.switch_page("pages/2_Analyse_Entreprise.py")
            if col2.button("✕", key=f"home_rm_{wt}"):
                st.session_state["watchlist"].remove(wt)
                st.rerun()
    else:
        st.caption("Aucun ticker en watchlist.")

# ---------------------------------------------------------------------------
# Contenu principal
# ---------------------------------------------------------------------------
st.title("📈 Dashboard Financier")
st.subheader("Analyse de Valeur & Consensus Analystes")
st.markdown("""
Identifiez des entreprises **potentiellement sous-évaluées** en croisant analyse fondamentale et sentiment de marché.
Couvre les marchés **US** (S&P 500, Nasdaq) et **Europe** (CAC 40, DAX 40, FTSE 100, Euro Stoxx 50).
""")

st.divider()

# ---------------------------------------------------------------------------
# Navigation rapide — 4 modules
# ---------------------------------------------------------------------------
st.subheader("Modules disponibles")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 🔎 Screener Multi-Ratios")
        st.markdown("""
        Filtrez un univers de plusieurs dizaines d'entreprises selon vos critères fondamentaux :
        PE, Forward PE, PS, PEG, P/B, EV/EBITDA, rendement dividende, secteur.

        Scan parallèle avec progress bar — résultats exportables en CSV.
        """)
        if st.button("Ouvrir le Screener →", key="nav_screener", type="primary", use_container_width=True):
            st.switch_page("pages/1_Screener.py")

    with st.container(border=True):
        st.markdown("### 🎯 Consensus Analystes")
        st.markdown("""
        Consultez les recommandations (Strong Buy → Strong Sell), les price targets
        (low / mean / median / high) et l'upside potentiel vs le cours actuel.

        Historique des upgrades/downgrades récents.
        """)
        if st.button("Ouvrir le Consensus →", key="nav_consensus", type="primary", use_container_width=True):
            st.switch_page("pages/3_Consensus_Analystes.py")

with col2:
    with st.container(border=True):
        st.markdown("### 🔍 Analyse Entreprise")
        st.markdown("""
        Deep-dive complet sur une entreprise : ratios de valorisation, santé financière,
        états financiers sur 4 ans, graphiques historiques, dividende.

        Jauge visuelle de valorisation + color-coding des ratios.
        """)
        if st.button("Ouvrir l'Analyse →", key="nav_analyse", type="primary", use_container_width=True):
            st.switch_page("pages/2_Analyse_Entreprise.py")

    with st.container(border=True):
        st.markdown("### 🏆 Score Composite")
        st.markdown("""
        Rankez tout un univers par **score composite** combinant valorisation (50 pts),
        consensus analystes (30 pts) et qualité financière (20 pts).

        Détection automatique des divergences : opportunités oubliées, value traps…
        """)
        if st.button("Ouvrir le Score Composite →", key="nav_score", type="primary", use_container_width=True):
            st.switch_page("pages/4_Score_Composite.py")

st.divider()

# ---------------------------------------------------------------------------
# Accès rapide ticker
# ---------------------------------------------------------------------------
st.subheader("Analyse rapide d'un ticker")
col_t, col_b1, col_b2 = st.columns([3, 1, 1])
quick_ticker = col_t.text_input(
    "Ticker",
    value=st.session_state["selected_ticker"],
    label_visibility="collapsed",
    placeholder="ex: AAPL, OR.PA, SAP.DE, HSBA.L",
).strip().upper()

if quick_ticker:
    st.session_state["selected_ticker"] = quick_ticker

if col_b1.button("🔍 Analyser", use_container_width=True):
    st.switch_page("pages/2_Analyse_Entreprise.py")
if col_b2.button("🎯 Consensus", use_container_width=True):
    st.switch_page("pages/3_Consensus_Analystes.py")

st.divider()

# ---------------------------------------------------------------------------
# Info marchés couverts
# ---------------------------------------------------------------------------
with st.expander("🌍 Marchés et conventions de tickers"):
    st.markdown("""
    | Marché | Suffixe | Exemple |
    |--------|---------|---------|
    | US (NYSE/Nasdaq) | aucun | `AAPL` |
    | Paris (Euronext) | `.PA` | `OR.PA` (L'Oréal) |
    | Francfort (Xetra) | `.DE` | `SAP.DE` |
    | Londres (LSE) | `.L` | `HSBA.L` |
    | Amsterdam | `.AS` | `ASML.AS` |
    | Milan | `.MI` | `ENEL.MI` |
    | Madrid | `.MC` | `IBE.MC` |
    | Copenhague | `.CO` | `NOVO-B.CO` |

    Les données proviennent de **Yahoo Finance** via yfinance. Mises à jour toutes les heures.
    """)

# ---------------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------------
st.divider()
st.caption("""
⚠️ **Disclaimer** : Ce dashboard est un outil d'aide à l'analyse financière,
il ne constitue pas un conseil en investissement. Les données proviennent de Yahoo Finance
(gratuit, non garanti pour usage professionnel). L'utilisateur reste seul responsable
de ses décisions d'investissement. Les ratios de valorisation ont plus de sens en contexte
relatif (vs pairs, vs historique) qu'en valeur absolue.
""")
