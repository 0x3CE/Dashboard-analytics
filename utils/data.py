"""
Wrappers yfinance avec mise en cache Streamlit (TTL 1h).
Toutes les fonctions retournent None / dict vide / DataFrame vide en cas d'erreur.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=3600, show_spinner=False)
def get_ticker_info(symbol: str) -> dict:
    """Retourne ticker.info (dict) pour un symbole. Dict vide si erreur."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info or len(info) <= 1:
            return {}
        return info
    except Exception:
        return {}


@st.cache_data(ttl=3600, show_spinner=False)
def get_ticker_history(symbol: str, period: str = "5y") -> pd.DataFrame:
    """Retourne l'historique de prix OHLCV. DataFrame vide si erreur."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        return hist if hist is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_income_stmt(symbol: str) -> pd.DataFrame:
    """Compte de résultat annuel. Colonnes = dates, index = items."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.income_stmt
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_balance_sheet(symbol: str) -> pd.DataFrame:
    """Bilan annuel."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.balance_sheet
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_cash_flow(symbol: str) -> pd.DataFrame:
    """Flux de trésorerie annuel."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.cash_flow
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_recommendations(symbol: str) -> pd.DataFrame:
    """Historique des recommandations analystes."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.recommendations
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_upgrades_downgrades(symbol: str) -> pd.DataFrame:
    """Historique des upgrades/downgrades récents."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.upgrades_downgrades
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_analyst_targets(symbol: str) -> dict:
    """Price targets analystes (low/mean/median/high/current)."""
    try:
        ticker = yf.Ticker(symbol)
        targets = ticker.analyst_price_targets
        if targets is None:
            return {}
        if isinstance(targets, dict):
            return targets
        # Certaines versions retournent un DataFrame
        if isinstance(targets, pd.DataFrame) and not targets.empty:
            return targets.iloc[0].to_dict()
        return {}
    except Exception:
        return {}


@st.cache_data(ttl=3600, show_spinner=False)
def get_earnings_trend(symbol: str) -> pd.DataFrame:
    """Estimations de résultats (earnings trend)."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.earnings_trend
        return df if df is not None and not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _fetch_single(symbol: str) -> tuple[str, dict]:
    """Fetch info pour un ticker (utilisé dans le parallélisme)."""
    time.sleep(0.05)  # éviter le rate limiting
    info = get_ticker_info(symbol)
    return symbol, info


def get_universe_data(
    tickers: list[str],
    max_workers: int = 5,
    progress_callback=None,
) -> dict[str, dict]:
    """
    Charge les données pour une liste de tickers en parallèle.
    progress_callback(i, total) est appelé après chaque ticker complété.
    Retourne {symbol: info_dict}.
    """
    results = {}
    total = len(tickers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_fetch_single, t): t for t in tickers}
        for i, future in enumerate(as_completed(futures), start=1):
            symbol, info = future.result()
            results[symbol] = info
            if progress_callback:
                progress_callback(i, total)

    return results
