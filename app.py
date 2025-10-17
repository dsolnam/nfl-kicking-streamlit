
import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NFL Kicking • Domes vs Outdoors", layout="wide")

st.title("NFL Kicking — Domes vs Outdoors (2015–2019)")
st.caption("Data: CSVs exported from your Kaggle notebook (nflfastR). Indoor = dome/closed; Outdoor = outdoors/open. FG distance filtered to 17–70 yds in preprocessing.")

# ---------- Data loading: prefer repo files, fall back to uploads ----------
def load_from_repo():
    required = ["fg_by_roof.csv", "fg_by_roof_distbins.csv"]
    if not all(os.path.exists(p) for p in required):
        return None, None, None
    by_roof = pd.read_csv("fg_by_roof.csv")
    dist_adj = pd.read_csv("fg_by_roof_distbins.csv")
    season_roof = pd.read_csv("fg_by_season_roof.csv") if os.path.exists("fg_by_season_roof.csv") else None
    return by_roof, dist_adj, season_roof

by_roof, dist_adj, season_roof = load_from_repo()

if by_roof is None or dist_adj is None:
    with st.sidebar:
        st.header("Load data")
        st.write("Upload the CSVs if they aren't committed in the repo:")
        by_roof_file = st.file_uploader("fg_by_roof.csv", type=["csv"])
        distbins_file = st.file_uploader("fg_by_roof_distbins.csv", type=["csv"])
        season_file = st.file_uploader("fg_by_season_roof.csv (optional)", type=["csv"])
    if not (by_roof_file and distbins_file):
        st.info("⬅️ Upload fg_by_roof.csv and fg_by_roof_distbins.csv in the sidebar to begin.")
        st.stop()
    by_roof = pd.read_csv(by_roof_file)
    dist_adj = pd.read_csv(distbins_file)
    season_roof = pd.read_csv(season_file) if season_file else None

# ---------- Sidebar controls ----------
with st.sidebar:
    st.header("Filters")
    roof_options = ["indoor", "outdoor"]
    selected_roofs = st.multiselect("Roof types", roof_options, default=roof_options)
    show_overall = st.checkbox("Show Overall FG% by Roof", value=True)
    show_bins    = st.checkbox("Show FG% by Distance Bin", value=True)
    show_season  = st.checkbox("Show Season Trend (if available)", value=True)
    # Season filter only if season_roof provided
    season_selection = None
    if season_roof is not None and not season_roof.empty and "season" in season_roof.columns:
        smin, smax = int(season_roof["season"].min()), int(season_roof["season"].max())
        season_selection = st.slider("Season range", min_value=smin, max_value=smax, value=(smin, smax), step=1)

# ---------- Helper: weighted overall from season_roof when filtering ----------
def weighted_overall(season_df, roofs, season_range):
    df = season_df.copy()
    if season_range is not None:
        lo, hi = season_range
        df = df[(df["season"] >= lo) & (df["season"] <= hi)]
    if roofs:
        df = df[df["roof_norm"].isin(roofs)]
    # If attempts present, compute weighted average; otherwise simple mean
    if "attempts" in df.columns:
        out = (df.groupby("roof_norm")
                 .apply(lambda g: (g["fg_pct"] * g["attempts"]).sum() / max(g["attempts"].sum(), 1))
                 .reset_index(name="fg_pct"))
    else:
        out = df.groupby("roof_norm")["fg_pct"].mean().reset_index()
    # Add placeholders for compatibility
    out["attempts"] = pd.NA
    out["makes"] = pd.NA
    out["avg_dist"] = pd.NA
    return out

# ---------- Build KPI data (overall per roof) ----------
if season_roof is not None and season_selection is not None:
    overall_df = weighted_overall(season_roof, selected_roofs, season_selection)
else:
    overall_df = by_roof.copy()
    if selected_roofs:
        overall_df = overall_df[overall_df["roof_norm"].isin(selected_roofs)]

