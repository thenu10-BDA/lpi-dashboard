import streamlit as st
import pandas as pd

st.set_page_config(page_title="LPI Dashboard", layout="wide")

# Load dataset safely
raw_df = pd.read_csv("cleaned_LPI_data.csv", header=None)

# If CSV is read as one column, split it manually
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

# Dashboard
st.title("Logistics Performance Dashboard")

st.write("This dashboard explores Logistics Performance Index (LPI) scores across countries and years.")

st.subheader("Dataset Preview")
st.dataframe(df.head())

year = st.selectbox("Select Year", sorted(df["Year"].unique()))

filtered_df = df[df["Year"] == year]

st.subheader(f"Top 10 Countries by LPI Score in {year}")

if not filtered_df.empty:
    top10 = filtered_df.sort_values(by="LPI_Score", ascending=False).head(10)
    st.bar_chart(top10.set_index("Country")["LPI_Score"])
else:
    st.warning("No data available for this year.")

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

st.subheader("Average LPI Score Over Time")

trend_df = df.groupby("Year")["LPI_Score"].mean()
st.line_chart(trend_df)

st.subheader("Key Insights")

if not filtered_df.empty:
    top_country = filtered_df.sort_values(by="LPI_Score", ascending=False).iloc[0]
    avg_score = filtered_df["LPI_Score"].mean()

    st.write(
        f"Top performing country in {year}: **{top_country['Country']}** "
        f"with score **{top_country['LPI_Score']:.2f}**"
    )

    st.write(f"Average LPI score in {year}: **{avg_score:.2f}**")
else:
    st.warning("No key insights available for the selected year.")