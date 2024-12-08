import streamlit as st
import pandas as pd
import psycopg2
import seaborn as sns
import matplotlib.pyplot as plt

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}

# Function to load data from PostgreSQL
def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
    SELECT 
        c.name AS category_name,
        v.phone AS vendor_phone,
        SUM(o.total_amount) AS total_order_contribution
    FROM 
        public.product_names pn
    LEFT JOIN 
        public.categories c ON pn.category_id = c.id
    LEFT JOIN 
        public.products p ON pn.id = p.name_id
    LEFT JOIN 
        public.vendors v ON p.vendor_id = v.id
    JOIN 
        public.product_ratings pr ON p.id = pr.product_id
    JOIN 
        public.orders o ON pr.order_id = o.id
    WHERE 
        o.deleted_at IS NULL  -- Ensure we only consider non-deleted orders
    GROUP BY 
        c.name, v.phone
    ORDER BY 
        c.name, v.phone;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Set up the Streamlit app
st.title("Dynamic Heatmap Dashboard")

# Load data
data = load_data()

# Check if data is loaded
if not data.empty:
    # Create a sidebar for user interaction
    st.sidebar.header("Filter Options")

    # Display the raw data
    if st.sidebar.checkbox("Show Raw Data"):
        st.subheader("Raw Data")
        st.write(data)

    # Pivot the data to create a heatmap-friendly format
    pivot_table = data.pivot(index='category_name', columns='vendor_phone', values='total_order_contribution').fillna(0)

    # Create a heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=.5)
    plt.title("Heatmap of Order Contributions by Product Categories and Vendors")
    plt.xlabel("Vendor Phone")
    plt.ylabel("Category Name")

    # Display the heatmap in Streamlit
    st.pyplot(plt)

else:
    st.write("No data available to display.")
    
    
    # used vendor phone number because vendor name is null