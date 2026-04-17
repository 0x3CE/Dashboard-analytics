"""
Page 1 — Screener multi-ratios.
Filtre un univers de tickers sur des critères fondamentaux.
"""

import io

import pandas as pd
import streamlit as st

from utils.data import get_universe_data
from utils.formatting import fmt_market_cap, fmt_pct, fmt_ratio, safe_get
from utils.ratios import ratio_color, score_ev_ebitda, score_pe, score_peg, score_pb, score_ps
from utils.universes import UNIVERSES

st.set_page_config(page_title="Screener", page_icon="🔎", layout="wide")

st.session_state.setdefault("selected_ticker", "AAPL")
st.session_state.setdefault("watchlist", [])

# ---------------------------------------------------------------------------
# Sidebar — filtres
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🔎 Screener")

    universe_name = st.selectbox("Univers", list(UNIVERSES.keys()))
    custom_input = st.text_area(
        "Ou tickers personnalisés (un par ligne)",
        placeholder="AAPL\nOR.PA\nSAP.DE",
        height=80,
    )

    st.divider()
    st.subheader("Filtres de valorisation")

    pe_max = st.number_input("PE max", min_value=0.0, max_value=200.0, value=25.0, step=1.0)
    fpe_max = st.number_input("Forward PE max", min_value=0.0, max_value=200.0, value=25.0, step=1.0)
    ps_max = st.number_input("Price/Sales max", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
    peg_max = st.number_input("PEG max", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
    pb_max = st.number_input("Price/Book max", min_value=0.0, max_value=30.0, value=5.0, step=0.5)
    ev_max = st.number_input("EV/EBITDA max", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
    div_min = st.number_input(
        "Rendement dividende min (%)", min_value=0.0, max_value=20.0, value=0.0, step=0.5
    )

    st.divider()
    st.subheader("Filtres qualitatifs")

    all_sectors = [
        "Tous",
        "Technology", "Healthcare", "Financials", "Consumer Cyclical",
        "Consumer Defensive", "Energy", "Industrials", "Basic Materials",
        "Communication Services", "Utilities", "Real Estate",
    ]
    sector_filter = st.multiselect("Secteurs", all_sectors[1:], default=[])

    run_scan = st.button("🚀 Lancer le screening", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Logique de scan
# ---------------------------------------------------------------------------
if run_scan:
    if custom_input.strip():
        tickers = [t.strip().upper() for t in custom_input.strip().splitlines() if t.strip()]
    else:
        tickers = UNIVERSES[universe_name]

    st.info(f"Scan de {len(tickers)} tickers en cours…")
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(i, total):
        progress_bar.progress(i / total)
        status_text.text(f"{i}/{total} tickers chargés")

    universe_data = get_universe_data(tickers, max_workers=5, progress_callback=update_progress)
    progress_bar.empty()
    status_text.empty()

    # ---------------------------------------------------------------------------
    # Construction du tableau
    # ---------------------------------------------------------------------------
    rows = []
    for sym, info in universe_data.items():
        if not info:
            continue

        pe = safe_get(info, "trailingPE")
        fpe = safe_get(info, "forwardPE")
        ps = safe_get(info, "priceToSalesTrailing12Months")
        peg = safe_get(info, "pegRatio")
        pb = safe_get(info, "priceToBook")
        ev = safe_get(info, "enterpriseToEbitda")
        div = safe_get(info, "dividendYield")
        mcap = safe_get(info, "marketCap")
        sector = safe_get(info, "sector", "")
        name = safe_get(info, "longName", sym)
        net_margin = safe_get(info, "profitMargins")
        roe = safe_get(info, "returnOnEquity")

        # Appliquer les filtres
        if pe is not None and pe > pe_max:
            continue
        if fpe is not None and fpe > fpe_max:
            continue
        if ps is not None and ps > ps_max:
            continue
        if peg is not None and peg > peg_max:
            continue
        if pb is not None and pb > pb_max:
            continue
        if ev is not None and ev > ev_max:
            continue
        if div_min > 0:
            if div is None or div * 100 < div_min:
                continue
        if sector_filter and sector not in sector_filter:
            continue

        rows.append({
            "Ticker": sym,
            "Nom": name,
            "Secteur": sector or "N/A",
            "Market Cap": mcap,
            "PE": pe,
            "Fwd PE": fpe,
            "PS": ps,
            "PEG": peg,
            "P/B": pb,
            "EV/EBITDA": ev,
            "Marge nette": net_margin,
            "ROE": roe,
            "Div. Yield": div,
        })

    if not rows:
        st.warning("Aucune entreprise ne correspond aux critères sélectionnés.")
        st.stop()

    df = pd.DataFrame(rows)
    df_sorted = df.sort_values("Market Cap", ascending=False).reset_index(drop=True)

    st.success(f"✅ {len(df_sorted)} entreprises correspondent aux critères.")

    # ---------------------------------------------------------------------------
    # Formatage pour affichage
    # ---------------------------------------------------------------------------
    df_display = pd.DataFrame()
    df_display["Ticker"] = df_sorted["Ticker"]
    df_display["Nom"] = df_sorted["Nom"]
    df_display["Secteur"] = df_sorted["Secteur"]
    df_display["Market Cap"] = df_sorted["Market Cap"].apply(fmt_market_cap)
    df_display["PE"] = df_sorted["PE"].apply(fmt_ratio)
    df_display["Fwd PE"] = df_sorted["Fwd PE"].apply(fmt_ratio)
    df_display["PS"] = df_sorted["PS"].apply(fmt_ratio)
    df_display["PEG"] = df_sorted["PEG"].apply(fmt_ratio)
    df_display["P/B"] = df_sorted["P/B"].apply(fmt_ratio)
    df_display["EV/EBITDA"] = df_sorted["EV/EBITDA"].apply(fmt_ratio)
    df_display["Marge nette"] = df_sorted["Marge nette"].apply(fmt_pct)
    df_display["ROE"] = df_sorted["ROE"].apply(fmt_pct)
    df_display["Div. Yield"] = df_sorted["Div. Yield"].apply(fmt_pct)

    # Color-coding via Styler
    def color_ratio_col(val, score_fn):
        """Applique couleur selon le score du ratio."""
        try:
            raw = float(val.replace("x", "").replace("N/A", "nan").replace("\u202f", ""))
            score = score_fn(raw)
            color = ratio_color(score)
            if color == "green":
                return "background-color: #d4edda; color: #155724"
            if color == "orange":
                return "background-color: #fff3cd; color: #856404"
            if color == "red":
                return "background-color: #f8d7da; color: #721c24"
        except (ValueError, AttributeError):
            pass
        return ""

    styler = df_display.style
    # Pas de .applymap chaîné complexe — on se contente d'un tableau lisible

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------------------------
    # Sélectionner un ticker pour analyse détaillée
    # ---------------------------------------------------------------------------
    st.divider()
    col1, col2 = st.columns([3, 1])
    selected_for_analysis = col1.selectbox(
        "Sélectionner un ticker pour analyse détaillée :",
        df_sorted["Ticker"].tolist(),
    )
    if col2.button("🔍 Analyser", type="primary"):
        st.session_state["selected_ticker"] = selected_for_analysis
        st.switch_page("pages/2_Analyse_Entreprise.py")

    # ---------------------------------------------------------------------------
    # Export CSV
    # ---------------------------------------------------------------------------
    csv_buf = io.StringIO()
    df_sorted.to_csv(csv_buf, index=False)
    st.download_button(
        label="📥 Télécharger les résultats (CSV)",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name="screener_resultats.csv",
        mime="text/csv",
    )

else:
    st.info("Configurez vos filtres dans la sidebar et cliquez sur **Lancer le screening**.")
    with st.expander("ℹ️ Comment utiliser le screener ?"):
        st.markdown("""
        1. **Sélectionnez un univers** (CAC 40, S&P 500, etc.) ou entrez vos propres tickers.
        2. **Ajustez les filtres** : chaque ratio doit être **inférieur** à la valeur saisie.
        3. **Lancez le scan** : les données sont récupérées en parallèle (mise en cache 1h).
        4. **Analysez** en détail un ticker en le sélectionnant dans la liste résultante.

        **Rappel des ratios :**
        - **PE** : Prix / Bénéfice. Attractif < 15.
        - **PS** : Prix / Chiffre d'affaires. Attractif < 2.
        - **PEG** : PE / Croissance des bénéfices. Attractif < 1.
        - **P/B** : Prix / Valeur comptable. Attractif < 2.
        - **EV/EBITDA** : Valeur d'entreprise / EBITDA. Attractif < 10.
        """)
