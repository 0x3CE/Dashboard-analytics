"""
Persistance de la watchlist sur disque (JSON).
Le fichier est créé automatiquement à côté du projet.
"""

import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "..", "watchlist.json")
_PATH = os.path.normpath(_PATH)


def load() -> list[str]:
    """Charge la watchlist depuis le fichier. Retourne [] si absent."""
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(t) for t in data]
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def save(tickers: list[str]) -> None:
    """Écrit la watchlist sur disque."""
    with open(_PATH, "w", encoding="utf-8") as f:
        json.dump(tickers, f, ensure_ascii=False, indent=2)


def init_session_state() -> None:
    """
    À appeler au début de chaque page.
    Charge depuis le fichier la première fois dans la session,
    ne touche plus à session_state ensuite.
    """
    import streamlit as st
    if "watchlist" not in st.session_state:
        st.session_state["watchlist"] = load()


def add(ticker: str) -> bool:
    """Ajoute un ticker. Retourne True si ajouté, False si déjà présent."""
    import streamlit as st
    ticker = ticker.strip().upper()
    if not ticker or ticker in st.session_state["watchlist"]:
        return False
    st.session_state["watchlist"].append(ticker)
    save(st.session_state["watchlist"])
    return True


def remove(ticker: str) -> None:
    """Supprime un ticker et sauvegarde."""
    import streamlit as st
    if ticker in st.session_state["watchlist"]:
        st.session_state["watchlist"].remove(ticker)
        save(st.session_state["watchlist"])
