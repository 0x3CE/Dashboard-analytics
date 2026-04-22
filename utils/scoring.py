"""
Score composite combinant valorisation, analystes et qualité.
"""

import math

from utils.ratios import score_valuation, score_quality, _safe_float, _clamp, score_earnings_growth, score_revenue_growth


# ---------------------------------------------------------------------------
# Score analystes
# ---------------------------------------------------------------------------

def score_analyst_recommendation(info: dict) -> float | None:
    """
    Convertit recommendationMean (1=Strong Buy, 5=Strong Sell) en score 0-100.
    Formule : (5 - mean) / 4 * 100
    """
    mean = _safe_float(info.get("recommendationMean"))
    if mean is None:
        return None
    return _clamp((5.0 - mean) / 4.0 * 100, 0.0, 100.0)


def score_analyst_upside(info: dict) -> float | None:
    """
    Score basé sur l'upside vs target mean.
    Bornes : -20% (→ 0) à +50% (→ 100).
    """
    target = _safe_float(info.get("targetMeanPrice"))
    current = _safe_float(info.get("currentPrice")) or _safe_float(info.get("regularMarketPrice"))
    if target is None or current is None or current == 0:
        return None

    upside = (target - current) / current  # ex: 0.25 = +25%
    # Bornes -0.20 → 0, +0.50 → 100
    score = (upside - (-0.20)) / (0.50 - (-0.20)) * 100
    return _clamp(score, 0.0, 100.0)


def score_analysts(info: dict) -> float:
    """
    Score analystes agrégé sur 30 pts.
    Poids : recommandation×15, upside×15.
    """
    scores_weights = [
        (score_analyst_recommendation(info), 15),
        (score_analyst_upside(info), 15),
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
# Score composite
# ---------------------------------------------------------------------------

def score_growth(info: dict) -> float:
    """
    Score de croissance agrégé sur 15 pts.
    Poids : earningsGrowth×8, revenueGrowth×7.
    """
    scores_weights = [
        (score_earnings_growth(info.get("earningsGrowth")), 8),
        (score_revenue_growth(info.get("revenueGrowth")), 7),
    ]
    tw, ws = 0, 0.0
    for s, w in scores_weights:
        if s is not None:
            ws += s * w
            tw += w
    if tw == 0:
        return 0.0
    return (ws / tw) * 15 / 100


def compute_composite_score(info: dict) -> dict:
    """
    Retourne un dict avec :
    - valuation  : score 0-35  (multiples, sectoriel + growth-adjusted)
    - dcf        : score 0-20  (valeur intrinsèque DCF)
    - growth     : score 0-15  (croissance bénéfices + CA)
    - analysts   : score 0-20
    - quality    : score 0-10
    - composite  : score total 0-100
    - has_data   : bool
    - dcf_result : dict brut du DCF (pour affichage dans l'onglet dédié)
    """
    from utils.dcf import compute_dcf

    sector = info.get("sector")

    val = score_valuation(info, sector=sector)
    dcf_result = compute_dcf(info)
    dcf_pts = dcf_result["dcf_score"] * 20 / 100
    gro = score_growth(info)
    ana = score_analysts(info)
    qua = score_quality(info)
    composite = val + dcf_pts + gro + ana + qua

    has_data = val > 0 or ana > 0

    return {
        "valuation": round(val, 1),
        "dcf": round(dcf_pts, 1),
        "growth": round(gro, 1),
        "analysts": round(ana, 1),
        "quality": round(qua, 1),
        "composite": round(composite, 1),
        "has_data": has_data,
        "dcf_result": dcf_result,
    }


# ---------------------------------------------------------------------------
# Détection des divergences
# ---------------------------------------------------------------------------

def classify_opportunity(val_score_raw: float, analyst_score_raw: float) -> str | None:
    """
    Détecte les divergences intéressantes.
    val_score_raw : score valuation 0-50
    analyst_score_raw : score analystes 0-30

    Normalisation interne en percentile 0-100 avant classification.
    """
    # Normaliser sur 100
    val_pct = val_score_raw / 35 * 100
    ana_pct = analyst_score_raw / 20 * 100

    low_val = val_pct >= 65     # valuation attractive (score élevé = sous-évalué)
    high_val = val_pct <= 35    # valuation chère
    low_ana = ana_pct <= 35     # analystes négatifs
    high_ana = ana_pct >= 65    # analystes positifs

    if low_val and high_ana:
        return "Opportunité oubliée"
    if low_val and low_ana:
        return "Value trap potentiel"
    if high_val and high_ana:
        return "Sur-évaluation consensuelle"
    return None


OPPORTUNITY_COLORS = {
    "Opportunité oubliée": "green",
    "Value trap potentiel": "red",
    "Sur-évaluation consensuelle": "orange",
}
