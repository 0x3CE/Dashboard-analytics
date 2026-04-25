"""
Page 4 — Score Composite.
Croise valorisation + analystes + qualité pour ranker un univers.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from utils.styles import apply_custom_css, PLOTLY_DARK_LAYOUT, CHART_COLORS, bloomberg_layout
from utils.topbar import render_ticker_tape, render_topnav
import utils.watchlist as wl
from utils.data import get_universe_data
from utils.formatting import fmt_market_cap, safe_get
from utils.scoring import (
    OPPORTUNITY_COLORS,
    classify_opportunity,
    compute_composite_score,
)
from utils.universes import UNIVERSES

st.set_page_config(page_title="Score Composite", page_icon="🏆", layout="wide")
apply_custom_css()
render_ticker_tape()
render_topnav("score")

st.session_state.setdefault("selected_ticker", "AAPL")
wl.init_session_state()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<p class="section-label">Composite Score</p>', unsafe_allow_html=True)

    universe_name = st.selectbox("Universe", list(UNIVERSES.keys()))
    custom_input = st.text_area(
        "Ou tickers personnalisés (un par ligne)",
        placeholder="AAPL\nOR.PA\nSAP.DE",
        height=80,
    )

    st.divider()
    st.info("""
    **Pondération du score (/ 100) :**
    - Valorisation (sectorielle) : 35 pts
    - DCF valeur intrinsèque : 20 pts
    - Croissance : 15 pts
    - Analystes : 20 pts
    - Qualité : 10 pts
    """)

    run_scan = st.button("🚀 Calculer les scores", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Logique
# ---------------------------------------------------------------------------
if run_scan:
    if custom_input.strip():
        tickers = [t.strip().upper() for t in custom_input.strip().splitlines() if t.strip()]
    else:
        tickers = UNIVERSES[universe_name]

    st.info(f"Calcul des scores pour {len(tickers)} tickers…")
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(i, total):
        progress_bar.progress(i / total)
        status_text.text(f"{i}/{total} tickers chargés")

    universe_data = get_universe_data(tickers, max_workers=5, progress_callback=update_progress)
    progress_bar.empty()
    status_text.empty()

    # ---------------------------------------------------------------------------
    # Construction du tableau de scores
    # ---------------------------------------------------------------------------
    rows = []
    for sym, info in universe_data.items():
        if not info:
            continue

        scores = compute_composite_score(info)
        if not scores["has_data"]:
            continue

        opp = classify_opportunity(scores["valuation"], scores["analysts"])
        mcap = safe_get(info, "marketCap")
        sector = safe_get(info, "sector", "N/A")
        name = safe_get(info, "longName", sym)

        rows.append({
            "Ticker": sym,
            "Nom": name,
            "Secteur": sector,
            "Market Cap": mcap,
            "Valorisation": scores["valuation"],
            "DCF": scores["dcf"],
            "Croissance": scores["growth"],
            "Analystes": scores["analysts"],
            "Qualité": scores["quality"],
            "Score Total": scores["composite"],
            "Divergence": opp or "",
        })

    if not rows:
        st.warning("Aucune donnée disponible.")
        st.stop()

    df = pd.DataFrame(rows).sort_values("Score Total", ascending=False).reset_index(drop=True)
    df["Rang"] = df.index + 1

    # ---------------------------------------------------------------------------
    # Tableau principal
    # ---------------------------------------------------------------------------
    st.subheader("Classement par score composite")

    def highlight_score(val):
        try:
            v = float(val)
            if v >= 65:
                return "background-color: rgba(16,185,129,0.15); color: #6EE7B7"
            if v >= 40:
                return "background-color: rgba(245,158,11,0.12); color: #FCD34D"
            if v >= 0:
                return "background-color: rgba(239,68,68,0.12); color: #FCA5A5"
        except (TypeError, ValueError):
            pass
        return ""

    def highlight_divergence(val):
        if not val:
            return ""
        color = OPPORTUNITY_COLORS.get(val, "")
        if color == "green":
            return "background-color: rgba(16,185,129,0.15); color: #6EE7B7; font-weight: 600"
        if color == "red":
            return "background-color: rgba(239,68,68,0.12); color: #FCA5A5; font-weight: 600"
        if color == "orange":
            return "background-color: rgba(245,158,11,0.12); color: #FCD34D; font-weight: 600"
        return ""

    df_display = df[["Rang", "Ticker", "Nom", "Secteur", "Valorisation", "DCF", "Croissance", "Analystes", "Qualité", "Score Total", "Divergence"]].copy()
    df_display["Market Cap"] = df["Market Cap"].apply(fmt_market_cap)
    df_display["Valorisation"] = df_display["Valorisation"].apply(lambda x: f"{x:.1f}")
    df_display["DCF"] = df_display["DCF"].apply(lambda x: f"{x:.1f}")
    df_display["Croissance"] = df_display["Croissance"].apply(lambda x: f"{x:.1f}")
    df_display["Analystes"] = df_display["Analystes"].apply(lambda x: f"{x:.1f}")
    df_display["Qualité"] = df_display["Qualité"].apply(lambda x: f"{x:.1f}")
    df_display["Score Total"] = df_display["Score Total"].apply(lambda x: f"{x:.1f}")

    styled = df_display.style \
        .applymap(highlight_score, subset=["Score Total"]) \
        .applymap(highlight_divergence, subset=["Divergence"])

    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------------------------
    # Détection des divergences — résumé
    # ---------------------------------------------------------------------------
    divergences = df[df["Divergence"] != ""]
    if not divergences.empty:
        st.divider()
        st.subheader("🔍 Divergences détectées")

        for opp_type in ["Opportunité oubliée", "Value trap potentiel", "Sur-évaluation consensuelle"]:
            subset = divergences[divergences["Divergence"] == opp_type]
            if subset.empty:
                continue

            color = OPPORTUNITY_COLORS[opp_type]
            if color == "green":
                icon = "🟢"
            elif color == "red":
                icon = "🔴"
            else:
                icon = "🟡"

            st.markdown(f"**{icon} {opp_type}** ({len(subset)})")
            tickers_list = ", ".join(subset["Ticker"].tolist())
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{tickers_list}")

    # ---------------------------------------------------------------------------
    # Scatter plot : Valorisation vs Analystes
    # ---------------------------------------------------------------------------
    st.divider()
    st.subheader("Carte de positionnement : Valorisation vs Analystes")

    df_plot = df.copy()
    df_plot["Market Cap Norm"] = df_plot["Market Cap"].fillna(1e9).clip(lower=1e8)
    df_plot["Label"] = df_plot.apply(
        lambda r: f"{r['Ticker']}<br>{r['Divergence']}" if r["Divergence"] else r["Ticker"],
        axis=1,
    )

    fig_scatter = px.scatter(
        df_plot,
        x="Valorisation",
        y="Analystes",
        size="Market Cap Norm",
        color="Secteur",
        text="Ticker",
        hover_data={
            "Nom": True,
            "Score Total": True,
            "Divergence": True,
            "Market Cap Norm": False,
        },
        labels={
            "Valorisation": "Score Valorisation (0–35)",
            "Analystes": "Score Analystes (0–20)",
        },
        size_max=50,
        color_discrete_sequence=CHART_COLORS["scale_categorical"],
    )

    fig_scatter.add_hline(y=10, line_dash="dot", line_color="#334155", opacity=0.8)
    fig_scatter.add_vline(x=17.5, line_dash="dot", line_color="#334155", opacity=0.8)

    fig_scatter.add_annotation(x=28, y=18, text="Opportunité oubliée", showarrow=False,
                               font=dict(color="#6EE7B7", size=11), opacity=0.8)
    fig_scatter.add_annotation(x=28, y=2, text="Value trap potentiel", showarrow=False,
                               font=dict(color="#FCA5A5", size=11), opacity=0.8)
    fig_scatter.add_annotation(x=4, y=18, text="Sur-évaluation consensuelle", showarrow=False,
                               font=dict(color="#FCD34D", size=11), opacity=0.8)

    fig_scatter.update_traces(textposition="top center",
                               textfont=dict(color="#94A3B8", size=10))
    fig_scatter.update_layout(**bloomberg_layout(
        "Valorisation (X) vs Score Analystes (Y) — taille = Market Cap",
        height=550,
    ))
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ---------------------------------------------------------------------------
    # Lien vers analyse détaillée
    # ---------------------------------------------------------------------------
    st.divider()
    col1, col2 = st.columns([3, 1])
    selected = col1.selectbox("Analyser en détail :", df["Ticker"].tolist())
    if col2.button("🔍 Voir l'analyse", type="primary"):
        st.session_state["selected_ticker"] = selected
        st.switch_page("pages/2_Analyse_Entreprise.py")

else:
    st.info("Sélectionnez un univers et cliquez sur **Calculer les scores**.")
    with st.expander("ℹ️ Méthodologie du score composite"):
        st.markdown("""
        ### Score composite (/ 100)

        | Catégorie | Poids | Sous-métriques |
        |-----------|-------|----------------|
        | **Valorisation** | 35 pts | PE growth-adjusted (15), PS (10), PEG (10), P/B (5), EV/EBITDA (10) — comparé à la médiane sectorielle |
        | **DCF** | 20 pts | Valeur intrinsèque 2 étapes + Gordon Growth Model |
        | **Croissance** | 15 pts | earningsGrowth (8), revenueGrowth (7) |
        | **Analystes** | 20 pts | Recommandation moyenne (10), Upside vs target (10) |
        | **Qualité** | 10 pts | ROE (7/20), Marge nette (7/20), Debt/Equity (6/20) |

        Le scoring de valorisation blende 60% sectoriel (vs médiane Damodaran 2025) + 40% absolu.
        Le PE est ajusté de la croissance : bornes dynamiques basées sur earningsGrowth/revenueGrowth.

        ### Détection des divergences

        - 🟢 **Opportunité oubliée** : valorisation attractive ET analystes positifs
        - 🔴 **Value trap potentiel** : valorisation attractive MAIS analystes négatifs
        - 🟡 **Sur-évaluation consensuelle** : valorisation chère ET analystes positifs

        *Ces signaux ne constituent pas un conseil en investissement.*
        """)
