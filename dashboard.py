import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ------------------ Page ------------------
st.set_page_config(
    page_title="NovaMart Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("NovaMart Dashboard - Havvah Zulfa")

# ------------------ Load Data ------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/novamart_clean.csv")

orders = load_data()

# ------------------ Sidebar ------------------
st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Select Region",
    sorted(orders["region"].dropna().unique()),
    default=sorted(orders["region"].dropna().unique())
)

month = st.sidebar.multiselect(
    "Select Month",
    sorted(orders["order_month"].dropna().unique()),
    default=sorted(orders["order_month"].dropna().unique())
)

# ------------------ Filter ------------------
filtered_data = orders[
    (orders["region"].isin(region)) &
    (orders["order_month"].isin(month))
]
filtered_data = orders.copy()
# ------------------ KPI ------------------
total_sales = filtered_data["sales"].sum()
total_profit = filtered_data["profit"].sum()
regions = filtered_data["region"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Regions Covered", regions)

# ------------------ Sales by Region ------------------
st.subheader("Sales by Region")

sales_region = filtered_data.groupby("region")["sales"].sum()

st.bar_chart(sales_region)

# ------------------ Monthly Sales Trend ------------------
st.subheader("Monthly Sales Trend")

monthly = filtered_data.groupby(
    ["order_month", "region"]
)["sales"].sum().reset_index()

fig = px.line(
    monthly,
    x="order_month",
    y="sales",
    color="region",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# ------------------ Area Chart ------------------
st.subheader("Cumulative Sales")

area = filtered_data.groupby("order_month")["sales"].sum()

st.area_chart(area)

# ------------------ Pivot Table ------------------
st.subheader("Region × Category Sales")

pivot = pd.pivot_table(
    filtered_data,
    values="sales",
    index="region",
    columns="category_y",
    aggfunc="sum"
)

st.dataframe(pivot)

# ------------------ Growth Alert ------------------
st.subheader("Growth Alert")

growth = filtered_data.groupby(
    ["region", "order_month"]
)["sales"].sum().reset_index()

growth["Growth"] = growth.groupby("region")["sales"].pct_change() * 100

if (growth["Growth"] < 0).any():
    st.warning("Sales dropped in one or more regions.")
else:
    st.success("No sales drop detected.")

# ------------------ Download ------------------
csv = filtered_data.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Data",
    csv,
    "Filtered_Data.csv",
    "text/csv"
)