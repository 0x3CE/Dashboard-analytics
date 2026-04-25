"""
Page 2 — Analyse détaillée d'une entreprise.
Sections : Header → Valorisation → Santé financière → États financiers → Graphiques → Dividende
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.styles import apply_custom_css, PLOTLY_DARK_LAYOUT, CHART_COLORS, GAUGE_STEPS, bloomberg_layout
from utils.topbar import render_ticker_tape, render_topnav
import utils.watchlist as wl
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
    score_earnings_growth,
    score_revenue_growth,
)
from utils.sector_benchmarks import get_sector_benchmarks, score_vs_sector
from utils.dcf import compute_dcf, compute_dcf_scenarios
from utils.scoring import compute_composite_score
from utils.analysis import (
    classify_growth_regime,
    detect_strengths,
    detect_risks,
    generate_verdict,
)

st.set_page_config(page_title="Analyse Entreprise", page_icon="🔍", layout="wide")
apply_custom_css()
render_ticker_tape()
render_topnav("analyse")

# ---------------------------------------------------------------------------
# Initialisation session state
# ---------------------------------------------------------------------------
st.session_state.setdefault("selected_ticker", "AAPL")
wl.init_session_state()

# ---------------------------------------------------------------------------
# Sidebar — sélection du ticker
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<p class="section-label">Company Analysis</p>', unsafe_allow_html=True)
    ticker_input = st.text_input(
        "Ticker",
        value=st.session_state["selected_ticker"],
        placeholder="AAPL   OR.PA   SAP.DE",
        help="Yahoo Finance ticker format.",
    ).strip().upper()

    if ticker_input:
        st.session_state["selected_ticker"] = ticker_input

    st.divider()
    st.markdown('<p class="section-label">Watchlist</p>', unsafe_allow_html=True)
    if st.button("+ ADD TO WATCHLIST", use_container_width=True):
        if ticker_input:
            if wl.add(ticker_input):
                st.success(f"{ticker_input} added.")
            else:
                st.info("Already in watchlist.")

    if st.session_state["watchlist"]:
        for wt in list(st.session_state["watchlist"]):
            col1, col2 = st.columns([3, 1])
            if col1.button(wt, key=f"wl_{wt}", use_container_width=True):
                st.session_state["selected_ticker"] = wt
                st.rerun()
            if col2.button("X", key=f"rm_{wt}"):
                wl.remove(wt)
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
name = safe_get(info, 'longName', symbol)
st.markdown(f'<div style="color:#FF6600;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:2px;">{symbol}</div>', unsafe_allow_html=True)
st.title(f"{name}")

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
# ---------------------------------------------------------------------------
# Analyse contextuelle — calcul (une seule fois, réutilisé dans tous les onglets)
# ---------------------------------------------------------------------------
with st.spinner("Analyse contextuelle…"):
    scores     = compute_composite_score(info)
    dcf_result = scores["dcf_result"]
    regime     = classify_growth_regime(info)
    strengths  = detect_strengths(info, scores, dcf_result)
    risks      = detect_risks(info, scores, dcf_result)
    verdict    = generate_verdict(info, scores, dcf_result, regime)

# ---------------------------------------------------------------------------
# Section "Analyse contextuelle" — toujours visible, avant les onglets
# ---------------------------------------------------------------------------
st.subheader("🧠 Analyse contextuelle")

_regime_color_map = {
    "blue": "blue", "green": "green", "yellow": "orange",
    "gray": "gray", "red": "red",
}
_badge_color = _regime_color_map.get(regime["color"], "gray")
st.markdown(
    f"**{regime['emoji']} RÉGIME :** :{_badge_color}[**{regime['regime']}**]"
    f" — *{regime['description']}*"
)

_col_left, _col_right = st.columns(2)
with _col_left:
    st.markdown("**✅ Points forts**")
    if strengths:
        for _s in strengths:
            st.markdown(f"- {_s}")
    else:
        st.caption("Aucun signal positif identifié.")

with _col_right:
    st.markdown("**⚠️ Points de vigilance**")
    if risks:
        for _r in risks:
            st.markdown(f"- {_r}")
    else:
        st.caption("Aucun signal de risque identifié.")

st.markdown(f"> **Verdict :** {verdict}")
st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Valorisation",
    "💪 Santé financière",
    "📈 États financiers",
    "📉 Graphiques",
    "💰 Dividende",
    "🎯 Valorisation Intrinsèque",
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

    # Jauge de valorisation globale (secteur-relative, growth-adjusted)
    st.divider()
    sector = safe_get(info, "sector")
    val_score = score_valuation(info, sector=sector)
    val_pct = val_score / 35 * 100
    label = valuation_label(val_score)

    st.subheader(f"Valorisation globale : {label}")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val_pct,
        number={"suffix": " / 100", "font": {"size": 22, "color": "#F0F0F0",
                                              "family": "'IBM Plex Mono', monospace"}},
        gauge={
            "axis": {"range": [0, 100],
                     "tickfont": {"color": "#555555", "size": 9},
                     "tickcolor": "#2A2A2A"},
            "bar": {"color": CHART_COLORS["primary"]},
            "bgcolor": "#0D0D0D",
            "bordercolor": "#2A2A2A",
            "steps": GAUGE_STEPS,
            "threshold": {
                "line": {"color": "#F0F0F0", "width": 2},
                "thickness": 0.75,
                "value": val_pct,
            },
        },
        title={"text": "VALUATION SCORE VS SECTOR MEDIAN (0=EXPENSIVE · 100=ATTRACTIVE)",
               "font": {"color": "#555555", "size": 10,
                        "family": "'IBM Plex Mono', monospace"}},
    ))
    fig_gauge.update_layout(height=300, margin=dict(t=60, b=0, l=20, r=20),
                             paper_bgcolor="#111111",
                             font={"family": "'IBM Plex Mono', monospace"})
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Tableau comparaison sectorielle
    st.divider()
    st.subheader(f"Comparaison sectorielle — {sector or 'Secteur inconnu'}")
    benchmarks = get_sector_benchmarks(sector)
    sector_rows = []
    for ratio_key, ratio_label, info_key in [
        ("pe",        "PE Trailing",  "trailingPE"),
        ("ps",        "Price/Sales",  "priceToSalesTrailing12Months"),
        ("peg",       "PEG Ratio",    "pegRatio"),
        ("pb",        "Price/Book",   "priceToBook"),
        ("ev_ebitda", "EV/EBITDA",    "enterpriseToEbitda"),
    ]:
        company_val = safe_get(info, info_key)
        median_val = benchmarks.get(ratio_key)
        vs_score = score_vs_sector(company_val, ratio_key, sector)
        vs_median = None
        if company_val is not None and median_val and median_val != 0:
            vs_median = (company_val - median_val) / median_val
        sector_rows.append({
            "Ratio": ratio_label,
            "Entreprise": fmt_ratio(company_val),
            "Médiane secteur": fmt_ratio(median_val),
            "Vs médiane": fmt_upside(vs_median) if vs_median is not None else "N/A",
            "Score /100": f"{vs_score:.0f}" if vs_score is not None else "N/A",
        })
    st.dataframe(sector_rows, use_container_width=True, hide_index=True)

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

    st.subheader("Croissance")
    eg = safe_get(info, "earningsGrowth")
    rg = safe_get(info, "revenueGrowth")
    eg_score = score_earnings_growth(eg)
    rg_score = score_revenue_growth(rg)

    def _growth_icon(score):
        if score is None:
            return "⚪"
        return "🟢" if score >= 65 else "🟡" if score >= 35 else "🔴"

    col1, col2 = st.columns(2)
    col1.metric(f"{_growth_icon(eg_score)} Croissance bénéfices (YoY)", fmt_pct(eg) if eg is not None else "N/A")
    col2.metric(f"{_growth_icon(rg_score)} Croissance revenus (YoY)", fmt_pct(rg) if rg is not None else "N/A")

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
                fig.add_bar(name="Revenus (Mrd)", x=years, y=rev,
                            marker_color=CHART_COLORS["primary"], marker_line_width=0)
                fig.add_bar(name="Résultat net (Mrd)", x=years, y=ni,
                            marker_color=CHART_COLORS["success"], marker_line_width=0)
                fig.update_layout(
                    **bloomberg_layout("Évolution Revenus & Résultat Net",
                                       barmode="group",
                                       xaxis_title="Année",
                                       yaxis_title=f"Mrd {display_currency}",
                                       height=350),
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
            labels={"Close": f"Prix ({display_currency})", "index": "Date"},
        )
        fig_price.update_traces(line_color=CHART_COLORS["primary"], line_width=1.5)
        fig_price.update_layout(**bloomberg_layout(f"Prix de clôture 5 ans — {symbol}", height=400))
        st.plotly_chart(fig_price, use_container_width=True)

        # Évolution marge nette si données dispo
        if not income.empty and "Net Income" in income.index and "Total Revenue" in income.index:
            years = [c.strftime("%Y") for c in income.columns]
            margins = (income.loc["Net Income"] / income.loc["Total Revenue"] * 100).values
            fig_margin = go.Figure()
            fig_margin.add_scatter(
                x=years, y=margins,
                mode="lines+markers",
                line=dict(color=CHART_COLORS["success"], width=2),
                marker=dict(color=CHART_COLORS["success"], size=7),
                name="Marge nette %",
            )
            fig_margin.update_layout(
                **bloomberg_layout("Évolution de la Marge Nette",
                                   xaxis_title="Année",
                                   yaxis_title="Marge nette (%)",
                                   height=300),
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

# ---- TAB 6 : Valorisation Intrinsèque (DCF) ----------------------------------
with tab6:
    import pandas as pd
    st.subheader("Valorisation DCF — Modèle à 2 étapes")

    dcf = dcf_result  # déjà calculé dans le bloc d'analyse contextuelle

    conf_colors = {"Élevée": "green", "Modérée": "orange", "Faible": "red"}
    conf_color = conf_colors.get(dcf["confidence"], "gray")
    st.markdown(f"**Fiabilité du modèle :** :{conf_color}[{dcf['confidence']}]")

    if dcf["intrinsic_value"] is None:
        reason = dcf["details"].get("reason", "Données insuffisantes.")
        st.warning(f"DCF non calculable : {reason}")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Valeur intrinsèque (DCF)", fmt_currency(dcf["intrinsic_value"], display_currency))
        col2.metric("Prix actuel", fmt_currency(dcf["current_price"], display_currency))

        mos = dcf["margin_of_safety"]
        mos_pct = f"{mos * 100:+.1f} %" if mos is not None else "N/A"
        mos_delta_color = "normal" if mos is None else ("normal" if mos >= 0 else "inverse")
        col3.metric("Marge de sécurité", mos_pct, delta=mos_pct, delta_color=mos_delta_color)

        st.divider()
        st.subheader("Hypothèses du modèle")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("WACC", f"{dcf['wacc'] * 100:.1f} %")
        col2.metric("Croissance Stage 1 (×5 ans)", f"{dcf['growth_rate_stage1'] * 100:.1f} %")
        col3.metric("Croissance Stage 2 (×5 ans)", f"{dcf['growth_rate_stage2'] * 100:.1f} %")
        col4.metric("FCF / action", fmt_currency(dcf["fcf_per_share"], display_currency))

        col1, col2 = st.columns(2)
        col1.metric("Taux terminal (Gordon)", "3.0 %")
        col2.metric("Source taux croissance", dcf["details"].get("growth_source", "N/A"))

        st.divider()
        st.subheader("Décomposition de la valeur intrinsèque")
        d = dcf["details"]
        decomp = pd.DataFrame([
            {"Composante": "PV Stage 1 (années 1–5)",   "Valeur / action": fmt_currency(d.get("pv_stage1"), display_currency)},
            {"Composante": "PV Stage 2 (années 6–10)",  "Valeur / action": fmt_currency(d.get("pv_stage2"), display_currency)},
            {"Composante": "PV Valeur terminale",        "Valeur / action": fmt_currency(d.get("pv_terminal"), display_currency)},
            {"Composante": "TOTAL",                      "Valeur / action": fmt_currency(dcf["intrinsic_value"], display_currency)},
        ])
        st.dataframe(decomp, use_container_width=True, hide_index=True)

        with st.expander("Détail des flux actualisés par année"):
            yearly = d.get("year_cashflows", [])
            if yearly:
                df_fcf = pd.DataFrame(yearly)
                df_fcf["FCF/action"] = df_fcf["FCF/action"].apply(lambda x: fmt_currency(x, display_currency))
                df_fcf["PV FCF/action"] = df_fcf["PV FCF/action"].apply(lambda x: fmt_currency(x, display_currency))
                df_fcf["Stage"] = df_fcf["Stage"].apply(lambda x: f"Stage {x}")
                st.dataframe(df_fcf, use_container_width=True, hide_index=True)

    # --- Scénarios bull / base / bear ---
    st.divider()
    st.subheader("Analyse de scénarios DCF")

    scenarios = compute_dcf_scenarios(info)

    if not scenarios.get("available"):
        st.info("Scénarios non disponibles — DCF de base non calculable.")
    else:
        def _mos_label(mos):
            return f"{mos * 100:+.1f} %" if mos is not None else "N/A"

        s_bull = scenarios["bull"]
        s_base = scenarios["base"]
        s_bear = scenarios["bear"]

        col_bull, col_base, col_bear = st.columns(3)

        with col_bull:
            st.markdown("**Scénario optimiste**")
            st.metric(
                f"Croissance S1 : {s_bull['growth_s1']*100:.0f}%/an",
                fmt_currency(s_bull.get("intrinsic_value"), display_currency),
                delta=_mos_label(s_bull.get("margin_of_safety")),
                delta_color="normal",
            )
        with col_base:
            st.markdown("**Scénario central**")
            st.metric(
                f"Croissance S1 : {s_base['growth_s1']*100:.0f}%/an",
                fmt_currency(s_base.get("intrinsic_value"), display_currency),
                delta=_mos_label(s_base.get("margin_of_safety")),
                delta_color="normal",
            )
        with col_bear:
            st.markdown("**Scénario pessimiste**")
            st.metric(
                f"Croissance S1 : {s_bear['growth_s1']*100:.0f}%/an",
                fmt_currency(s_bear.get("intrinsic_value"), display_currency),
                delta=_mos_label(s_bear.get("margin_of_safety")),
                delta_color="inverse",
            )

    st.info(
        "⚠️ Ce DCF est une estimation indicative basée sur les données Yahoo Finance. "
        "Il ne constitue pas un conseil en investissement. Les projections reposent sur "
        "des hypothèses simplifiées (taux de croissance constant par étape, WACC approché via beta, "
        "taux terminal fixe à 3%). Pour une analyse professionnelle, utilisez un modèle complet "
        "intégrant la structure du capital et des scénarios de croissance multiples."
    )
