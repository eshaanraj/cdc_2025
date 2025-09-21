import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Industry Trends Explorer", layout="wide")

st.title("📈 Industry Trends Explorer")
st.caption("Visualize industry values over time from plain_format_extended.xlsx")

# ---------------------------
# Load Excel (always from plain_format_extended.xlsx)
# ---------------------------
DATA_PATH = "plain_format_extended.xlsx"

if not os.path.exists(DATA_PATH):
    st.error(f"Could not find {DATA_PATH} in the current directory.")
    st.stop()

@st.cache_data(show_spinner=False)
def load_wide_excel(path):
    df = pd.read_excel(path, sheet_name=0)

    # Normalize the Industry column name
    obj_cols = [c for c in df.columns if df[c].dtype == "O"]
    industry_col = obj_cols[0] if obj_cols else df.columns[0]
    if industry_col != "Industry":
        df = df.rename(columns={industry_col: "Industry"})

    # Identify year columns (string or int)
    year_cols = [c for c in df.columns if str(c).isdigit()]
    if not year_cols:
        raise ValueError("No year columns found in the file.")
    # Ensure numeric
    for c in year_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df[["Industry"] + year_cols]

df_wide = load_wide_excel(DATA_PATH)
st.success(f"Loaded data from {DATA_PATH}")

# ---------------------------
# Controls
# ---------------------------
all_industries = sorted(df_wide["Industry"].dropna().unique().tolist())
default_selection = all_industries[:5] if len(all_industries) > 0 else []

selected_industries = st.multiselect(
    "Select one or more industries",
    options=all_industries,
    default=default_selection,
)

# Year range slider
present_year_cols = [c for c in df_wide.columns if str(c).isdigit()]
present_year_ints = sorted(int(str(c)) for c in present_year_cols)
if present_year_ints:
    year_min, year_max = st.slider(
        "Year range",
        min_value=min(present_year_ints),
        max_value=max(present_year_ints),
        value=(min(present_year_ints), max(present_year_ints)),
        step=1,
    )
else:
    st.warning("No year columns found.")
    st.stop()

# ---------------------------
# Prepare long data
# ---------------------------
value_years = [y for y in present_year_ints if year_min <= y <= year_max]

# Match existing columns (int or str)
value_cols_existing = []
for y in value_years:
    if y in df_wide.columns:
        value_cols_existing.append(y)
    elif str(y) in df_wide.columns:
        value_cols_existing.append(str(y))

df_subset = df_wide[["Industry"] + value_cols_existing].copy()
df_subset.columns = ["Industry"] + [str(c) for c in df_subset.columns[1:]]
df_long = df_subset.melt(id_vars="Industry", var_name="Year", value_name="Value")
df_long["Year"] = pd.to_numeric(df_long["Year"], errors="coerce")

if selected_industries:
    df_plot = df_long[df_long["Industry"].isin(selected_industries)].dropna(subset=["Value"])
else:
    df_plot = df_long.dropna(subset=["Value"])

# ---------------------------
# Output
# ---------------------------
with st.expander("Preview data (filtered)"):
    st.dataframe(df_plot.sort_values(["Industry", "Year"]).reset_index(drop=True), use_container_width=True)

st.markdown("### Trend")
st.line_chart(
    df_plot.pivot_table(index="Year", columns="Industry", values="Value", aggfunc="mean").sort_index()
)
