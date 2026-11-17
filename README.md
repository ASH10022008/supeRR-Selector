# supeRR-Selector

Streamlit dashboard ranking Rajasthan Royals players by performance in high-pressure deliveries.

## Run and deploy

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on [Streamlit Community Cloud](https://share.streamlit.io) using branch `main` and entry file `streamlit_app.py`. Rankings read `data/processed_ball_by_ball.csv`.

## Method

**High pressure:** death overs (overs 16–20) **or** a collapse (5+ wickets down by over 15).

**Eligibility:** at least 30 normal deliveries and 20 high-pressure deliveries.

Let `N` be normal deliveries, `P` high-pressure deliveries, `R` runs, and `W` wickets taken on pressure deliveries.

- Batter strike rate: `SR = 100 × R / deliveries`
- Bowler economy: `Econ = 6 × R / deliveries`
- League pressure benchmarks: `league_SR = 100 × total pressure runs / P`; `league_Econ = 6 × total pressure runs / P`
- Batter impact: `(pressure_SR − league_SR) + 0.2 × (pressure_SR − normal_SR)`
- Bowler impact: `15 × (league_Econ − pressure_Econ) + 3 × (normal_Econ − pressure_Econ) + 360 × W / P`
- Final clutch score (both roles): `impact × ln(1 + P) × ln(1 + pressure_matches) × avg_stakes × avg_recency`

**Weights:** stakes multipliers are Final 2.5, Semi 1.9, Qualifier 1.8, Eliminator 1.7, Super4 1.5, League 1.2, and other/unknown 1.0. Recency weight is `e^(−0.35 × years_ago)`, where `years_ago` is measured from the latest dataset date using 365.25 days per year. Stakes and recency are averaged over pressure deliveries.
