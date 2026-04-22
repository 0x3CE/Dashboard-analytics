"""
Calcul de scores 0-100 pour chaque ratio financier.
Bornes issues de la spec section 6.
"""

import math


def _safe_float(val):
    if val is None:
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (TypeError, ValueError):
        return None


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def _linear_score(val: float, good: float, bad: float) -> float:
    """
    Score linéaire 0-100 entre `good` (→ 100) et `bad` (→ 0).
    Fonctionne que good < bad ou good > bad.
    """
    if good == bad:
        return 50.0
    score = (val - bad) / (good - bad) * 100
    return _clamp(score, 0.0, 100.0)


# ---------------------------------------------------------------------------
# Scores de valorisation (bornes spec §6)
# ---------------------------------------------------------------------------

def score_pe(pe) -> float | None:
    """PE trailing. Attractif < 10, Très cher > 30."""
    val = _safe_float(pe)
    if val is None or val <= 0:
        return None
    return _linear_score(val, good=10.0, bad=30.0)


def score_forward_pe(fpe) -> float | None:
    """Forward PE. Attractif < 10, Très cher > 25."""
    val = _safe_float(fpe)
    if val is None or val <= 0:
        return None
    return _linear_score(val, good=10.0, bad=25.0)


def score_ps(ps) -> float | None:
    """Price/Sales. Attractif < 1, Très cher > 8."""
    val = _safe_float(ps)
    if val is None or val <= 0:
        return None
    return _linear_score(val, good=1.0, bad=8.0)


def score_peg(peg) -> float | None:
    """PEG. Attractif < 0.5, Très cher > 2.5."""
    val = _safe_float(peg)
    if val is None or val <= 0:
        return None
    return _linear_score(val, good=0.5, bad=2.5)


def score_pb(pb) -> float | None:
    """Price/Book. Attractif < 1, Très cher > 5."""
    val = _safe_float(pb)
    if val is None or val <= 0:
        return None
    return _linear_score(val, good=1.0, bad=5.0)


def score_ev_ebitda(ev_ebitda) -> float | None:
    """EV/EBITDA. Attractif < 6, Très cher > 20."""
    val = _safe_float(ev_ebitda)
    if val is None or val <= 0:
        return None
    return _linear_score(val, good=6.0, bad=20.0)


# ---------------------------------------------------------------------------
# Scores de croissance
# ---------------------------------------------------------------------------

def score_earnings_growth(growth) -> float | None:
    """Croissance des bénéfices YoY. good=30%, bad=0%. Négatif → None."""
    val = _safe_float(growth)
    if val is None or val < 0:
        return None
    return _linear_score(val, good=0.30, bad=0.0)


def score_revenue_growth(growth) -> float | None:
    """Croissance du CA YoY. good=20%, bad=0%. Négatif → None."""
    val = _safe_float(growth)
    if val is None or val < 0:
        return None
    return _linear_score(val, good=0.20, bad=0.0)


def score_pe_growth_adjusted(pe, growth_rate) -> float | None:
    """
    PE avec bornes dynamiques basées sur la croissance.
    Principe : un PE juste ≈ 1× le taux de croissance en % (règle PEG=1).
      good = max(8, growth_pct * 0.8)
      bad  = max(20, growth_pct * 2.5)
    Fallback sur bornes statiques si growth_rate None ou nul.
    """
    pe_val = _safe_float(pe)
    if pe_val is None or pe_val <= 0:
        return None
    growth_val = _safe_float(growth_rate)
    if not growth_val or growth_val <= 0:
        return _linear_score(pe_val, good=10.0, bad=30.0)
    growth_pct = growth_val * 100
    good = max(8.0, growth_pct * 0.8)
    bad = max(20.0, growth_pct * 2.5)
    return _linear_score(pe_val, good=good, bad=bad)


# ---------------------------------------------------------------------------
# Scores de qualité
# ---------------------------------------------------------------------------

def score_roe(roe) -> float | None:
    """ROE (décimal, ex: 0.20 = 20%). Excellent > 20%, Faible < 10%."""
    val = _safe_float(roe)
    if val is None:
        return None
    return _linear_score(val, good=0.20, bad=0.05)