# KPIs: Indoor / Outdoor FG% and delta
colA, colB, colC = st.columns(3)
try:
    indoor  = float(overall_df.loc[overall_df["roof_norm"]=="indoor","fg_pct"].iloc[0]) if "indoor" in overall_df["roof_norm"].values else None
    outdoor = float(overall_df.loc[overall_df["roof_norm"]=="outdoor","fg_pct"].iloc[0]) if "outdoor" in overall_df["roof_norm"].values else None
    if indoor is not None: colA.metric("FG% • Indoor", f"{indoor:.2%}")
    if outdoor is not None: colB.metric("FG% • Outdoor", f"{outdoor:.2%}")
    if indoor is not None and outdoor is not None:
        colC.metric("Indoor − Outdoor (pp)", f"{(indoor - outdoor)*100:.2f}")
except Exception as e:
    st.warning(f"Couldn't compute KPIs: {e}")

# Secondary KPIs: 40–49 and 50+ deltas from dist_adj (not season-filtered)
def bin_delta(df, bin_label):
    sub = df[df["dist_bin"] == bin_label]
    try:
        ind = float(sub.loc[sub["roof_norm"]=="indoor","fg_pct"])
        out = float(sub.loc[sub["roof_norm"]=="outdoor","fg_pct"])
        return (ind - out) * 100
    except Exception:
        return None

colD, colE = st.columns(2)
delta_40_49 = bin_delta(dist_adj, "40-49")
delta_50p   = bin_delta(dist_adj, "50+")
if delta_40_49 is not None:
    colD.metric("Δ pp (Indoor − Outdoor) • 40–49 yds", f"{delta_40_49:.2f}")
if delta_50p is not None:
    colE.metric("Δ pp (Indoor − Outdoor) • 50+ yds", f"{delta_50p:.2f}")

st.markdown("---")

# ---------- Charts ----------
if show_overall:
    fig1_df = overall_df.sort_values("roof_norm")
    fig1 = px.bar(
        fig1_df, x="roof_norm", y="fg_pct",
        text=fig1_df["fg_pct"].map(lambda v: f"{v:.1%}"),
        labels={"roof_norm":"Roof", "fg_pct":"FG%"},
        title="Field-Goal % by Roof" + (f" — Seasons {season_selection[0]}–{season_selection[1]}" if season_roof is not None and season_selection is not None else "")
    )
    fig1.update_yaxes(tickformat=".0%")
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)

if show_bins:
    bins_df = dist_adj.copy()
    if selected_roofs:
        bins_df = bins_df[bins_df["roof_norm"].isin(selected_roofs)]
    fig2 = px.bar(
        bins_df.sort_values(["dist_bin","roof_norm"]),
        x="dist_bin", y="fg_pct", color="roof_norm", barmode="group",
        text=bins_df["fg_pct"].map(lambda v: f"{v:.1%}"),
        labels={"dist_bin":"Distance (yds)","fg_pct":"FG%","roof_norm":"Roof"},
        title="FG% by Distance Bin & Roof (overall)"
    )
    fig2.update_yaxes(tickformat=".0%")
    fig2.update_traces(textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)

if show_season and season_roof is not None and not season_roof.empty:
    sdf = season_roof.copy()
    if selected_roofs:
        sdf = sdf[sdf["roof_norm"].isin(selected_roofs)]
    if season_selection is not None:
        lo, hi = season_selection
        sdf = sdf[(sdf["season"] >= lo) & (sdf["season"] <= hi)]
    fig3 = px.line(
        sdf.sort_values(["season","roof_norm"]),
        x="season", y="fg_pct", color="roof_norm", markers=True,
        hover_data={"attempts":True, "avg_dist":":.1f"} if set(["attempts","avg_dist"]).issubset(sdf.columns) else None,
        labels={"season":"Season","fg_pct":"FG%","roof_norm":"Roof"},
        title="FG% by Season & Roof"
    )
    fig3.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig3, use_container_width=True)

# ---------- Data expander ----------
with st.expander("Show data tables"):
    st.subheader("Overall (by_roof / weighted by season range)")
    st.dataframe(overall_df)
    st.subheader("Distance bins (dist_adj)")
    st.dataframe(dist_adj if not selected_roofs else dist_adj[dist_adj["roof_norm"].isin(selected_roofs)])
    if season_roof is not None:
        st.subheader("Season-level (season_roof)")
        st.dataframe(season_roof)

st.caption("Tip: Add XP analysis, surface (turf vs grass), or a logistic regression in your Kaggle notebook and export new CSVs to extend this app.")
