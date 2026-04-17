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

def score_valuation(info: dict) -> float:
    """
    Score de valorisation agrégé sur 50 pts.
    Poids : PE×15, PS×10, PEG×10, P/B×5, EV/EBITDA×10.
    """
    scores_weights = [
        (score_pe(info.get("trailingPE")), 15),
        (score_ps(info.get("priceToSalesTrailing12Months")), 10),
        (score_peg(info.get("pegRatio")), 10),
        (score_pb(info.get("priceToBook")), 5),
        (score_ev_ebitda(info.get("enterpriseToEbitda")), 10),
    ]
    total_weight = 0
    weighted_sum = 0.0
    for s, w in scores_weights:
        if s is not None:
            weighted_sum += s * w
            total_weight += w

    if total_weight == 0:
        return 0.0
    # Ramener sur 50 pts
    return (weighted_sum / total_weight) * 50 / 100


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
    return (weighted_sum / total_weight) * 20 / 100


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
