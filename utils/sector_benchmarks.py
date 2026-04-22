"""
Benchmarks de ratios par secteur (médiane GICS, données 2024/2025).
Sources: Damodaran Jan 2025, Bloomberg consensus.
"""

SECTOR_MEDIANS: dict = {
    "Technology": {
        "pe": 28.0, "ps": 5.5, "peg": 1.8, "pb": 7.0, "ev_ebitda": 20.0,
    },
    "Communication Services": {
        "pe": 22.0, "ps": 3.5, "peg": 1.5, "pb": 4.5, "ev_ebitda": 14.0,
    },
    "Consumer Cyclical": {
        "pe": 20.0, "ps": 1.2, "peg": 1.6, "pb": 4.0, "ev_ebitda": 12.0,
    },
    "Consumer Defensive": {
        "pe": 22.0, "ps": 1.5, "peg": 2.5, "pb": 5.5, "ev_ebitda": 15.0,
    },
    "Healthcare": {
        "pe": 24.0, "ps": 3.5, "peg": 1.9, "pb": 4.5, "ev_ebitda": 14.0,
    },
    "Financials": {
        "pe": 13.0, "ps": 2.5, "peg": 1.3, "pb": 1.4, "ev_ebitda": 10.0,
    },
    "Industrials": {
        "pe": 20.0, "ps": 1.8, "peg": 2.0, "pb": 4.0, "ev_ebitda": 13.0,
    },
    "Basic Materials": {
        "pe": 14.0, "ps": 1.2, "peg": 1.5, "pb": 2.2, "ev_ebitda": 8.0,
    },
    "Energy": {
        "pe": 12.0, "ps": 1.0, "peg": 1.2, "pb": 1.8, "ev_ebitda": 6.0,
    },
    "Utilities": {
        "pe": 17.0, "ps": 2.0, "peg": 2.5, "pb": 1.6, "ev_ebitda": 11.0,
    },
    "Real Estate": {
        "pe": 30.0, "ps": 5.0, "peg": 3.0, "pb": 2.0, "ev_ebitda": 18.0,
    },
}

DEFAULT_BENCHMARKS: dict = {
    "pe": 20.0, "ps": 2.5, "peg": 1.8, "pb": 3.5, "ev_ebitda": 13.0,
}

# Variantes yfinance → clés GICS standard
_SECTOR_ALIASES: dict = {
    "Consumer Discretionary": "Consumer Cyclical",
    "Information Technology": "Technology",
    "Materials": "Basic Materials",
    "Communication": "Communication Services",
    "Financial Services": "Financials",
}


def _normalize_sector(sector: str) -> str:
    return _SECTOR_ALIASES.get(sector, sector)


def get_sector_benchmarks(sector: str | None) -> dict:
    """
    Retourne les médianes de ratios pour un secteur GICS.
    Retourne DEFAULT_BENCHMARKS si secteur inconnu ou None.
    """
    if sector is None:
        return DEFAULT_BENCHMARKS.copy()
    return SECTOR_MEDIANS.get(_normalize_sector(sector), DEFAULT_BENCHMARKS).copy()


def score_vs_sector(value, ratio_name: str, sector: str | None) -> float | None:
    """
    Score 0-100 comparant value à la médiane sectorielle.
    50 = exactement à la médiane (juste valorisé vs secteur).
    100 = moitié de la médiane (très attractif).
    0 = double de la médiane (très cher).

    ratio_name: "pe" | "ps" | "peg" | "pb" | "ev_ebitda"
    """
    if value is None:
        return None
    try:
        val = float(value)
    except (TypeError, ValueError):
        return None
    if val <= 0:
        return None

    benchmarks = get_sector_benchmarks(sector)
    median = benchmarks.get(ratio_name)
    if not median or median <= 0:
        return None

    # score = 100 - 50*(val/median)
    # val = median/2 → 75, val = median → 50, val = 2*median → 0
    raw = 100.0 - 50.0 * (val / median)
    return max(0.0, min(100.0, raw))
