import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# PAGE CONFIG
st.set_page_config(
page_title="EV Population Dashboard",
layout="wide"
)

# DATABASE CONNECTION
engine = create_engine(
"postgresql://postgres:aisyah456%25@localhost:5432/project_dw_kel3"
)

# LOAD TABLES
fact = pd.read_sql(
"SELECT * FROM fact_ev_population",
engine
)

dim_time = pd.read_sql(
"SELECT * FROM dim_time",
engine
)

dim_location = pd.read_sql(
"SELECT * FROM dim_location",
engine
)

dim_vehicle = pd.read_sql(
"SELECT * FROM dim_vehicle",
engine
)

dim_utility = pd.read_sql(
"SELECT * FROM dim_utility",
engine
)

# JOIN TABLES
df = fact.merge(
dim_time,
on="time_id",
how="left"
)

df = df.merge(
dim_location,
on="location_id",
how="left"
)

df = df.merge(
dim_vehicle,
on="vehicle_id",
how="left"
)

df = df.merge(
dim_utility,
on="utility_id",
how="left"
)

# TITLE
st.title("Electric Vehicle Population Dashboard")

# KPI
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total EV",
        f"{len(df):,}"
    )

with col2:
    st.metric(
        "County",
        df["county"].nunique()
    )

with col3:
    st.metric(
        "Manufacturer",
        df["make"].nunique()
    )

with col4:
    st.metric(
        "Average Range",
        round(
            df["electric_range"].mean(),
            2
        )
    )

# SIDEBAR FILTER
st.sidebar.header("Filter")

selected_year = st.sidebar.multiselect(
    "Model Year",
    sorted(df["model_year"].unique()),
    default=sorted(df["model_year"].unique())
)

selected_type = st.sidebar.multiselect(
"Vehicle Type",
sorted(df["electric_vehicle_type"].unique()),
default=sorted(df["electric_vehicle_type"].unique())
)

filtered = df[
    (df["model_year"].isin(selected_year))
    &
    (df["electric_vehicle_type"].isin(selected_type))
]

# OLAP MENU
st.sidebar.header("OLAP Operation")

olap_mode = st.sidebar.selectbox(
"Select Operation",
[
"Overview",
"Slice",
"Dice",
"Drill Down",
"Roll Up"
]
)

# OVERVIEW
if olap_mode == "Overview":

    st.subheader("Trend EV Growth by Model Year")

    trend = (
        filtered
        .groupby("model_year")
        .size()
        .reset_index(name="total_ev")
    )

    fig, ax = plt.subplots(figsize=(10,5))

    ax.plot(
        trend["model_year"],
        trend["total_ev"]
    )

    ax.set_title("Trend EV Growth")
    ax.set_xlabel("Model Year")
    ax.set_ylabel("Total EV")

    st.pyplot(fig)

    st.subheader("Top 10 Counties")

    county = (
        filtered
        .groupby("county")
        .size()
        .reset_index(name="total_ev")
        .sort_values(
            "total_ev",
            ascending=False
        )
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(10,5))

    ax.bar(
        county["county"],
        county["total_ev"]
    )

    ax.set_title("Top 10 County")
    ax.set_xlabel("County")
    ax.set_ylabel("Total EV")

    plt.xticks(rotation=45)

    st.pyplot(fig)

    st.subheader("Top 10 Manufacturers")

    make = (
        filtered
        .groupby("make")
        .size()
        .reset_index(name="total_ev")
        .sort_values(
            "total_ev",
            ascending=False
        )
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(10,5))

    ax.bar(
        make["make"],
        make["total_ev"]
    )

    ax.set_title("Top Manufacturer")
    ax.set_xlabel("Make")
    ax.set_ylabel("Total EV")

    plt.xticks(rotation=45)

    st.pyplot(fig)

    st.subheader("Vehicle Type Distribution")

    vehicle_type = (
        filtered
        .groupby("electric_vehicle_type")
        .size()
        .reset_index(name="count")
    )

    st.dataframe(
        vehicle_type,
        use_container_width=True
    )

