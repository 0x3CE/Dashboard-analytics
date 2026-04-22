"""
Moteur d'analyse contextuelle — interprétation verbale des données financières.
Aucun appel externe. Toutes les données proviennent du dict yfinance `info`.
"""

from utils.ratios import _safe_float


# ---------------------------------------------------------------------------
# Régime de croissance
# ---------------------------------------------------------------------------

def classify_growth_regime(info: dict) -> dict:
    """
    Classifie le régime de croissance d'une entreprise.
    Utilise earningsGrowth en priorité, revenueGrowth en fallback.
    """
    eg = _safe_float(info.get("earningsGrowth"))
    rg = _safe_float(info.get("revenueGrowth"))
    growth = eg if eg is not None else rg

    if growth is None:
        return {
            "regime": "Données insuffisantes",
            "emoji": "❓",
            "color": "gray",
            "description": "Données de croissance non disponibles — analyse de valorisation à interpréter avec prudence.",
            "use_classical_scoring": True,
            "key_metric": "N/A",
        }
    if growth > 0.30:
        return {
            "regime": "Hypercroissance",
            "emoji": "🚀",
            "color": "blue",
            "description": "Les métriques classiques de valorisation sont peu fiables — l'analyse doit se concentrer sur le PEG et la soutenabilité de la croissance.",
            "use_classical_scoring": False,
            "key_metric": "PEG",
        }
    if growth > 0.15:
        return {
            "regime": "Croissance forte",
            "emoji": "📈",
            "color": "green",
            "description": "Croissance solide qui peut justifier des multiples élevés — surveiller la cohérence entre croissance bénéfices et revenus.",
            "use_classical_scoring": True,
            "key_metric": "PEG",
        }
    if growth > 0.05:
        return {
            "regime": "Croissance modérée",
            "emoji": "🌱",
            "color": "yellow",
            "description": "Régime équilibré où les ratios PE et EV/EBITDA restent des guides fiables de valorisation.",
            "use_classical_scoring": True,
            "key_metric": "PE",
        }
    if growth >= 0.0:
        return {
            "regime": "Mature",
            "emoji": "🏛️",
            "color": "gray",
            "description": "Croissance limitée — le rendement du dividende et la génération de FCF priment sur les perspectives de progression.",
            "use_classical_scoring": True,
            "key_metric": "EV/EBITDA",
        }
    return {
        "regime": "Déclin",
        "emoji": "📉",
        "color": "red",
        "description": "Contraction en cours — la valorisation doit intégrer un risque de détérioration durable des fondamentaux.",
        "use_classical_scoring": True,
        "key_metric": "FCF",
    }


# ---------------------------------------------------------------------------
# Détection des points forts
# ---------------------------------------------------------------------------

def detect_strengths(info: dict, scores: dict, dcf_result: dict) -> list:
    """
    Retourne une liste de signaux positifs identifiés sur l'entreprise.
    """
    peg  = _safe_float(info.get("pegRatio"))
    eg   = _safe_float(info.get("earningsGrowth"))
    rg   = _safe_float(info.get("revenueGrowth"))
    gm   = _safe_float(info.get("grossMargins"))
    pm   = _safe_float(info.get("profitMargins"))
    rec  = _safe_float(info.get("recommendationMean"))
    roe  = _safe_float(info.get("returnOnEquity"))
    de   = _safe_float(info.get("debtToEquity"))
    mos  = dcf_result.get("margin_of_safety") if dcf_result else None

    result = []

    if peg is not None and peg < 1.0:
        result.append(f"PEG {peg:.2f} : la croissance semble sous-évaluée par le marché")

    if eg is not None and eg > 0.50:
        result.append(f"Croissance des bénéfices exceptionnelle à +{eg*100:.0f}% YoY")
    elif eg is not None and eg > 0.20:
        result.append(f"Bonne croissance des bénéfices à +{eg*100:.0f}% YoY")

    if rg is not None and rg > 0.30:
        result.append(f"Forte accélération du chiffre d'affaires à +{rg*100:.0f}% YoY")

    if gm is not None and gm > 0.60:
        result.append(f"Marge brute exceptionnelle à {gm*100:.0f}% — fossé concurrentiel marqué")

    if pm is not None and pm > 0.25:
        result.append(f"Marge nette solide à {pm*100:.0f}% — forte capacité bénéficiaire")

    if rec is not None and rec < 2.0:
        result.append(f"Consensus analystes très favorable (note {rec:.1f}/5 — forte conviction achat)")

    if mos is not None and mos > 0.20:
        result.append(f"DCF indique une décote de {mos*100:.0f}% par rapport à la valeur intrinsèque")

    if roe is not None and roe > 0.30:
        result.append(f"ROE élevé à {roe*100:.0f}% — capital alloué efficacement")

    if de is not None and de < 0.5:
        result.append(f"Bilan sain : levier financier faible (D/E {de:.2f})")

    return result


