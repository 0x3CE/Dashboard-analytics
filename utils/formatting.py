"""
Helpers de formatage pour l'affichage des données financières.
"""


def fmt_market_cap(val, currency: str = "") -> str:
    """Formate une capitalisation boursière en K/M/Mrd."""
    if val is None or val != val:  # None ou NaN
        return "N/A"
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "N/A"

    suffix = f" {currency}" if currency else ""
    if abs(val) >= 1e12:
        return f"{val / 1e12:.2f} Bn{suffix}"
    if abs(val) >= 1e9:
        return f"{val / 1e9:.2f} Mrd{suffix}"
    if abs(val) >= 1e6:
        return f"{val / 1e6:.2f} M{suffix}"
    if abs(val) >= 1e3:
        return f"{val / 1e3:.2f} K{suffix}"
    return f"{val:.2f}{suffix}"


def fmt_pct(val, decimals: int = 2) -> str:
    """Formate une valeur décimale en pourcentage. Ex: 0.1234 → '12.34 %'"""
    if val is None or val != val:
        return "N/A"
    try:
        return f"{float(val) * 100:.{decimals}f} %"
    except (TypeError, ValueError):
        return "N/A"


def fmt_ratio(val, decimals: int = 2, suffix: str = "x") -> str:
    """Formate un ratio. Ex: 15.234 → '15.23x'"""
    if val is None or val != val:
        return "N/A"
    try:
        return f"{float(val):.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "N/A"


def fmt_number(val, decimals: int = 2) -> str:
    """Formate un nombre avec séparateur de milliers."""
    if val is None or val != val:
        return "N/A"
    try:
        return f"{float(val):,.{decimals}f}".replace(",", "\u202f")
    except (TypeError, ValueError):
        return "N/A"


def fmt_currency(val, currency: str = "", decimals: int = 2) -> str:
    """Formate un montant avec devise."""
    if val is None or val != val:
        return "N/A"
    try:
        formatted = f"{float(val):,.{decimals}f}".replace(",", "\u202f")
        return f"{formatted} {currency}".strip() if currency else formatted
    except (TypeError, ValueError):
        return "N/A"


def fmt_upside(val) -> str:
    """Formate un upside en % avec signe. Ex: 0.123 → '+12.30 %'"""
    if val is None or val != val:
        return "N/A"
    try:
        pct = float(val) * 100
        sign = "+" if pct >= 0 else ""
        return f"{sign}{pct:.2f} %"
    except (TypeError, ValueError):
        return "N/A"


def safe_get(d: dict, key: str, default=None):
    """Récupère une valeur depuis un dict en gérant None et NaN."""
    val = d.get(key, default)
    if val is None:
        return default
    try:
        import math
        if isinstance(val, float) and math.isnan(val):
            return default
    except (TypeError, ValueError):
        pass
    return val


def normalize_price_gbp(price, currency: str):
    """
    Le LSE donne parfois les prix en GBX (pence).
    Si currency == 'GBp', diviser par 100 pour obtenir GBP.
    """
    if currency == "GBp" and price is not None:
        try:
            return float(price) / 100, "GBP"
        except (TypeError, ValueError):
            pass
    return price, currency
