import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}

# Function to connect to the database and fetch data


def fetch_data():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Fetch data from groups_carts
        cursor.execute("SELECT group_id, quantity FROM groups_carts;")
        groups_carts = pd.DataFrame(cursor.fetchall(), columns=[
                                    'group_id', 'quantity'])

        # Fetch data from single_deals
        cursor.execute("SELECT quantity FROM single_deals;")
        single_deals = pd.DataFrame(cursor.fetchall(), columns=['quantity'])

        cursor.close()
        conn.close()

        return groups_carts, single_deals

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames on error

# Function to calculate average quantities


def calculate_average_quantities(groups_carts, single_deals):
    # Calculate average quantities for group deals
    average_group_quantities = groups_carts.groupby(
        'group_id')['quantity'].mean().reset_index()
    average_group_quantities['deal_type'] = 'Group Deals'

    # Calculate average quantity for individual deals
    average_single_quantity = single_deals['quantity'].mean()
    average_single_quantities = pd.DataFrame({
        'group_id': ['00000000-0000-0000-0000-000000000000'],  # Dummy UUID
        'quantity': [average_single_quantity],
        'deal_type': ['Single Deals']
    })

    # Combine the two DataFrames
    combined = pd.concat(
        [average_group_quantities, average_single_quantities], ignore_index=True)
    return combined


# Streamlit dashboard
st.title('Average Order Quantity Comparison: Group Deals vs Individual Deals')

# Fetch data from the database
groups_carts, single_deals = fetch_data()

# Display fetched data for debugging
st.write("Groups Carts Data:", groups_carts)
st.write("Single Deals Data:", single_deals)

# Check if data is fetched successfully
if not groups_carts.empty and not single_deals.empty:
    # Calculate average quantities
    average_quantities = calculate_average_quantities(
        groups_carts, single_deals)

    # Display average quantities for debugging
    st.write("Average Quantities:", average_quantities)

    # Create a grouped bar chart
    fig, ax = plt.subplots()
    for deal_type in average_quantities['deal_type'].unique():
        subset = average_quantities[average_quantities['deal_type'] == deal_type]
        ax.bar(subset['group_id'], subset['quantity'], label=deal_type)

    ax.set_xlabel('Deal Type')
    ax.set_ylabel('Average Quantity')
    ax.set_title('Average Order Quantities')
    ax.legend()

    # Display the chart in Streamlit
    st.pyplot(fig)
else:
    st.error("No data available to display.")