# ---------------------------------------------------------------------------
# Détection des risques
# ---------------------------------------------------------------------------

def detect_risks(info: dict, scores: dict, dcf_result: dict) -> list:
    """
    Retourne une liste de signaux de risque identifiés.
    """
    beta = _safe_float(info.get("beta"))
    ps   = _safe_float(info.get("priceToSalesTrailing12Months"))
    eg   = _safe_float(info.get("earningsGrowth"))
    rg   = _safe_float(info.get("revenueGrowth"))
    de   = _safe_float(info.get("debtToEquity"))
    peg  = _safe_float(info.get("pegRatio"))
    fcf  = _safe_float(info.get("freeCashflow"))
    mos  = dcf_result.get("margin_of_safety") if dcf_result else None

    result = []

    # Beta (mutuellement exclusif)
    if beta is not None and beta > 2.0:
        result.append(f"Beta {beta:.2f} : volatilité très élevée, drawdowns potentiels importants")
    elif beta is not None and beta > 1.5:
        result.append(f"Beta {beta:.2f} : volatilité supérieure au marché à surveiller")

    # P/S (mutuellement exclusif)
    if ps is not None and ps > 15:
        result.append(f"P/S {ps:.1f}x : multiple extrême — fort risque de compression en cas de ralentissement")
    elif ps is not None and ps > 8:
        result.append(f"P/S {ps:.1f}x : multiple élevé qui laisse peu de marge à l'erreur")

    if mos is not None and mos < -0.40:
        result.append("DCF indique une forte surévaluation (>40%) — fiabilité réduite sur les hypercroissances")

    if eg is not None and rg is not None and eg > 0 and rg > 0 and eg < rg * 0.5:
        result.append(
            f"Croissance bénéfices (+{eg*100:.0f}%) nettement inférieure à la croissance CA (+{rg*100:.0f}%) — compression de marges possible"
        )

    if de is not None and de > 2.0:
        result.append(f"Levier financier élevé (D/E {de:.2f}) — risque en cas de hausse des taux")

    if peg is not None and peg > 3.0:
        result.append(f"PEG {peg:.2f} : croissance payée à un prix élevé")

    if fcf is not None and fcf < 0:
        result.append("Free Cash Flow négatif — l'entreprise consomme de la trésorerie")

    return result


# ---------------------------------------------------------------------------
# Verdict synthétique
# ---------------------------------------------------------------------------

def generate_verdict(info: dict, scores: dict, dcf_result: dict, regime: dict) -> str:
    """
    Génère une phrase de verdict synthétique. Premier match dans l'arbre gagne.
    """
    composite   = scores.get("composite", 0)
    mos         = dcf_result.get("margin_of_safety") if dcf_result else None
    peg         = _safe_float(info.get("pegRatio"))
    regime_name = regime.get("regime", "")

    if regime_name == "Hypercroissance":
        if peg is not None and peg < 1.0:
            return (
                "Croissance exceptionnelle avec PEG inférieur à 1 — les multiples élevés sont "
                "justifiés par la dynamique bénéficiaire."
            )
        if peg is not None and peg > 2.0:
            return (
                f"Entreprise en hypercroissance mais PEG à {peg:.1f} — la prime de croissance "
                "est significative et exige une exécution sans faille."
            )
        return (
            "Régime de croissance élevée : la valorisation doit être lue au prisme du PEG "
            "et des perspectives à 3–5 ans."
        )

    if composite >= 65:
        return (
            "Profil attractif sur l'ensemble des critères — valorisation, croissance et qualité "
            "sont alignés favorablement."
        )

    if composite >= 50 and mos is not None and mos > 0:
        return (
            "Valorisation raisonnable confirmée par le DCF — "
            "la génération de cash-flow soutient le prix actuel."
        )

    if composite >= 40 and mos is not None and mos < -0.30:
        return (
            "Multiples élevés par rapport à la valeur intrinsèque DCF — "
            "la thèse repose sur la poursuite de la croissance."
        )

    if composite < 40:
        return (
            "Valorisation tendue — la thèse haussière doit reposer sur "
            "une accélération significative des fondamentaux."
        )

    return (
        "Profil mixte nécessitant une analyse approfondie des catalyseurs "
        "de croissance et de la dynamique sectorielle."
    )
