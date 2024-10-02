import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set the Seaborn style
sns.set(style='dark')

def create_cancel_product_df(df):
    canceled_orders_df = df[df['order_status'] == 'canceled']
    top_10_canceled_products_df = canceled_orders_df.groupby(by="product_category_name").order_id.nunique().reset_index()
    top_10_canceled_products_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    
    top_10_canceled_products_df = top_10_canceled_products_df.sort_values(by="order_count", ascending=False).head(10)
    return top_10_canceled_products_df

def create_rfm_df(df):
    df['customer_id'] = df['customer_unique_id'].str[:5]
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",  # mengambil tanggal order terakhir
        "order_id": "nunique",              # frekuensi pembelian
        "payment_value": "sum"              # nilai total pembayaran
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # Convert the timestamp to date and calculate recency
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]).dt.date
    recent_date = df["order_purchase_timestamp"].max().date()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

# Load data
all_df = pd.read_csv("main_data.csv")

# Convert the necessary columns to datetime
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Sort data based on purchase timestamp and reset the index
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Get minimum and maximum date
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

# Sidebar for date range selection
with st.sidebar:
    st.image("https://raw.githubusercontent.com/milacahyanii/Dicoding/main/iconshop.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', 
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data by the selected date range
main_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                 (all_df["order_purchase_timestamp"].dt.date <= end_date)]

# Create dataframes for cancel product and RFM
cancel_product_df = create_cancel_product_df(main_df)
rfm_df = create_rfm_df(main_df)

# Header for dashboard
st.header('Milss E-Commerce Dashboard :store:')

# Top 10 Canceled Products
st.subheader('Top 10 Kategori Produk yang Paling Banyak Dibatalkan :cancel:')
plt.figure(figsize=(12, 8))
sns.barplot(
    x=cancel_product_df['order_count'],
    y=cancel_product_df['product_category_name'],
    palette='Blues_r'
)
plt.title('Top 10 Kategori Produk yang Paling Banyak Dibatalkan', fontsize=20, weight='bold')
plt.ylabel('Kategori Produk', fontsize=14, weight='bold')
plt.xlabel('Jumlah Pesanan yang Dibatalkan', fontsize=14, weight='bold')
plt.tight_layout()
st.pyplot(plt)

# Category Product Reviews
st.subheader('Kategori Produk Berdasarkan Review Customers  :label:')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))

all_df.rename(columns={"product_category_name_english": "category_eng"}, inplace=True)
top_category_product_review = all_df.groupby('category_eng').review_score.mean().reset_index().sort_values(by='review_score', ascending=False).head(10)
sns.barplot(x='review_score', y='category_eng', data=top_category_product_review, palette='Blues', ax=ax[0])
ax[0].set_xlabel('Rata-rata Skor Ulasan')
ax[0].set_title('Kepuasan Tertinggi')

low_category_product_review = all_df.groupby('category_eng').review_score.mean().reset_index().sort_values(by='review_score', ascending=True).head(10)
sns.barplot(x='review_score', y='category_eng', data=low_category_product_review, palette='Blues', ax=ax[1])
ax[1].set_xlabel('Rata-rata Skor Ulasan')
ax[1].invert_xaxis()
ax[1].set_title('Kepuasan Terendah')

plt.suptitle('Kategori Produk dengan Ulasan Terbaik dan Terburuk Berdasarkan Skor Ulasan')
plt.tight_layout(pad=1)
st.pyplot(fig)

# RFM Analysis
st.subheader("Pengguna terbaik berdasarkan RFM Parameters :shopping_bags:")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_monetary)

# Plot RFM charts
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_title("Berdasarkan Recency (hari)", fontsize=15)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_title("Berdasarkan Frequency", fontsize=15)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_title("Berdasarkan Monetary", fontsize=15)

plt.suptitle("Pelanggan Terbaik Berdasarkan Parameter RFM", fontsize=19)
st.pyplot(fig)

st.caption('Mila Cahyani 2024')
