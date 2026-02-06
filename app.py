import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(
    page_title="E-Commerce Funnel & Conversion Analytics",
    layout="wide"
)

st.title("🛒 E-Commerce Funnel & Conversion Analytics")
st.markdown("Interactive dashboard based on Olist e-commerce dataset")

# ----------------------------------
# Load Data
# ----------------------------------
@st.cache_data
def load_data():
    orders = pd.read_csv(
        "olist_orders_dataset.csv",
        parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"]
    )
    customers = pd.read_csv("olist_customers_dataset.csv")
    items = pd.read_csv("olist_order_items_dataset.csv")
    payments = pd.read_csv("olist_order_payments_dataset.csv")
    return orders, customers, items, payments


orders, customers, items, payments = load_data()

# ----------------------------------
# Data Preparation
# ----------------------------------
payments_agg = payments.groupby("order_id", as_index=False)["payment_value"].sum()

items_agg = items.groupby("order_id").agg(
    total_items=("order_item_id", "count"),
    total_price=("price", "sum")
).reset_index()

df = (
    orders.merge(customers, on="customer_id", how="left")
    .merge(payments_agg, on="order_id", how="left")
    .merge(items_agg, on="order_id", how="left")
)

# ----------------------------------
# Funnel Metrics
# ----------------------------------
total_orders = df["order_id"].nunique()
approved_orders = df[df["order_status"] == "approved"]["order_id"].nunique()
shipped_orders = df[df["order_status"] == "shipped"]["order_id"].nunique()
delivered_orders = df[df["order_status"] == "delivered"]["order_id"].nunique()

funnel_df = pd.DataFrame({
    "Stage": ["Total Orders", "Approved", "Shipped", "Delivered"],
    "Count": [total_orders, approved_orders, shipped_orders, delivered_orders]
})

# ----------------------------------
# KPI Section
# ----------------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Approved Orders", f"{approved_orders:,}")
col3.metric("Shipped Orders", f"{shipped_orders:,}")
col4.metric("Delivered Orders", f"{delivered_orders:,}")

# ----------------------------------
# Funnel Visualization
# ----------------------------------
st.subheader("🔻 Conversion Funnel")

fig_funnel = px.funnel(
    funnel_df,
    x="Count",
    y="Stage",
    title="Order Conversion Funnel"
)
st.plotly_chart(fig_funnel, use_container_width=True)

# ----------------------------------
# Order Status Distribution
# ----------------------------------
st.subheader("📦 Order Status Distribution")

status_df = df["order_status"].value_counts().reset_index()
status_df.columns = ["order_status", "count"]

fig_status = px.bar(
    status_df,
    x="order_status",
    y="count",
    color="order_status",
    title="Order Status Breakdown"
)

st.plotly_chart(fig_status, use_container_width=True)

# ----------------------------------
# Revenue Analysis
# ----------------------------------
st.subheader("💰 Revenue Analysis")

fig_revenue = px.histogram(
    df,
    x="payment_value",
    nbins=50,
    title="Payment Value Distribution",
    labels={"payment_value": "Order Payment Value"}
)

st.plotly_chart(fig_revenue, use_container_width=True)

# ----------------------------------
# Time-based Trend
# ----------------------------------
st.subheader("📈 Orders Over Time")

df["order_date"] = df["order_purchase_timestamp"].dt.date
orders_by_date = df.groupby("order_date")["order_id"].nunique().reset_index()

fig_time = px.line(
    orders_by_date,
    x="order_date",
    y="order_id",
    title="Daily Orders Trend"
)

st.plotly_chart(fig_time, use_container_width=True)


