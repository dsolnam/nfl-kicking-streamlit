
# NFL Kicking — Domes vs Outdoors (Streamlit)

A lightweight Streamlit dashboard that visualizes field-goal performance indoors vs outdoors using CSVs exported from a Kaggle notebook (nflfastR data).

## Quick start (local)
1. `pip install -r requirements.txt`
2. `streamlit run app.py`
3. Upload `fg_by_roof.csv` and `fg_by_roof_distbins.csv` (and optional `fg_by_season_roof.csv`) via the sidebar.

## Deploy on Streamlit Community Cloud (free)
1. Push this folder to a public GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your repo, select `app.py` as the entry point.
3. Deploy — you'll get a public URL.
4. Use the sidebar to upload your CSVs from Kaggle each time you run the app. (Or commit them to the repo if you want them preloaded.)

## Expected CSV schemas

### fg_by_roof.csv
- `roof_norm` (indoor/outdoor)
- `attempts`, `makes`, `avg_dist` (optional for chart)
- `fg_pct` (0–1 float)

### fg_by_roof_distbins.csv
- `roof_norm` (indoor/outdoor)
- `dist_bin` (`<30`, `30-39`, `40-49`, `50+` or similar)
- `fg_pct` (0–1 float)

### fg_by_season_roof.csv (optional)
- `season`, `roof_norm`, `fg_pct`, `attempts`, `avg_dist`

## Portfolio blurb (copy/paste)
> Built an end-to-end analysis of NFL field-goal performance using nflfastR (2015–2024). Cleaned play-by-play data in Kaggle, normalized roof status, and quantified an indoor edge primarily on 40+ yard attempts. Published a Streamlit dashboard (Plotly charts) and Datawrapper links for quick sharing; code and data are reproducible via Kaggle + GitHub.

## Ideas for future enhancements
- Add XP (extra point) analysis
- Filter by season/team/kicker
- Compare grass vs turf
- Add logistic regression and confidence intervals
