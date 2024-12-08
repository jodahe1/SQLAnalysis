import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}

def load_cleaned_data(file_path="orders_cleaned.csv"):
    """Load the cleaned data that was processed and saved by the data cleaner."""
    return pd.read_csv(file_path)

st.title("Order Trends Forecasting (ARIMA)")

# Load the cleaned data (using the data cleaner output)
orders = load_cleaned_data()

# Data Summary and Display
st.write("Data Summary", orders.describe())

# Data visualization
st.line_chart(orders.set_index('date')['total_amount'])

# Ensure the date column is renamed correctly for ARIMA (ds for date, y for total amount)
orders = orders.rename(columns={'date': 'ds', 'total_amount': 'y'})

# Step 1: Ensure 'ds' is in datetime format and 'y' is numeric
orders['ds'] = pd.to_datetime(orders['ds'], errors='coerce')
orders['y'] = pd.to_numeric(orders['y'], errors='coerce')

# Step 2: Handle missing values
orders.dropna(subset=['ds', 'y'], inplace=True)

# Step 3: Remove non-positive values of 'y'
orders = orders[orders['y'] > 0]

# Step 4: Apply log transformation to 'y' to stabilize variance
orders['y'] = np.log1p(orders['y'])  # Apply log transformation to 'y' to handle skewed data

# Step 5: Check for missing values after cleaning
st.write("Missing values count:", orders.isnull().sum())
st.write("Data preview after cleaning:", orders.head())

# --- ARIMA Model --- #
# Prepare the data for ARIMA (we need a time series with the 'y' values and date as index)
orders.set_index('ds', inplace=True)

# Fit the ARIMA model (for simplicity, let's use ARIMA(1,1,1) for demonstration)
try:
    arima_model = ARIMA(orders['y'], order=(1, 1, 1))
    arima_model_fit = arima_model.fit()

    # Forecast the next 30 days with ARIMA
    arima_forecast = arima_model_fit.forecast(steps=30)
    arima_forecast = np.expm1(arima_forecast)  # Reverse the log transformation

    # Display ARIMA forecast
    st.write("Forecasted Order Trends (ARIMA)")
    arima_forecast_df = pd.DataFrame({'ds': pd.date_range(start=orders.index[-1], periods=31, freq='D')[1:], 'yhat': arima_forecast})
    st.line_chart(arima_forecast_df.set_index('ds')['yhat'])

except Exception as e:
    st.error(f"ARIMA Model fitting failed: {e}")
