"""
Page 3 — Consensus & Recommandations Analystes.
"""

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from utils.data import get_ticker_info, get_ticker_history, get_upgrades_downgrades
from utils.formatting import fmt_currency, fmt_pct, fmt_upside, safe_get, normalize_price_gbp
from utils.scoring import score_analyst_recommendation, score_analyst_upside

st.set_page_config(page_title="Consensus Analystes", page_icon="🎯", layout="wide")

st.session_state.setdefault("selected_ticker", "AAPL")
st.session_state.setdefault("watchlist", [])

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🎯 Consensus Analystes")
    ticker_input = st.text_input(
        "Ticker",
        value=st.session_state["selected_ticker"],
        placeholder="ex: AAPL, OR.PA, SAP.DE",
    ).strip().upper()

    if ticker_input:
        st.session_state["selected_ticker"] = ticker_input

symbol = st.session_state["selected_ticker"]

if not symbol:
    st.info("Entrez un ticker dans la sidebar.")
    st.stop()

with st.spinner(f"Chargement du consensus pour {symbol}…"):
    info = get_ticker_info(symbol)

if not info:
    st.error(f"Aucune donnée disponible pour **{symbol}**.")
    st.stop()

currency = safe_get(info, "currency", "")
current_price_raw = safe_get(info, "currentPrice") or safe_get(info, "regularMarketPrice")
current_price, display_currency = normalize_price_gbp(current_price_raw, currency)

st.title(f"🎯 Consensus Analystes — {safe_get(info, 'longName', symbol)}")

# ---------------------------------------------------------------------------
# Section A — Recommandations actuelles
# ---------------------------------------------------------------------------
st.subheader("Recommandations actuelles")

reco_mean = safe_get(info, "recommendationMean")
reco_key = safe_get(info, "recommendationKey", "N/A")
nb_analysts = safe_get(info, "numberOfAnalystOpinions")

col1, col2, col3 = st.columns(3)
col1.metric("Recommandation", (reco_key or "N/A").replace("_", " ").title())
col2.metric(
    "Score moyen",
    f"{reco_mean:.2f} / 5" if reco_mean else "N/A",
    help="1 = Strong Buy, 5 = Strong Sell",
)
col3.metric("Nb d'analystes", str(nb_analysts) if nb_analysts else "N/A")

# Score analystes
score_reco = score_analyst_recommendation(info)
score_up = score_analyst_upside(info)
if score_reco is not None or score_up is not None:
    c1, c2 = st.columns(2)
    if score_reco is not None:
        c1.metric("Score recommandation (0–100)", f"{score_reco:.1f}")
    if score_up is not None:
        c2.metric("Score upside (0–100)", f"{score_up:.1f}")

# Breakdown si disponible (strong_buy, buy, hold, sell, strong_sell dans info)
breakdown_keys = {
    "Strong Buy": safe_get(info, "strongBuy") or safe_get(info, "recommendationsBuy"),
    "Buy": safe_get(info, "buy"),
    "Hold": safe_get(info, "hold"),
    "Sell": safe_get(info, "sell"),
    "Strong Sell": safe_get(info, "strongSell") or safe_get(info, "recommendationsSell"),
}
breakdown = {k: v for k, v in breakdown_keys.items() if v is not None and v > 0}

