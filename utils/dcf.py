"""
Valorisation DCF à 2 étapes + valeur terminale (Gordon Growth Model).

Stage 1 : années 1-5, taux de croissance élevé (capé à 40%)
Stage 2 : années 6-10, décroissance vers la moitié du taux stage 1
Terminal : Gordon Growth Model avec taux terminal = 3%

WACC = rf + beta * prime_marché, clampé [8%, 15%]
rf = 4.5% (taux 10Y US Trésor, 2025)
prime_marché = 5.5% (Damodaran 2025)
"""

from utils.ratios import _safe_float, _clamp

RISK_FREE_RATE = 0.045
MARKET_PREMIUM = 0.055
TERMINAL_GROWTH = 0.03
WACC_MIN = 0.08
WACC_MAX = 0.15
GROWTH_CAP_STAGE1 = 0.40
STAGE1_YEARS = 5
STAGE2_YEARS = 5


def _compute_wacc(beta) -> float:
    b = _safe_float(beta)
    if b is None or b <= 0:
        b = 1.0
    b = min(b, 3.0)
    return _clamp(RISK_FREE_RATE + b * MARKET_PREMIUM, WACC_MIN, WACC_MAX)


def _resolve_growth(info: dict) -> tuple:
    """Retourne (growth_rate, source_label) ou (None, reason)."""
    eg = _safe_float(info.get("earningsGrowth"))
    rg = _safe_float(info.get("revenueGrowth"))
    if eg is not None and eg > 0:
        return min(eg, GROWTH_CAP_STAGE1), "earningsGrowth"
    if rg is not None and rg > 0:
        return min(rg, GROWTH_CAP_STAGE1), "revenueGrowth"
    return None, "no_growth_data"


def compute_dcf(info: dict) -> dict:
    """
    Calcule la valeur intrinsèque DCF par action.

    Retourne un dict avec :
      intrinsic_value     : float | None — valeur intrinsèque par action
      current_price       : float | None
      margin_of_safety    : float | None — (intrinsic - price) / intrinsic
      dcf_score           : float — 0 à 100
      confidence          : "Élevée" | "Modérée" | "Faible"
      wacc                : float | None
      growth_rate_stage1  : float | None
      growth_rate_stage2  : float | None
      fcf_per_share       : float | None
      details             : dict  — décomposition pour affichage
    """
    base = {
        "intrinsic_value": None,
        "current_price": None,
        "margin_of_safety": None,
        "dcf_score": 0.0,
        "confidence": "Faible",
        "wacc": None,
        "growth_rate_stage1": None,
        "growth_rate_stage2": None,
        "fcf_per_share": None,
        "details": {},
    }

    fcf = _safe_float(info.get("freeCashflow"))
    shares = _safe_float(info.get("sharesOutstanding"))
    price = _safe_float(info.get("currentPrice")) or _safe_float(info.get("regularMarketPrice"))
    base["current_price"] = price

    if not fcf or fcf <= 0 or not shares or shares <= 0:
        base["details"]["reason"] = (
            "FCF négatif ou nul, ou nombre d'actions manquant — DCF non calculable"
        )
        return base

    fcf_per_share = fcf / shares
    base["fcf_per_share"] = fcf_per_share

    beta = _safe_float(info.get("beta"))
    wacc = _compute_wacc(beta)
    base["wacc"] = wacc

    growth_s1, growth_source = _resolve_growth(info)
    if growth_s1 is None:
        base["details"]["reason"] = (
            "earningsGrowth et revenueGrowth indisponibles — DCF non calculable"
        )
        return base

    growth_s2 = growth_s1 / 2.0
    base["growth_rate_stage1"] = growth_s1
    base["growth_rate_stage2"] = growth_s2

    # --- Projection des flux ---
    pv_total = 0.0
    cf = fcf_per_share
    year_cashflows = []

    for yr in range(1, STAGE1_YEARS + 1):
        cf = cf * (1 + growth_s1)
        pv = cf / ((1 + wacc) ** yr)
        pv_total += pv
        year_cashflows.append({"Année": yr, "FCF/action": round(cf, 4), "PV FCF/action": round(pv, 4), "Stage": 1})

    pv_stage1 = pv_total

    for offset in range(1, STAGE2_YEARS + 1):
        yr = STAGE1_YEARS + offset
        cf = cf * (1 + growth_s2)
        pv = cf / ((1 + wacc) ** yr)
        pv_total += pv
        year_cashflows.append({"Année": yr, "FCF/action": round(cf, 4), "PV FCF/action": round(pv, 4), "Stage": 2})

    pv_stage2 = pv_total - pv_stage1

    if wacc <= TERMINAL_GROWTH:
        base["details"]["reason"] = "WACC ≤ taux terminal — impossible de calculer la valeur terminale"
        return base

    # Gordon Growth Model
    terminal_fcf = cf * (1 + TERMINAL_GROWTH)
    terminal_value = terminal_fcf / (wacc - TERMINAL_GROWTH)
    n_total = STAGE1_YEARS + STAGE2_YEARS
    pv_terminal = terminal_value / ((1 + wacc) ** n_total)

    intrinsic = pv_stage1 + pv_stage2 + pv_terminal
    if intrinsic <= 0:
        base["details"]["reason"] = "Valeur intrinsèque calculée négative ou nulle"
        return base

    base["intrinsic_value"] = round(intrinsic, 2)

    # Marge de sécurité : (intrinsic - price) / intrinsic
    mos = None
    if price and price > 0:
        mos = (intrinsic - price) / intrinsic
        base["margin_of_safety"] = round(mos, 4)

    # Score DCF : MoS +30% → 100, 0% → 50, -30% → 0
    if mos is not None:
        dcf_score = _clamp((mos + 0.30) / 0.60 * 100, 0.0, 100.0)
    else:
        dcf_score = 50.0
    base["dcf_score"] = round(dcf_score, 1)

    # Confidence
    beta_ok = beta is not None and 0.3 <= beta <= 3.0
    if growth_source == "earningsGrowth" and beta_ok:
        base["confidence"] = "Élevée"
    else:
        base["confidence"] = "Modérée"

    base["details"] = {
        "year_cashflows": year_cashflows,
        "pv_stage1": round(pv_stage1, 2),
        "pv_stage2": round(pv_stage2, 2),
        "pv_terminal": round(pv_terminal, 2),
        "terminal_value": round(terminal_value, 2),
        "growth_source": growth_source,
        "beta_used": beta if beta else 1.0,
    }

    return base


