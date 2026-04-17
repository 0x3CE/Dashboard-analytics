"""
Page 2 — Analyse détaillée d'une entreprise.
Sections : Header → Valorisation → Santé financière → États financiers → Graphiques → Dividende
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data import (
    get_balance_sheet,
    get_cash_flow,
    get_income_stmt,
    get_ticker_history,
    get_ticker_info,
)
from utils.formatting import (
    fmt_currency,
    fmt_market_cap,
    fmt_pct,
    fmt_ratio,
    fmt_upside,
    normalize_price_gbp,
    safe_get,
)
from utils.ratios import (
    ratio_color,
    score_ev_ebitda,
    score_forward_pe,
    score_pb,
    score_pe,
    score_peg,
    score_ps,
    valuation_label,
    score_valuation,
)

st.set_page_config(page_title="Analyse Entreprise", page_icon="🔍", layout="wide")

# ---------------------------------------------------------------------------
# Initialisation session state
# ---------------------------------------------------------------------------
st.session_state.setdefault("selected_ticker", "AAPL")
st.session_state.setdefault("watchlist", [])

# ---------------------------------------------------------------------------
# Sidebar — sélection du ticker
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🔍 Analyse Entreprise")
    ticker_input = st.text_input(
        "Ticker",
        value=st.session_state["selected_ticker"],
        placeholder="ex: AAPL, OR.PA, SAP.DE",
        help="Entrez un ticker au format Yahoo Finance.",
    ).strip().upper()

    if ticker_input:
        st.session_state["selected_ticker"] = ticker_input

    # Watchlist
    st.divider()
    st.subheader("⭐ Ma Watchlist")
    if st.button("➕ Ajouter à la watchlist", use_container_width=True):
        if ticker_input and ticker_input not in st.session_state["watchlist"]:
            st.session_state["watchlist"].append(ticker_input)
            st.success(f"{ticker_input} ajouté !")
        elif ticker_input in st.session_state["watchlist"]:
            st.info("Déjà dans la watchlist.")

    if st.session_state["watchlist"]:
        for wt in st.session_state["watchlist"]:
            col1, col2 = st.columns([3, 1])
            if col1.button(wt, key=f"wl_{wt}", use_container_width=True):
                st.session_state["selected_ticker"] = wt
                st.rerun()
            if col2.button("✕", key=f"rm_{wt}"):
                st.session_state["watchlist"].remove(wt)
                st.rerun()

symbol = st.session_state["selected_ticker"]

if not symbol:
    st.info("Entrez un ticker dans la sidebar pour commencer l'analyse.")
    st.stop()

# ---------------------------------------------------------------------------
# Chargement des données
# ---------------------------------------------------------------------------
with st.spinner(f"Chargement des données pour {symbol}…"):
    info = get_ticker_info(symbol)

if not info:
    st.error(f"Aucune donnée disponible pour **{symbol}**. Vérifiez le ticker.")
    st.stop()

currency = safe_get(info, "currency", "")
# Correction LSE pence
current_price_raw = safe_get(info, "currentPrice") or safe_get(info, "regularMarketPrice")
current_price, display_currency = normalize_price_gbp(current_price_raw, currency)

# ---------------------------------------------------------------------------
# Header — informations générales
# ---------------------------------------------------------------------------
st.title(f"🏢 {safe_get(info, 'longName', symbol)}")

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Prix actuel",
    fmt_currency(current_price, display_currency) if current_price else "N/A",
    delta=fmt_pct(safe_get(info, "regularMarketChangePercent")) if safe_get(info, "regularMarketChangePercent") else None,
)
col2.metric("Market Cap", fmt_market_cap(safe_get(info, "marketCap"), display_currency))
col3.metric("Secteur", safe_get(info, "sector", "N/A"))
col4.metric("Pays", safe_get(info, "country", "N/A"))

with st.expander("ℹ️ Description de l'entreprise"):
    desc = safe_get(info, "longBusinessSummary", "Description non disponible.")
    st.write(desc)
    cols = st.columns(3)
    cols[0].write(f"**Industrie :** {safe_get(info, 'industry', 'N/A')}")
    cols[1].write(f"**Bourse :** {safe_get(info, 'exchange', 'N/A')}")
    cols[2].write(f"**Site :** {safe_get(info, 'website', 'N/A')}")

st.divider()

# ---------------------------------------------------------------------------
# Onglets principaux
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Valorisation",
    "💪 Santé financière",
    "📈 États financiers",
    "📉 Graphiques",
    "💰 Dividende",
])

# ---- TAB 1 : Valorisation --------------------------------------------------
with tab1:
    st.subheader("Ratios de valorisation")

    ratios = [
        ("PE (Trailing)", safe_get(info, "trailingPE"), score_pe, ""),
        ("PE (Forward)", safe_get(info, "forwardPE"), score_forward_pe, ""),
        ("Price/Sales", safe_get(info, "priceToSalesTrailing12Months"), score_ps, ""),
        ("PEG Ratio", safe_get(info, "pegRatio"), score_peg, ""),
        ("Price/Book", safe_get(info, "priceToBook"), score_pb, ""),
        ("EV/EBITDA", safe_get(info, "enterpriseToEbitda"), score_ev_ebitda, ""),
        ("EV/Revenue", safe_get(info, "enterpriseToRevenue"), None, ""),
    ]

    cols = st.columns(4)
    for i, (label, val, score_fn, _) in enumerate(ratios):
        score = score_fn(val) if score_fn and val is not None else None
        color = ratio_color(score)
        col = cols[i % 4]
        with col:
            if color == "green":
                icon = "🟢"
            elif color == "orange":
                icon = "🟡"
            elif color == "red":
                icon = "🔴"
            else:
                icon = "⚪"
            col.metric(f"{icon} {label}", fmt_ratio(val))

    # Jauge de valorisation globale
    st.divider()
    val_score = score_valuation(info)
    val_pct = val_score / 50 * 100
    label = valuation_label(val_score)

    st.subheader(f"Valorisation globale : {label}")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val_pct,
        number={"suffix": " / 100", "font": {"size": 24}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "steelblue"},
            "steps": [
                {"range": [0, 35], "color": "#FF4B4B"},
                {"range": [35, 65], "color": "#FFA500"},
                {"range": [65, 100], "color": "#00CC44"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 3},
                "thickness": 0.75,
                "value": val_pct,
            },
        },
        title={"text": "Score Valorisation (0=Cher, 100=Très attractif)"},
    ))
    fig_gauge.update_layout(height=300, margin=dict(t=60, b=0, l=20, r=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

# ---- TAB 2 : Santé financière ----------------------------------------------
with tab2:
    st.subheader("Marges")
    col1, col2, col3 = st.columns(3)
    col1.metric("Marge brute", fmt_pct(safe_get(info, "grossMargins")))
    col2.metric("Marge opérationnelle", fmt_pct(safe_get(info, "operatingMargins")))
    col3.metric("Marge nette", fmt_pct(safe_get(info, "profitMargins")))

    st.subheader("Rentabilité")
    col1, col2, col3 = st.columns(3)
    col1.metric("ROE", fmt_pct(safe_get(info, "returnOnEquity")))
    col2.metric("ROA", fmt_pct(safe_get(info, "returnOnAssets")))
    col3.metric("ROIC", fmt_pct(safe_get(info, "returnOnCapital")))

    st.subheader("Structure financière")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Debt/Equity", fmt_ratio(safe_get(info, "debtToEquity")))
    col2.metric("Current Ratio", fmt_ratio(safe_get(info, "currentRatio")))
    col3.metric("Quick Ratio", fmt_ratio(safe_get(info, "quickRatio")))
    col4.metric(
        "Free Cash Flow",
        fmt_market_cap(safe_get(info, "freeCashflow"), display_currency),
    )

    col1, col2 = st.columns(2)
    col1.metric("Total Cash", fmt_market_cap(safe_get(info, "totalCash"), display_currency))
    col2.metric("Total Debt", fmt_market_cap(safe_get(info, "totalDebt"), display_currency))

# ---- TAB 3 : États financiers ----------------------------------------------
with tab3:
    with st.spinner("Chargement des états financiers…"):
        income = get_income_stmt(symbol)
        balance = get_balance_sheet(symbol)
        cashflow = get_cash_flow(symbol)

    if income.empty and balance.empty and cashflow.empty:
        st.warning("États financiers non disponibles pour ce ticker.")
    else:
        if not income.empty:
            st.subheader("Compte de résultat")
            # Transposer : dates en index, items en colonnes
            income_t = income.T.copy()
            income_t.index = income_t.index.strftime("%Y")

            rows_of_interest = [
                "Total Revenue", "Gross Profit", "Operating Income",
                "Net Income", "EBITDA", "Basic EPS",
            ]
            available = [r for r in rows_of_interest if r in income_t.columns]
            if available:
                df_show = income_t[available].copy()
                # Formatage en millions
                numeric_cols = [c for c in df_show.columns if c != "Basic EPS"]
                for c in numeric_cols:
                    df_show[c] = df_show[c].apply(
                        lambda x: f"{x/1e9:.2f} Mrd" if x is not None and x == x else "N/A"
                    )
                st.dataframe(df_show, use_container_width=True)

            # Graphique revenus / résultat net
            rev_row = "Total Revenue"
            ni_row = "Net Income"
            if rev_row in income.index and ni_row in income.index:
                years = [c.strftime("%Y") for c in income.columns]
                rev = income.loc[rev_row].values / 1e9
                ni = income.loc[ni_row].values / 1e9

                fig = go.Figure()
                fig.add_bar(name="Revenus (Mrd)", x=years, y=rev, marker_color="#2196F3")
                fig.add_bar(name="Résultat net (Mrd)", x=years, y=ni, marker_color="#4CAF50")
                fig.update_layout(
                    title="Évolution Revenus & Résultat Net",
                    barmode="group",
                    xaxis_title="Année",
                    yaxis_title=f"Mrd {display_currency}",
                    height=350,
                )
                st.plotly_chart(fig, use_container_width=True)

        if not balance.empty:
            st.subheader("Bilan simplifié")
            balance_t = balance.T.copy()
            balance_t.index = balance_t.index.strftime("%Y")
            rows_b = ["Total Assets", "Total Liabilities Net Minority Interest", "Stockholders Equity"]
            available_b = [r for r in rows_b if r in balance_t.columns]
            if available_b:
                df_b = balance_t[available_b].copy()
                for c in available_b:
                    df_b[c] = df_b[c].apply(
                        lambda x: f"{x/1e9:.2f} Mrd" if x is not None and x == x else "N/A"
                    )
                st.dataframe(df_b, use_container_width=True)

# ---- TAB 4 : Graphiques historiques ----------------------------------------
with tab4:
    with st.spinner("Chargement de l'historique de prix…"):
        hist = get_ticker_history(symbol, period="5y")

    if hist.empty:
        st.warning("Historique de prix non disponible.")
    else:
        # Prix 5 ans
        fig_price = px.line(
            hist, x=hist.index, y="Close",
            title=f"Prix de clôture sur 5 ans — {symbol}",
            labels={"Close": f"Prix ({display_currency})", "index": "Date"},
        )
        fig_price.update_traces(line_color="#2196F3")
        fig_price.update_layout(height=400)
        st.plotly_chart(fig_price, use_container_width=True)

        # Évolution marge nette si données dispo
        if not income.empty and "Net Income" in income.index and "Total Revenue" in income.index:
            years = [c.strftime("%Y") for c in income.columns]
            margins = (income.loc["Net Income"] / income.loc["Total Revenue"] * 100).values
            fig_margin = go.Figure()
            fig_margin.add_scatter(
                x=years, y=margins,
                mode="lines+markers",
                line=dict(color="#4CAF50"),
                name="Marge nette %",
            )
            fig_margin.update_layout(
                title="Évolution de la Marge Nette",
                xaxis_title="Année",
                yaxis_title="Marge nette (%)",
                height=300,
            )
            st.plotly_chart(fig_margin, use_container_width=True)

# ---- TAB 5 : Dividende -----------------------------------------------------
with tab5:
    div_yield = safe_get(info, "dividendYield")
    payout = safe_get(info, "payoutRatio")
    div_rate = safe_get(info, "dividendRate")
    ex_date = safe_get(info, "exDividendDate")

    if div_yield is None and div_rate is None:
        st.info("Cette entreprise ne verse pas de dividende (ou les données ne sont pas disponibles).")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Rendement dividende", fmt_pct(div_yield))
        col2.metric("Dividende annuel", fmt_currency(div_rate, display_currency))
        col3.metric("Payout Ratio", fmt_pct(payout))

        if safe_get(info, "fiveYearAvgDividendYield"):
            st.metric(
                "Rendement moyen 5 ans",
                f"{safe_get(info, 'fiveYearAvgDividendYield'):.2f} %",
            )

        if ex_date:
            import datetime
            try:
                date_str = datetime.datetime.fromtimestamp(ex_date).strftime("%d/%m/%Y")
                st.info(f"📅 Prochaine date ex-dividende : **{date_str}**")
            except Exception:
                pass
