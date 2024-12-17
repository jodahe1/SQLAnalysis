import streamlit as st
import pandas as pd
import psycopg2
import threading
import time

# Database connection parameters
# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}


# Global variable to store order data
order_data = pd.DataFrame()

# Function to fetch new orders


def fetch_new_orders():
    global order_data
    conn = psycopg2.connect(**DB_CONFIG)
    while True:
        # Query to fetch new orders
        query = "SELECT * FROM orders WHERE created_at >= NOW() - INTERVAL '5 minutes';"
        new_orders = pd.read_sql(query, conn)

        # Update order_data
        if not new_orders.empty:
            previous_count = order_data.shape[0]
            order_data = pd.concat(
                [order_data, new_orders]).drop_duplicates().reset_index(drop=True)

            # Check for anomalies
            # Example condition for significant drop
            if order_data.shape[0] < previous_count * 0.5:
                st.warning("Significant drop in orders detected!")

        time.sleep(300)  # Sleep for 5 minutes


# Start the background thread
threading.Thread(target=fetch_new_orders, daemon=True).start()

# Streamlit app UI
st.title("Order Dashboard")
st.dataframe(order_data)