if breakdown:
    st.divider()
    st.subheader("Répartition des recommandations")
    colors = ["#00CC44", "#8BC34A", "#FFA500", "#FF7043", "#FF4B4B"]
    fig_bar = go.Figure(go.Bar(
        x=list(breakdown.values()),
        y=list(breakdown.keys()),
        orientation="h",
        marker_color=colors[:len(breakdown)],
        text=list(breakdown.values()),
        textposition="outside",
    ))
    fig_bar.update_layout(
        title="Nombre d'analystes par recommandation",
        xaxis_title="Nombre d'analystes",
        height=300,
        margin=dict(l=0, r=30, t=40, b=0),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------------------------
# Section B — Price Targets
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Price Targets")

t_low = safe_get(info, "targetLowPrice")
t_mean = safe_get(info, "targetMeanPrice")
t_median = safe_get(info, "targetMedianPrice")
t_high = safe_get(info, "targetHighPrice")

if t_mean is None and t_high is None:
    st.info("Price targets non disponibles pour ce ticker.")
else:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Target bas", fmt_currency(t_low, display_currency))
    col2.metric("Target moyen", fmt_currency(t_mean, display_currency))
    col3.metric("Target médiane", fmt_currency(t_median, display_currency))
    col4.metric("Target haut", fmt_currency(t_high, display_currency))

    if current_price and t_mean:
        upside = (t_mean - current_price) / current_price
        upside_str = fmt_upside(upside)
        delta_color = "normal" if upside >= 0 else "inverse"
        col5.metric(
            "Upside potentiel",
            upside_str,
            delta=upside_str,
            delta_color=delta_color,
        )

    # Visualisation du prix actuel vs fourchette
    if current_price and t_low and t_high and t_mean:
        fig_range = go.Figure()

        # Bande low–high
        fig_range.add_shape(
            type="rect",
            x0=0, x1=1,
            y0=t_low, y1=t_high,
            fillcolor="rgba(33, 150, 243, 0.1)",
            line=dict(color="rgba(33, 150, 243, 0.3)"),
        )

        # Ligne prix actuel
        fig_range.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="#2196F3",
            annotation_text=f"Prix actuel: {fmt_currency(current_price, display_currency)}",
            annotation_position="right",
        )
        # Ligne target moyen
        fig_range.add_hline(
            y=t_mean,
            line_dash="dot",
            line_color="#4CAF50",
            annotation_text=f"Target moyen: {fmt_currency(t_mean, display_currency)}",
            annotation_position="right",
        )

        fig_range.update_layout(
            title="Prix actuel vs fourchette de targets",
            showlegend=False,
            height=350,
            xaxis=dict(visible=False),
            yaxis_title=f"Prix ({display_currency})",
            yaxis=dict(range=[t_low * 0.85, t_high * 1.10]),
        )

        # Ajouter prix actuel et targets comme points
        fig_range.add_scatter(
            x=[0.5], y=[current_price],
            mode="markers",
            marker=dict(color="#2196F3", size=14, symbol="diamond"),
            name="Prix actuel",
        )
        fig_range.add_scatter(
            x=[0.5], y=[t_mean],
            mode="markers",
            marker=dict(color="#4CAF50", size=14, symbol="circle"),
            name="Target moyen",
        )
        if t_low:
            fig_range.add_scatter(
                x=[0.5], y=[t_low],
                mode="markers",
                marker=dict(color="#FF7043", size=10, symbol="triangle-down"),
                name="Target bas",
            )
        if t_high:
            fig_range.add_scatter(
                x=[0.5], y=[t_high],
                mode="markers",
                marker=dict(color="#4CAF50", size=10, symbol="triangle-up"),
                name="Target haut",
            )

        st.plotly_chart(fig_range, use_container_width=True)

    # Prix historique + bande targets
    with st.spinner("Chargement de l'historique…"):
        hist = get_ticker_history(symbol, period="1y")

    if not hist.empty and t_mean is not None:
        import plotly.express as px
        fig_hist = go.Figure()
        fig_hist.add_scatter(
            x=hist.index, y=hist["Close"],
            mode="lines",
            name="Prix",
            line=dict(color="#2196F3"),
        )
        if t_low and t_high:
            fig_hist.add_scatter(
                x=list(hist.index) + list(reversed(hist.index)),
                y=[t_high] * len(hist) + [t_low] * len(hist),
                fill="toself",
                fillcolor="rgba(76, 175, 80, 0.1)",
                line=dict(color="rgba(76, 175, 80, 0)"),
                name="Fourchette targets",
            )
        fig_hist.add_hline(y=t_mean, line_dash="dot", line_color="#4CAF50",
                           annotation_text="Target moyen")
        fig_hist.update_layout(
            title="Historique 1 an + fourchette des targets analystes",
            xaxis_title="Date",
            yaxis_title=f"Prix ({display_currency})",
            height=400,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# ---------------------------------------------------------------------------
# Section C — Historique des upgrades/downgrades
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Historique des upgrades / downgrades")

with st.spinner("Chargement des upgrades/downgrades…"):
    upgrades = get_upgrades_downgrades(symbol)

if upgrades.empty:
    st.info("Historique des upgrades/downgrades non disponible.")
else:
    # Afficher les 20 plus récents
    df_ud = upgrades.head(20).copy()
    if "GradeDate" in df_ud.columns:
        df_ud["GradeDate"] = pd.to_datetime(df_ud["GradeDate"]).dt.strftime("%d/%m/%Y")

    # Coloration Action
    def color_action(val):
        if isinstance(val, str):
            v = val.lower()
            if "upgrade" in v or "init" in v or "buy" in v:
                return "background-color: #d4edda"
            if "downgrade" in v or "sell" in v:
                return "background-color: #f8d7da"
        return ""

    st.dataframe(df_ud, use_container_width=True, hide_index=True)
