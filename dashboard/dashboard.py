# Dibuat oleh : I Gusti Ngurah Ervan Juli Ardana

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    return daily_orders_df


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_id").order_id.sum(
    ).sort_values(ascending=False).reset_index()
    return sum_order_items_df


def create_bystate_df(df):
    bystate_df = df.groupby(
        by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return bystate_df

# FUNGSI RFM


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_approved_at": "max",  # mengambil tanggal order terakhir
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id",
                      "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_approved_at"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


def sum_city_df(df):
    sum_city_data = df.groupby(by="customer_city").order_id.nunique(
    ).sort_values(ascending=False).reset_index()
    sum_city_data.rename(columns={
        "customer_city": "city"
    }, inplace=True)
    return sum_city_data


def create_byreview_df(df):
    create_byreview_df = df.groupby(by="review_score").order_id.nunique(
    ).reset_index()
    create_byreview_df.rename(columns={
        "review_score": "score"
    }, inplace=True)
    return create_byreview_df


all_df = pd.read_csv("main_data.csv")

datetime_columns = ["order_approved_at", "order_delivered_customer_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Membuat Komponen Filter
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    # st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                 (all_df["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
byreview_df = create_byreview_df(main_df)
rfm_df = create_rfm_df(main_df)
sum_city_df_df = sum_city_df(main_df)

st.header('Public E-Commerce')

# membuat kolom:
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

# mengisi kolom 1
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

# mengisi kolom 2
with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "$", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

# menambahkan chart
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# membuat sub header
st.subheader("Best & Worst Sales City")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_id", y="city",
            data=sum_city_df_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Most Sales City", loc="center", fontsize=70)
ax[0].tick_params(axis='y', labelsize=15)

sns.barplot(x="order_id", y="city", data=sum_city_df_df.sort_values(
    by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Sales City", loc="center", fontsize=70)
ax[1].tick_params(axis='y', labelsize=15)

st.pyplot(fig)

# membuat sub header 2
st.subheader("Demografi Customers")

fig1, ax = plt.subplots(figsize=(16, 8))

colors_ = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors_
)
plt.title("Number of Customer by States", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=12)

st.pyplot(fig1)

# membuat sub header 3
st.subheader("Review Customers")

fig1, ax = plt.subplots(figsize=(16, 8))

colors_ = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#90CAF9"]

sns.barplot(
    y="order_id",
    x="score",
    data=byreview_df.sort_values(by="score", ascending=False),
    palette=colors_
)
plt.title("Number of Review Score by Customer", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)
plt.show()

st.pyplot(fig1)

# RFM
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(
        rfm_df.monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(
    by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(
    by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(
    by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)
