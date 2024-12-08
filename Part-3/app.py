import streamlit as st
import pandas as pd
from prophet import Prophet
import numpy as np
import psycopg2

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = "SELECT created_at, total_amount FROM orders"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("Order Trends Forecasting")

# Load and clean data
orders = load_data()
orders['created_at'] = pd.to_datetime(orders['created_at'])
daily_orders = orders.groupby(orders['created_at'].dt.date)['total_amount'].sum().reset_index()
daily_orders.columns = ['date', 'total_amount']
daily_orders['date'] = pd.to_datetime(daily_orders['date'])
daily_orders = daily_orders.rename(columns={'date': 'ds', 'total_amount': 'y'})

# Handle extreme values
daily_orders['y'] = daily_orders['y'].apply(lambda x: np.log1p(x))

# Display data
st.write("Data Summary", daily_orders.describe())
st.line_chart(daily_orders.set_index('ds')['y'])

# Create and fit the model
try:
    model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
    model.add_seasonality(name='monthly', period=30.5, fourier_order=3)
    model.fit(daily_orders, control={'max_treedepth': 10, 'adapt_delta': 0.8})
except RuntimeError as e:
    st.error(f"Model fitting failed: {e}")
    st.stop()

# Forecast future trends
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Reverse log transformation
forecast['yhat'] = np.expm1(forecast['yhat'])

# Display forecast
st.write("Forecasted Order Trends")
fig = model.plot(forecast)
st.pyplot(fig)
