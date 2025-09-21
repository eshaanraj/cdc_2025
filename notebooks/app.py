import os
import glob
import streamlit as st
import pandas as pd
#AI assisted with setting up streamlit webapp
st.set_page_config(page_title="Industry Trends Explorer", layout="wide")

st.title("📈 Industry Trends Explorer")
st.caption("Upload an Excel in **wide** format: `Industry, 2012, 2013, ..., 2023, ...`. Then pick industries to visualize.")

# ---------------------------
# Helpers
# ---------------------------
@st.cache_data(show_spinner=False)
def load_wide_excel(file):
    df = pd.read_excel(file, sheet_name=0)

    # Normalize the Industry column name
    obj_cols = [c for c in df.columns if df[c].dtype == "O"]
    industry_col = obj_cols[0] if obj_cols else df.columns[0]
    if industry_col != "Industry":
        df = df.rename(columns={industry_col: "Industry"})

    # Identify year columns (string or int)
    year_cols = [c for c in df.columns if str(c).isdigit()]
    if not year_cols:
        raise ValueError("No year columns found. Ensure your sheet has columns like 2018, 2019, 2020, ...")

    # Ensure numeric for year columns
    for c in year_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Keep only Industry + years
    return df[["Industry"] + year_cols]

# ---------------------------
# Data source selection
# ---------------------------
uploaded = st.file_uploader(
    "Upload Excel (wide format)",
    type=["xlsx", "xls"],
    help="Prefer this in Colab. If omitted, the app will try to find a local .xlsx like plain_format_extended.xlsx",
)

df_wide = None
source_msg = ""

if uploaded is not None:
    df_wide = load_wide_excel(uploaded)
    source_msg = "Using uploaded file."
else:
    # Look for a local Excel file in current working dir
    candidates = []
    if os.path.exists("plain_format_extended.xlsx"):
        candidates = ["plain_format_extended.xlsx"]
    else:
        candidates = sorted(glob.glob("*.xlsx"))

    if candidates:
        try:
            df_wide = load_wide_excel(candidates[0])
            source_msg = f"Using local file: {candidates[0]}"
        except Exception as e:
            st.error(f"Found a local Excel file but failed to load: {candidates[0]}\n{e}")
            st.stop()
    else:
        st.info("Please upload an Excel file to proceed.")
        st.stop()

st.success(source_msg)

# ---------------------------
# Controls
# ---------------------------
all_industries = sorted(df_wide["Industry"].dropna().unique().tolist())
default_selection = all_industries[:5] if len(all_industries) > 0 else []

selected_industries = st.multiselect(
    "Select one or more industries",
    options=all_industries,
    default=default_selection,
    help="Choose industries to plot",
)

# Year range slider based on actual columns present (string or int)
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
# Prepare long data (robust to int/str headers & missing years)
# ---------------------------
# Keep only years within the chosen range that actually exist
value_years = [y for y in present_year_ints if year_min <= y <= year_max]

# Build exact column labels as they exist in df_wide
value_cols_existing = []
for y in value_years:
    if y in df_wide.columns:
        value_cols_existing.append(y)
    elif str(y) in df_wide.columns:
        value_cols_existing.append(str(y))

if not value_cols_existing:
    st.warning("No columns found in the selected year range.")
    st.stop()

# Subset safely with only existing columns
df_subset = df_wide[["Industry"] + value_cols_existing].copy()

# Melt to long (convert year-like cols to strings first)
df_subset.columns = ["Industry"] + [str(c) for c in df_subset.columns[1:]]
df_long = df_subset.melt(id_vars="Industry", var_name="Year", value_name="Value")
df_long["Year"] = pd.to_numeric(df_long["Year"], errors="coerce")

# Filter by selected industries if any
if selected_industries:
    df_plot = df_long[df_long["Industry"].isin(selected_industries)].dropna(subset=["Value"])
else:
    df_plot = df_long.dropna(subset=["Value"])

# ---------------------------
# Output
# ---------------------------
with st.expander("Preview data (filtered)"):
    st.dataframe(
        df_plot.sort_values(["Industry", "Year"]).reset_index(drop=True),
        use_container_width=True,
    )

st.markdown("### Trend")
st.line_chart(
    df_plot.pivot_table(index="Year", columns="Industry", values="Value", aggfunc="mean").sort_index()
)

st.caption("Tip: Upload your Excel in Colab (left sidebar > Files) or use the uploader above.")
