import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="LPI Dashboard",
    page_icon="🌍",
    layout="wide"
)


# Load dataset safely

raw_df = pd.read_csv("cleaned_LPI_data.csv", header=None)

if raw_df.shape[1] == 1:
    rows = []

    for value in raw_df[0].astype(str):
        if value.strip() == "Country,Year,LPI_Score":
            continue

        parts = value.rsplit(",", 2)

        if len(parts) == 3:
            rows.append(parts)

    df = pd.DataFrame(rows, columns=["Country", "Year", "LPI_Score"])

else:
    df = pd.read_csv("cleaned_LPI_data.csv")
    df.columns = ["Country", "Year", "LPI_Score"]


# Clean data

df["Country"] = df["Country"].astype(str).str.strip()
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["LPI_Score"] = pd.to_numeric(df["LPI_Score"], errors="coerce")

df = df.dropna()
df["Year"] = df["Year"].astype(int)


# Sidebar filters

st.sidebar.title("Dashboard Filters")

years = sorted(df["Year"].unique())
selected_year = st.sidebar.selectbox("Select Year", years)

available_countries = sorted(df["Country"].unique())

default_countries = [
    country for country in ["Germany", "Singapore", "Sri Lanka"]
    if country in available_countries
]

selected_countries = st.sidebar.multiselect(
    "Select Countries for Comparison",
    available_countries,
    default=default_countries
)

filtered_df = df[df["Year"] == selected_year]


# Dashboard title

st.title("Logistics Performance Index Dashboard")

st.write(
    "This dashboard explores Logistics Performance Index (LPI) scores across countries and years "
    "using World Bank data."
)

# KPI Cards

st.subheader("Dashboard Overview")

if not filtered_df.empty:
    total_countries = filtered_df["Country"].nunique()
    average_score = filtered_df["LPI_Score"].mean()
    highest_score = filtered_df["LPI_Score"].max()
    top_country = filtered_df.sort_values(
        by="LPI_Score",
        ascending=False
    ).iloc[0]["Country"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Selected Year", selected_year)
    col2.metric("Countries", total_countries)
    col3.metric("Average LPI Score", f"{average_score:.2f}")
    col4.metric("Top Country", top_country)
else:
    st.warning("No data available for the selected year.")

st.divider()


# Main charts

left_col, right_col = st.columns(2)

with left_col:
    st.subheader(f"Top 10 Countries in {selected_year}")

    if not filtered_df.empty:
        top10 = filtered_df.sort_values(
            by="LPI_Score",
            ascending=False
        ).head(10)

        st.bar_chart(top10.set_index("Country")["LPI_Score"])
    else:
        st.warning("No top 10 data available.")

with right_col:
    st.subheader("Average LPI Score Over Time")

    trend_df = df.groupby("Year")["LPI_Score"].mean()

    if not trend_df.empty:
        st.line_chart(trend_df)
    else:
        st.warning("No trend data available.")

st.divider()


# Country comparison

st.subheader("Country Comparison Over Time")

if selected_countries:
    compare_df = df[df["Country"].isin(selected_countries)]

    chart_df = compare_df.pivot_table(
        index="Year",
        columns="Country",
        values="LPI_Score",
        aggfunc="mean"
    )

    st.line_chart(chart_df)
else:
    st.info("Select at least one country from the sidebar to view the comparison chart.")

st.divider()


# Key insights

st.subheader("Key Insights")

if not filtered_df.empty:
    top_row = filtered_df.sort_values(
        by="LPI_Score",
        ascending=False
    ).iloc[0]

    avg_score = filtered_df["LPI_Score"].mean()

    st.write(
        f"In **{selected_year}**, the top-performing country was "
        f"**{top_row['Country']}** with an LPI score of **{top_row['LPI_Score']:.2f}**."
    )

    st.write(
        f"The average LPI score across countries in **{selected_year}** was "
        f"**{avg_score:.2f}**."
    )

    st.write(
        "The dashboard allows users to compare selected countries over time and identify "
        "whether logistics performance improved, declined, or remained stable."
    )
else:
    st.warning("No key insights available for the selected year.")


# Dataset preview

with st.expander("View Dataset Preview"):
    st.dataframe(df.head(20))