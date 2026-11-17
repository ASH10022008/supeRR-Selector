# supeRR-Selector

A Streamlit dashboard for exploring Rajasthan Royals clutch-performance rankings, pressure metrics, and player comparisons.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app reads the processed delivery dataset from `data/processed_ball_by_ball.csv`.

## Deploy on Streamlit Community Cloud

1. Push this repository and the branch you want to deploy to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io), choose **New app**.
3. Select `ASH10022008/supeRR-Selector`, branch `main`, and main file `streamlit_app.py`.
4. Deploy. Streamlit installs the packages listed in the root `requirements.txt`.

If the repository is not available in the picker, sign in with the GitHub account that can access it and authorize Streamlit Community Cloud to access the repository.

## Project files

- `streamlit_app.py` — dashboard entry point.
- `pressure_engine.py` — computes player metrics and rankings.
- `preprocessing.py` — preprocessing utility for the source CSV files.
- `data/` — source and processed CSV datasets.
