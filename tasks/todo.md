# Dashboard Financier — Todo & État du projet

## État actuel

Le code est **complet et fonctionnel**. L'app tourne avec :
```bash
source venv/bin/activate
python -m streamlit run app.py
# → http://localhost:8501
```

> ⚠️ Utiliser `python -m streamlit` et PAS `streamlit` directement.

---

## Ce qui a été fait ✅

### Infrastructure de base
- [x] `utils/data.py` — wrappers yfinance + cache 1h
- [x] `utils/universes.py` — 6 univers (SP500, CAC40, DAX40, FTSE, Nasdaq, EuroStoxx)
- [x] `utils/ratios.py` — scoring 0-100 par ratio (avec PE growth-adjusted)
- [x] `utils/scoring.py` — score composite + détection divergences
- [x] `utils/formatting.py` — formatage nombres/devises/%, correction GBp→GBP
- [x] `app.py` — page d'accueil + watchlist session_state
- [x] `pages/1_Screener.py` — scan parallèle, filtres, export CSV
- [x] `pages/2_Analyse_Entreprise.py` — deep-dive 6 onglets + jauge valorisation
- [x] `pages/3_Consensus_Analystes.py` — targets, breakdown recos, upgrades/downgrades
- [x] `pages/4_Score_Composite.py` — classement + scatter plot + divergences

### Nouveau scoring (session du 2026-04-22)
- [x] `utils/sector_benchmarks.py` — médianes Damodaran 2025 pour 11 secteurs GICS
- [x] `utils/dcf.py` — DCF 2 stages + Gordon Growth Model + 3 scénarios (bull/base/bear)
- [x] Score composite revu : Valorisation(35) + DCF(20) + Croissance(15) + Analystes(20) + Qualité(10)
- [x] PE growth-adjusted : bornes dynamiques selon earningsGrowth
- [x] Scoring sectoriel : blend 60% vs médiane secteur + 40% absolu

### Analyse contextuelle (session du 2026-04-22)
- [x] `utils/analysis.py` — moteur rule-based : régime croissance, forces, risques, verdict
- [x] Section "🧠 Analyse contextuelle" sur page 2 (visible avant les onglets)
- [x] Régimes : Hypercroissance / Croissance forte / Croissance modérée / Mature / Déclin
- [x] Points forts + Points de vigilance générés automatiquement
- [x] Verdict contextuel selon régime + composite + DCF
- [x] Tab 6 "🎯 Valorisation Intrinsèque" : DCF détaillé + 3 scénarios côte à côte

---

## Résultats scoring NVDA / MSFT / AAPL (avril 2026)

| Ticker | Composite | Régime | Verdict |
|---|---|---|---|
| NVDA | 50.9/100 | 🚀 Hypercroissance | PEG < 1, multiples justifiés |
| MSFT | 73.3/100 | 🚀 Hypercroissance | DCF MoS +39%, très attractif |
| AAPL | 39.1/100 | 📈 Croissance forte | Valorisation tendue |

---

## À tester (reprendre ici)

- [ ] Page 2 avec `AAPL` (vérifier section contextuelle)
- [ ] Page 2 avec `OR.PA` (Europe — DCF Faible attendu, pas d'earningsGrowth)
- [ ] Page 2 avec `SAP.DE` (Xetra)
- [ ] Page 2 avec `HSBA.L` (LSE — vérifier correction pence GBp)
- [ ] Page 1 : screener CAC40 avec PE max = 20
- [ ] Page 3 : consensus `AAPL`
- [ ] Page 4 : score composite sur 10 tickers mixtes (vérifier colonnes DCF + Croissance)
- [ ] Ticker invalide `XXXXXX` → ne doit pas crasher

---

## Améliorations v2

### Priorité haute
- [ ] **API Claude** : remplacer le moteur rule-based par un appel Claude pour une analyse vraiment nuancée (contexte macro, historique, actualité)
- [ ] **Comparaison peer-to-peer** : 2-5 entreprises côte à côte
- [ ] **Alertes watchlist** : ratio passe sous un seuil → notification

### Priorité moyenne
- [ ] **DCF amélioré** : structure du capital (dette/equity) dans le WACC au lieu de l'approximation beta seule
- [ ] **Backtesting simple** : perf du screener sur 1 an
- [ ] **Comparaison sectorielle dynamique** : charger les peers en temps réel plutôt que médianes statiques
- [ ] **Export PDF** d'une fiche entreprise

### Priorité basse
- [ ] **DCF scénarios sensibilité** : tableau WACC × taux croissance
- [ ] **Prometheus metrics** / export Grafana
- [ ] **Flux news + sentiment**

---

## Notes techniques

- `utils/analysis.py` : moteur rule-based pur Python, aucun appel API
- `utils/dcf.py` : `compute_dcf()` + `compute_dcf_scenarios()`, FCF-based (limité pour hypercroissances)
- `utils/sector_benchmarks.py` : médianes statiques Damodaran Jan 2025 — à mettre à jour annuellement
- Le D/E de AAPL/MSFT paraît très élevé (buybacks réduisent les fonds propres) — c'est exact mais trompeur, à documenter dans l'interface