def score_net_margin(margin) -> float | None:
    """Marge nette (décimal). Excellent > 20%, Faible < 5%."""
    val = _safe_float(margin)
    if val is None:
        return None
    return _linear_score(val, good=0.20, bad=0.0)


def score_debt_equity(de) -> float | None:
    """Debt/Equity. Inversé : moins = mieux. Excellent < 0.5, Faible > 2."""
    val = _safe_float(de)
    if val is None or val < 0:
        return None
    return _linear_score(val, good=0.0, bad=2.5)


# ---------------------------------------------------------------------------
# Scores agrégés
# ---------------------------------------------------------------------------

def score_valuation(info: dict, sector: str | None = None) -> float:
    """
    Score de valorisation agrégé sur 35 pts.
    Blend 40% statique (growth-adjusted) + 60% sectoriel.
    Si sector=None → 100% statique (rétrocompatible).
    Poids des ratios : PE×15, PS×10, PEG×10, P/B×5, EV/EBITDA×10.
    """
    from utils.sector_benchmarks import score_vs_sector as svs

    growth = _safe_float(info.get("earningsGrowth")) or _safe_float(info.get("revenueGrowth"))
    pe_raw = info.get("trailingPE")
    ps_raw = info.get("priceToSalesTrailing12Months")
    peg_raw = info.get("pegRatio")
    pb_raw = info.get("priceToBook")
    ev_raw = info.get("enterpriseToEbitda")

    static_sw = [
        (score_pe_growth_adjusted(pe_raw, growth), 15),
        (score_ps(ps_raw), 10),
        (score_peg(peg_raw), 10),
        (score_pb(pb_raw), 5),
        (score_ev_ebitda(ev_raw), 10),
    ]

    sector_sw = [
        (svs(pe_raw, "pe", sector), 15),
        (svs(ps_raw, "ps", sector), 10),
        (svs(peg_raw, "peg", sector), 10),
        (svs(pb_raw, "pb", sector), 5),
        (svs(ev_raw, "ev_ebitda", sector), 10),
    ]

    def _wavg(sw):
        tw, ws = 0, 0.0
        for s, w in sw:
            if s is not None:
                ws += s * w
                tw += w
        return (ws / tw) if tw > 0 else None

    static_avg = _wavg(static_sw)
    sector_avg = _wavg(sector_sw)

    if static_avg is None and sector_avg is None:
        return 0.0

    if sector is None or sector_avg is None:
        blended = static_avg or 0.0
    elif static_avg is None:
        blended = sector_avg
    else:
        blended = 0.4 * static_avg + 0.6 * sector_avg

    return blended * 35 / 100


def score_quality(info: dict) -> float:
    """
    Score de qualité agrégé sur 20 pts.
    Poids : ROE×7, Marge nette×7, Debt/Equity×6.
    """
    scores_weights = [
        (score_roe(info.get("returnOnEquity")), 7),
        (score_net_margin(info.get("profitMargins")), 7),
        (score_debt_equity(info.get("debtToEquity")), 6),
    ]
    total_weight = 0
    weighted_sum = 0.0
    for s, w in scores_weights:
        if s is not None:
            weighted_sum += s * w
            total_weight += w

    if total_weight == 0:
        return 0.0
    return (weighted_sum / total_weight) * 10 / 100


# ---------------------------------------------------------------------------
# Helpers visuels
# ---------------------------------------------------------------------------

def ratio_color(score: float | None) -> str:
    """Retourne 'green', 'orange' ou 'red' selon le score 0-100."""
    if score is None:
        return "gray"
    if score >= 65:
        return "green"
    if score >= 35:
        return "orange"
    return "red"


def valuation_label(composite_score: float) -> str:
    """Label qualitatif pour un score de valorisation normalisé 0-50."""
    pct = composite_score / 50 * 100
    if pct >= 65:
        return "Sous-évalué"
    if pct >= 35:
        return "Juste valorisé"
    return "Sur-évalué"
