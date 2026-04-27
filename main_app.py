import streamlit as st
import pandas as pd

st.set_page_config(page_title="LPI Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("cleaned_LPI_data.csv")

# Fix column names
df.columns = df.columns.str.strip()

# Make sure correct column names are used
df = df.rename(columns={
    df.columns[0]: "Country",
    df.columns[1]: "Year",
    df.columns[2]: "LPI_Score"
})

# Clean data
df["Country"] = df["Country"].astype(str).str.strip()
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["LPI_Score"] = pd.to_numeric(df["LPI_Score"], errors="coerce")

df = df.dropna(subset=["Country", "Year", "LPI_Score"])
df["Year"] = df["Year"].astype(int)

# Dashboard title
st.title("Logistics Performance Dashboard")

st.write(
    "This dashboard explores Logistics Performance Index (LPI) scores across countries and years."
)

# Dataset preview
st.subheader("Dataset Preview")
st.dataframe(df.head())

# Year filter
years = sorted(df["Year"].unique())

year = st.selectbox("Select Year", years)

filtered_df = df[df["Year"] == year]

# Top 10 chart
st.subheader(f"Top 10 Countries by LPI Score in {year}")

if not filtered_df.empty:
    top10 = filtered_df.sort_values(by="LPI_Score", ascending=False).head(10)
    st.bar_chart(top10.set_index("Country")["LPI_Score"])
else:
    st.warning("No data available for the selected year.")

# Country comparison
st.subheader("Compare Countries Over Time")

available_countries = sorted(df["Country"].unique())

default_countries = [
    country for country in ["Germany", "Singapore", "Sri Lanka"]
    if country in available_countries
]

countries = st.multiselect(
    "Select Countries",
    available_countries,
    default=default_countries
)

if countries:
    compare_df = df[df["Country"].isin(countries)]

    chart_df = compare_df.pivot_table(
        index="Year",
        columns="Country",
        values="LPI_Score",
        aggfunc="mean"
    )

    st.line_chart(chart_df)
else:
    st.info("Select at least one country to view the comparison chart.")

# Average trend
st.subheader("Average LPI Score Over Time")

trend_df = df.groupby("Year")["LPI_Score"].mean()

if not trend_df.empty:
    st.line_chart(trend_df)
else:
    st.warning("No trend data available.")

# Key insights
st.subheader("Key Insights")

if not filtered_df.empty:
    top_country = filtered_df.sort_values(by="LPI_Score", ascending=False).iloc[0]
    avg_score = filtered_df["LPI_Score"].mean()

    st.write(
        f"Top performing country in {year}: **{top_country['Country']}** "
        f"with score **{top_country['LPI_Score']:.2f}**"
    )

    st.write(
        f"Average LPI score in {year}: **{avg_score:.2f}**"
    )
else:
    st.warning("No data available for the selected year.")