# SLICE
elif olap_mode == "Slice":

    st.subheader("Slice Analysis")

    slice_year = st.selectbox(
        "Choose Model Year",
        sorted(df["model_year"].unique())
    )

    slice_df = df[
        df["model_year"] == slice_year
    ]

    st.metric(
        "Total EV",
        len(slice_df)
    )

    county_slice = (
        slice_df
        .groupby("county")
        .size()
        .reset_index(name="total_ev")
        .sort_values(
            "total_ev",
            ascending=False
        )
    )

    fig, ax = plt.subplots(figsize=(10,5))

    ax.bar(
        county_slice["county"],
        county_slice["total_ev"]
    )

    ax.set_title(
        f"EV Distribution Year {slice_year}"
    )

    ax.set_xlabel("County")
    ax.set_ylabel("Total EV")

    plt.xticks(rotation=45)

    st.pyplot(fig)

    st.dataframe(
        slice_df,
        use_container_width=True
    )
    
# DICE
elif olap_mode == "Dice":

    st.subheader("Dice Analysis")

    dice_year = st.multiselect(
        "Model Year",
        sorted(df["model_year"].unique())
    )

    dice_county = st.multiselect(
        "County",
        sorted(df["county"].dropna().unique())
    )

    dice_type = st.multiselect(
        "Vehicle Type",
        sorted(df["electric_vehicle_type"].unique())
    )

    dice_df = df.copy()

    if dice_year:
        dice_df = dice_df[
            dice_df["model_year"].isin(dice_year)
        ]

    if dice_county:
        dice_df = dice_df[
            dice_df["county"].isin(dice_county)
        ]

    if dice_type:
        dice_df = dice_df[
            dice_df["electric_vehicle_type"].isin(dice_type)
        ]

    st.metric(
        "Total EV",
        len(dice_df)
    )

    st.dataframe(
        dice_df,
        use_container_width=True
    )

# DRILL DOWN
elif olap_mode == "Drill Down":

    st.subheader("Drill Down")

    level = st.selectbox(
        "Location Hierarchy",
        ["state", "county", "city"]
    )

    drill = (
        filtered
        .groupby(level)
        .size()
        .reset_index(name="total_ev")
        .sort_values(
            "total_ev",
            ascending=False
        )
    )

    fig, ax = plt.subplots(figsize=(10,5))

    ax.bar(
        drill[level],
        drill["total_ev"]
    )

    ax.set_title(
        f"Drill Down by {level}"
    )

    ax.set_xlabel(level)
    ax.set_ylabel("Total EV")

    plt.xticks(rotation=45)

    st.pyplot(fig)

    st.dataframe(
        drill,
        use_container_width=True
    )

# ROLL UP
elif olap_mode == "Roll Up":

    st.subheader("Roll Up")

    level = st.selectbox(
        "Aggregation Level",
        ["city", "county", "state"]
    )

    roll = (
        filtered
        .groupby(level)
        .size()
        .reset_index(name="total_ev")
        .sort_values(
            "total_ev",
            ascending=False
        )
    )

    fig, ax = plt.subplots(figsize=(10,5))

    ax.bar(
        roll[level],
        roll["total_ev"]
    )

    ax.set_title(
        f"Roll Up by {level}"
    )

    ax.set_xlabel(level)
    ax.set_ylabel("Total EV")

    plt.xticks(rotation=45)

    st.pyplot(fig)

    st.dataframe(
        roll,
        use_container_width=True
    )

# ELECTRIC RANGE
st.subheader("Average Electric Range by Manufacturer")

range_data = (
    filtered
    .groupby("make")["electric_range"]
    .mean()
    .reset_index()
    .sort_values(
        "electric_range",
        ascending=False
    )
    .head(10)
)

fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(
    range_data["make"],
    range_data["electric_range"]
)

ax.set_title(
    "Average Electric Range by Manufacturer"
)

ax.set_xlabel("Make")
ax.set_ylabel("Electric Range")

plt.xticks(rotation=45)

st.pyplot(fig)

# RAW DATA

with st.expander("View Raw Data"):
    st.dataframe(
        filtered,
        use_container_width=True
    )