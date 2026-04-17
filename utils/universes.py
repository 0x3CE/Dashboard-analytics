"""
Listes curatives de tickers par univers boursier.
Chaque liste contient des tickers au format yfinance.
"""

SP500_TOP50 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "BRK-B", "LLY",
    "AVGO", "JPM", "TSLA", "UNH", "V", "XOM", "MA", "JNJ", "PG", "COST",
    "HD", "ABBV", "MRK", "CVX", "BAC", "KO", "NFLX", "CRM", "AMD", "PEP",
    "TMO", "ACN", "ADBE", "WMT", "LIN", "MCD", "CSCO", "ABT", "DHR", "TXN",
    "NEE", "PM", "ORCL", "CAT", "AMGN", "GE", "IBM", "INTC", "QCOM", "UNP",
    "HON",
]

NASDAQ_TOP30 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST",
    "NFLX", "AMD", "ADBE", "QCOM", "INTC", "CSCO", "TXN", "AMAT", "MU",
    "LRCX", "PANW", "KLAC", "MRVL", "SNPS", "CDNS", "ASML", "MELI", "ABNB",
    "TEAM", "ZS", "DDOG",
]

CAC40 = [
    "AI.PA", "AIR.PA", "ALO.PA", "MT.AS", "CS.PA", "BNP.PA", "EN.PA",
    "CAP.PA", "CA.PA", "ACA.PA", "BN.PA", "DSY.PA", "ENGI.PA", "EL.PA",
    "ERF.PA", "RMS.PA", "KER.PA", "OR.PA", "LR.PA", "MC.PA", "ML.PA",
    "ORA.PA", "RI.PA", "PUB.PA", "RNO.PA", "SAF.PA", "SGO.PA", "SAN.PA",
    "SU.PA", "GLE.PA", "STLAM.MI", "STM.PA", "TEP.PA", "HO.PA", "TTE.PA",
    "URW.AS", "VIE.PA", "DG.PA", "WLN.PA", "FR.PA",
]

DAX40 = [
    "ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "BEI.DE",
    "BNR.DE", "CON.DE", "1COV.DE", "DTG.DE", "DB1.DE", "DHL.DE", "DBK.DE",
    "DTE.DE", "EOAN.DE", "FRE.DE", "FME.DE", "HNR1.DE", "HEI.DE", "HEN3.DE",
    "IFX.DE", "LIN.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PAH3.DE",
    "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE", "SHL.DE", "SIE.DE", "SRT.DE",
    "SY1.DE", "VOW3.DE", "VNA.DE", "ZAL.DE", "ENR.DE",
]

FTSE100_TOP30 = [
    "HSBA.L", "SHEL.L", "AZN.L", "ULVR.L", "BP.L", "GSK.L", "RIO.L",
    "BATS.L", "DGE.L", "LSEG.L", "REL.L", "NG.L", "LLOY.L", "BARC.L",
    "GLEN.L", "BT-A.L", "VOD.L", "NWG.L", "IMB.L", "SSE.L", "WPP.L",
    "EXPN.L", "RKT.L", "ABF.L", "PRU.L", "SGRO.L", "TSCO.L", "III.L",
    "CNA.L", "LAND.L",
]

EUROSTOXX50 = [
    "ASML.AS", "SAP.DE", "LVMH.PA", "SIE.DE", "TTE.PA", "NOVO-B.CO",
    "SAN.MC", "INDITEX.MC", "ALV.DE", "AIR.DE", "BNP.PA", "IBE.MC",
    "OR.PA", "ENEL.MI", "MUV2.DE", "BAS.DE", "DTE.DE", "ABI.BR",
    "RMS.PA", "MC.PA", "BAYN.DE", "BBVA.MC", "ING.AS", "CRH.L",
    "ENI.MI", "AD.AS", "SU.PA", "ADS.DE", "UNA.AS", "KER.PA",
    "BMW.DE", "DBK.DE", "PHIA.AS", "CS.PA", "GLE.PA", "HEI.DE",
    "EL.PA", "VIV.PA", "DG.PA", "ENGI.PA", "AXA.PA", "STLAM.MI",
    "VOW3.DE", "MBG.DE", "SOG.PA", "AI.PA", "FLTR.L", "PRX.AS",
    "DSY.PA", "EDF.PA",
]

UNIVERSES = {
    "S&P 500 (Top 50)": SP500_TOP50,
    "Nasdaq (Top 30)": NASDAQ_TOP30,
    "CAC 40": CAC40,
    "DAX 40": DAX40,
    "FTSE 100 (Top 30)": FTSE100_TOP30,
    "Euro Stoxx 50": EUROSTOXX50,
}

ALL_TICKERS = sorted(set(
    SP500_TOP50 + NASDAQ_TOP30 + CAC40 + DAX40 + FTSE100_TOP30 + EUROSTOXX50
))
