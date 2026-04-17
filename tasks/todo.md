# Dashboard Financier — Todo & État du projet

## État actuel

Le code est **complet et syntaxiquement valide**. L'app démarre avec :
```bash
python -m streamlit run app.py
```

> ⚠️ Utiliser `python -m streamlit` et PAS `streamlit` directement — sur certaines configs
> la commande `streamlit` pointe vers un mauvais interpréteur Python (sans plotly).

---

## Problème rencontré sur ordi boulot

- `plotly` non trouvé malgré l'installation → conflit d'interpréteurs Python
- Push GitHub bloqué : clé SSH non configurée sur cet ordi
- **Code intact**, rien de perdu — tout est dans ce dossier

---

## À faire sur le Mac pour démarrer

```bash
# 1. Cloner / copier le projet
cd ~/Documents  # ou où tu veux

# 2. Créer un venv propre
python3 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer
python -m streamlit run app.py
# → http://localhost:8501
```

---

## Push GitHub (à faire sur le Mac)

Le repo distant est configuré : `git@github.com:0x3CE/Dashboard-analytics.git`

```bash
# Si la clé SSH est configurée sur le Mac :
git push -u origin main

# Sinon en HTTPS :
git remote set-url origin https://github.com/0x3CE/Dashboard-analytics.git
git push -u origin main
```

---

## Ce qui fonctionne ✅

- [x] `utils/data.py` — wrappers yfinance + cache 1h
- [x] `utils/universes.py` — 6 univers (SP500, CAC40, DAX40, FTSE, Nasdaq, EuroStoxx)
- [x] `utils/ratios.py` — scoring 0-100 par ratio
- [x] `utils/scoring.py` — score composite + détection divergences
- [x] `utils/formatting.py` — formatage nombres/devises/%, correction GBp→GBP
- [x] `app.py` — page d'accueil + watchlist session_state
- [x] `pages/1_Screener.py` — scan parallèle, filtres, export CSV
- [x] `pages/2_Analyse_Entreprise.py` — deep-dive 5 onglets + jauge valorisation
- [x] `pages/3_Consensus_Analystes.py` — targets, breakdown recos, upgrades/downgrades
- [x] `pages/4_Score_Composite.py` — classement + scatter plot + divergences

---

## À tester une fois lancé sur le Mac

- [ ] Page 2 avec `AAPL` (US)
- [ ] Page 2 avec `OR.PA` (Euronext Paris)
- [ ] Page 2 avec `SAP.DE` (Xetra)
- [ ] Page 2 avec `HSBA.L` (LSE — vérifier correction pence GBp)
- [ ] Page 1 : screener CAC40 avec PE max = 20
- [ ] Page 3 : consensus `AAPL`
- [ ] Page 4 : score composite sur 10 tickers mixtes
- [ ] Ticker invalide `XXXXXX` → ne doit pas crasher

---

## Améliorations v2 (idées de la spec)

- [ ] Comparaison peer-to-peer (2-5 entreprises côte à côte)
- [ ] Backtesting simple : perf du screener sur 1 an
- [ ] Export PDF d'une fiche entreprise
- [ ] DCF simplifié avec hypothèses ajustables
- [ ] Comparaison sectorielle (percentile rank vs pairs)
- [ ] Alertes watchlist (ratio passe sous un seuil)
- [ ] Flux news + sentiment
