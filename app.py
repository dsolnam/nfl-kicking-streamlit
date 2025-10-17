
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NFL Kicking • Domes vs Outdoors", layout="wide")

st.title("NFL Kicking — Domes vs Outdoors (2015–Present)")
st.caption("Data: nflfastR play-by-play (your CSV exports from Kaggle). Indoor = dome/closed; Outdoor = outdoors/open; FG distance filtered to 17–70 yds.")

with st.sidebar:
    st.header("Load data")
    st.write("Upload the two CSVs you exported from Kaggle:")
    by_roof_file = st.file_uploader("fg_by_roof.csv", type=["csv"])
    distbins_file = st.file_uploader("fg_by_roof_distbins.csv", type=["csv"])
    season_file = st.file_uploader("fg_by_season_roof.csv (optional)", type=["csv"])
    st.markdown("---")
    st.write("Tip: If you don't have the season file, the app still works.")

# Stop until required files are provided
if not (by_roof_file and distbins_file):
    st.info("⬅️ Upload fg_by_roof.csv and fg_by_roof_distbins.csv in the sidebar to begin.")
    st.stop()

# Read the required CSVs
by_roof = pd.read_csv(by_roof_file)
dist_adj = pd.read_csv(distbins_file)

# Optional season file
season_roof = None
if season_file is not None:
    try:
        season_roof = pd.read_csv(season_file)
    except Exception as e:
        st.warning(f"Couldn't read fg_by_season_roof.csv: {e}")

# --- KPI: overall indoor vs outdoor ---
colA, colB, colC = st.columns(3)
try:
    indoor  = float(by_roof.loc[by_roof['roof_norm']=='indoor','fg_pct'])
    outdoor = float(by_roof.loc[by_roof['roof_norm']=='outdoor','fg_pct'])
    delta_pp = (indoor - outdoor) * 100
    colA.metric("FG% • Indoor", f"{indoor:.2%}")
    colB.metric("FG% • Outdoor", f"{outdoor:.2%}")
    colC.metric("Indoor − Outdoor (pp)", f"{delta_pp:.2f}")
except Exception:
    st.warning("Couldn't compute KPIs. Ensure by_roof.csv has columns: roof_norm, fg_pct.")

st.markdown("---")

# --- Chart 1: overall FG% by roof ---
fig1 = px.bar(
    by_roof.sort_values("roof_norm"),
    x="roof_norm", y="fg_pct",
    text=by_roof["fg_pct"].map(lambda v: f"{v:.1%}"),
    labels={"roof_norm":"Roof", "fg_pct":"FG%"},
    title="Field-Goal % by Roof"
)
fig1.update_yaxes(tickformat=".0%")
fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# --- Chart 2: grouped bars by distance bin ---
fig2 = px.bar(
    dist_adj.sort_values(["dist_bin","roof_norm"]),
    x="dist_bin", y="fg_pct", color="roof_norm", barmode="group",
    text=dist_adj["fg_pct"].map(lambda v: f"{v:.1%}"),
    labels={"dist_bin":"Distance (yds)","fg_pct":"FG%","roof_norm":"Roof"},
    title="FG% by Distance Bin & Roof"
)
fig2.update_yaxes(tickformat=".0%")
fig2.update_traces(textposition="outside")
st.plotly_chart(fig2, use_container_width=True)

# --- Optional Chart 3: season trend ---
if season_roof is not None and not season_roof.empty:
    try:
        fig3 = px.line(
            season_roof.sort_values(["season","roof_norm"]),
            x="season", y="fg_pct", color="roof_norm", markers=True,
            hover_data={"attempts":True, "avg_dist":":.1f"},
            labels={"season":"Season","fg_pct":"FG%","roof_norm":"Roof"},
            title="FG% by Season & Roof"
        )
        fig3.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig3, use_container_width=True)
    except Exception as e:
        st.warning(f"Couldn't build season chart: {e}")

# --- Data preview & download helpers ---
with st.expander("Show data tables"):
    st.subheader("by_roof")
    st.dataframe(by_roof)
    st.subheader("dist_adj (by distance bin)")
    st.dataframe(dist_adj)
    if season_roof is not None:
        st.subheader("season_roof")
        st.dataframe(season_roof)

st.markdown("---")
st.markdown("**Notes:** • Upload CSVs generated from your Kaggle notebook. • Consider adding XP analysis or surface (turf vs grass) as future enhancements.")
