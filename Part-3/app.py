import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# Database configuration (if needed for future data)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}


def load_cleaned_data(file_path="orders_cleaned.csv"):
    """Load the cleaned data that was processed and saved."""
    return pd.read_csv(file_path)


st.title("Order Trends Forecasting (ARIMA)")

# Load the cleaned data (using the data cleaner output)
orders = load_cleaned_data()

# Data Summary and Display
st.write("Data Summary:", orders.describe())

# Data visualization
st.line_chart(orders.set_index('date')['total_amount'])

# Rename columns for ARIMA
orders = orders.rename(columns={'date': 'ds', 'total_amount': 'y'})

# Ensure 'ds' is in datetime format and 'y' is numeric
orders['ds'] = pd.to_datetime(orders['ds'], errors='coerce')
orders['y'] = pd.to_numeric(orders['y'], errors='coerce')

# Handle missing values
orders.dropna(subset=['ds', 'y'], inplace=True)
orders = orders[orders['y'] > 0]

# Apply log transformation to 'y'
orders['y'] = np.log1p(orders['y'])

# Display missing values count and data preview
st.write("Missing values count:", orders.isnull().sum())
st.write("Data preview after cleaning:", orders.head())

# --- User Inputs for ARIMA Model --- #
st.sidebar.header("ARIMA Configuration")
p = st.sidebar.number_input("AR Parameter (p):", min_value=0, value=1)
d = st.sidebar.number_input(
    "Differencing Parameter (d):", min_value=0, value=1)
q = st.sidebar.number_input("MA Parameter (q):", min_value=0, value=1)
forecast_steps = st.sidebar.number_input(
    "Number of days to forecast:", min_value=1, value=30)

# Prepare data for ARIMA
orders.set_index('ds', inplace=True)

# --- ARIMA Model --- #
try:
    arima_model = ARIMA(orders['y'], order=(p, d, q))
    arima_model_fit = arima_model.fit()

    # Forecast the specified number of days
    arima_forecast = arima_model_fit.forecast(steps=forecast_steps)
    arima_forecast = np.expm1(arima_forecast)  # Reverse the log transformation

    # Create a DataFrame for the forecast
    forecast_index = pd.date_range(
        start=orders.index[-1] + pd.Timedelta(days=1), periods=forecast_steps)
    arima_forecast_df = pd.DataFrame(
        {'ds': forecast_index, 'yhat': arima_forecast})

    # Display ARIMA forecast
    st.write("Forecasted Order Trends (ARIMA)")
    st.line_chart(arima_forecast_df.set_index('ds')['yhat'])

    # Performance metrics (AIC, BIC)
    st.write("Model Performance Metrics:")
    st.write(f"AIC: {arima_model_fit.aic}")
    st.write(f"BIC: {arima_model_fit.bic}")

    # Plotting actual vs forecast
    fig, ax = plt.subplots()
    orders['y'].plot(ax=ax, label='Historical Data', color='blue')
    arima_forecast_df.set_index('ds')['yhat'].plot(
        ax=ax, label='Forecast', color='orange')
    ax.set_title("Actual vs Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Amount")
    ax.legend()
    st.pyplot(fig)

except Exception as e:
    st.error(f"ARIMA Model fitting failed: {e}")