# ---------------------------------------------------------------------------
# Scénarios DCF (bull / base / bear)
# ---------------------------------------------------------------------------

def _run_scenario(fcf_per_share: float, growth_s1: float, growth_s2: float,
                  wacc: float, price) -> dict:
    """
    Exécute un DCF avec les paramètres fournis.
    Retourne {"intrinsic_value", "margin_of_safety", "growth_s1"}.
    """
    if wacc <= TERMINAL_GROWTH:
        return {"intrinsic_value": None, "margin_of_safety": None, "growth_s1": growth_s1}

    pv_total = 0.0
    cf = fcf_per_share

    for yr in range(1, STAGE1_YEARS + 1):
        cf = cf * (1 + growth_s1)
        pv_total += cf / ((1 + wacc) ** yr)

    for offset in range(1, STAGE2_YEARS + 1):
        yr = STAGE1_YEARS + offset
        cf = cf * (1 + growth_s2)
        pv_total += cf / ((1 + wacc) ** yr)

    terminal_fcf = cf * (1 + TERMINAL_GROWTH)
    terminal_value = terminal_fcf / (wacc - TERMINAL_GROWTH)
    n_total = STAGE1_YEARS + STAGE2_YEARS
    pv_terminal = terminal_value / ((1 + wacc) ** n_total)

    intrinsic = pv_total + pv_terminal
    if intrinsic <= 0:
        return {"intrinsic_value": None, "margin_of_safety": None, "growth_s1": growth_s1}

    mos = None
    if price and price > 0:
        mos = round((intrinsic - price) / intrinsic, 4)

    return {
        "intrinsic_value": round(intrinsic, 2),
        "margin_of_safety": mos,
        "growth_s1": growth_s1,
    }


def compute_dcf_scenarios(info: dict) -> dict:
    """
    Calcule 3 scénarios DCF (optimiste / central / pessimiste).

    Retourne :
    {
      "available": bool,
      "bull": {"intrinsic_value", "margin_of_safety", "growth_s1"},
      "base": {...},
      "bear": {...},
    }
    """
    _unavail = {"available": False, "bull": {}, "base": {}, "bear": {}}

    fcf    = _safe_float(info.get("freeCashflow"))
    shares = _safe_float(info.get("sharesOutstanding"))
    price  = _safe_float(info.get("currentPrice")) or _safe_float(info.get("regularMarketPrice"))
    beta   = _safe_float(info.get("beta"))

    if not fcf or fcf <= 0 or not shares or shares <= 0:
        return _unavail

    base_growth, _ = _resolve_growth(info)
    if base_growth is None:
        return _unavail

    fcf_per_share = fcf / shares
    wacc_base = _compute_wacc(beta)

    # Paramètres scénarios
    bull_s1 = min(base_growth * 1.4, 0.50)
    bull_s2 = bull_s1 * 0.6

    bear_s1 = base_growth * 0.5
    bear_s2 = bear_s1 / 2.0
    wacc_bear = min(wacc_base + 0.015, WACC_MAX)

    base_s1 = base_growth
    base_s2 = base_growth / 2.0

    return {
        "available": True,
        "bull": _run_scenario(fcf_per_share, bull_s1, bull_s2, wacc_base, price),
        "base": _run_scenario(fcf_per_share, base_s1, base_s2, wacc_base, price),
        "bear": _run_scenario(fcf_per_share, bear_s1, bear_s2, wacc_bear, price),
    }

    return base
