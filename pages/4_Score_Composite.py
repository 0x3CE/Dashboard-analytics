"""
Page 4 — Score Composite.
Croise valorisation + analystes + qualité pour ranker un univers.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from utils.data import get_universe_data
from utils.formatting import fmt_market_cap, safe_get
from utils.scoring import (
    OPPORTUNITY_COLORS,
    classify_opportunity,
    compute_composite_score,
)
from utils.universes import UNIVERSES

st.set_page_config(page_title="Score Composite", page_icon="🏆", layout="wide")

st.session_state.setdefault("selected_ticker", "AAPL")
st.session_state.setdefault("watchlist", [])

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🏆 Score Composite")

    universe_name = st.selectbox("Univers", list(UNIVERSES.keys()))
    custom_input = st.text_area(
        "Ou tickers personnalisés (un par ligne)",
        placeholder="AAPL\nOR.PA\nSAP.DE",
        height=80,
    )

    st.divider()
    st.info("""
    **Pondération du score (/ 100) :**
    - Valorisation : 50 pts
    - Analystes : 30 pts
    - Qualité : 20 pts
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

    st.success(f"✅ Scores calculés pour {len(df)} entreprises.")

    # ---------------------------------------------------------------------------
    # Tableau principal
    # ---------------------------------------------------------------------------
    st.subheader("Classement par score composite")

    def highlight_score(val):
        try:
            v = float(val)
            if v >= 65:
                return "background-color: #d4edda; color: #155724"
            if v >= 40:
                return "background-color: #fff3cd; color: #856404"
            if v >= 0:
                return "background-color: #f8d7da; color: #721c24"
        except (TypeError, ValueError):
            pass
        return ""

    def highlight_divergence(val):
        if not val:
            return ""
        color = OPPORTUNITY_COLORS.get(val, "")
        if color == "green":
            return "background-color: #d4edda; font-weight: bold"
        if color == "red":
            return "background-color: #f8d7da; font-weight: bold"
        if color == "orange":
            return "background-color: #fff3cd; font-weight: bold"
        return ""

    df_display = df[["Rang", "Ticker", "Nom", "Secteur", "Valorisation", "Analystes", "Qualité", "Score Total", "Divergence"]].copy()
    df_display["Market Cap"] = df["Market Cap"].apply(fmt_market_cap)
    df_display["Valorisation"] = df_display["Valorisation"].apply(lambda x: f"{x:.1f}")
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
        title="Valorisation (X) vs Score Analystes (Y) — taille = Market Cap",
        labels={
            "Valorisation": "Score Valorisation (0–50)",
            "Analystes": "Score Analystes (0–30)",
        },
        size_max=50,
    )

    # Lignes de séparation quadrants
    fig_scatter.add_hline(y=15, line_dash="dot", line_color="gray", opacity=0.5)
    fig_scatter.add_vline(x=25, line_dash="dot", line_color="gray", opacity=0.5)

    # Annotations quadrants
    fig_scatter.add_annotation(x=40, y=28, text="Opportunité oubliée", showarrow=False,
                               font=dict(color="green", size=11), opacity=0.7)
    fig_scatter.add_annotation(x=40, y=2, text="Value trap potentiel", showarrow=False,
                               font=dict(color="red", size=11), opacity=0.7)
    fig_scatter.add_annotation(x=5, y=28, text="Sur-évaluation consensuelle", showarrow=False,
                               font=dict(color="orange", size=11), opacity=0.7)

    fig_scatter.update_traces(textposition="top center")
    fig_scatter.update_layout(height=550)
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
        | **Valorisation** | 50 pts | PE (15), PS (10), PEG (10), P/B (5), EV/EBITDA (10) |
        | **Analystes** | 30 pts | Recommandation moyenne (15), Upside vs target (15) |
        | **Qualité** | 20 pts | ROE (7), Marge nette (7), Debt/Equity inversé (6) |

        Chaque sous-score est normalisé 0–100 selon des bornes absolues (voir spec §6),
        puis pondéré pour obtenir le score final sur 100.

        ### Détection des divergences

        - 🟢 **Opportunité oubliée** : valorisation attractive ET analystes positifs
        - 🔴 **Value trap potentiel** : valorisation attractive MAIS analystes négatifs
        - 🟡 **Sur-évaluation consensuelle** : valorisation chère ET analystes positifs

        *Ces signaux ne constituent pas un conseil en investissement.*
        """)
