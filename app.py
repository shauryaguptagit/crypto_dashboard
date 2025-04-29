import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import datetime

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("📈 Crypto Market Insights Dashboard")

# --- Constants ---
COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL"
}
DAYS = 365
API_URL = "https://api.coingecko.com/api/v3/coins/{}/market_chart"

# --- Fetch Data ---
@st.cache_data(show_spinner=True)
def fetch_data(coin_id, days):
    url = API_URL.format(coin_id)
    params = {"vs_currency": "usd", "days": days}
    response = requests.get(url, params=params)
    data = response.json()["prices"]
    df = pd.DataFrame(data, columns=["timestamp", coin_id])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

# --- Load and Merge Data ---
def load_data():
    dfs = [fetch_data(coin, DAYS) for coin in COINS.keys()]
    df = pd.concat(dfs, axis=1)
    df.columns = [COINS[coin] for coin in COINS.keys()]
    df.dropna(inplace=True)
    return df

# --- Main Processing ---
data = load_data()
returns = data.pct_change().dropna()
volatility = returns.rolling(window=30).std()
correlation = returns.corr()

# --- Plotting Functions ---
def plot_line_chart(df, title, ylabel):
    fig, ax = plt.subplots(figsize=(10, 4))
    df.plot(ax=ax)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    st.pyplot(fig)

def plot_heatmap(df, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(df, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title(title)
    st.pyplot(fig)

# --- Layout ---
st.subheader("🔹 Price Trends")
plot_line_chart(data, "Price Trends", "Price (USD)")

st.subheader("🔹 Daily Returns")
plot_line_chart(returns, "Daily Returns", "Return")

st.subheader("🔹 Rolling Volatility (30-day)")
plot_line_chart(volatility, "30-Day Rolling Volatility", "Volatility")

st.subheader("🔹 Correlation Heatmap")
plot_heatmap(correlation, "Asset Correlation")

# --- Sidebar ---
st.sidebar.title("Options")
if st.sidebar.checkbox("Show Raw Data"):
    st.subheader("Raw Price Data")
    st.dataframe(data.tail())

st.sidebar.markdown("---")
st.sidebar.markdown("[Powered by CoinGecko API](https://www.coingecko.com/en/api)")