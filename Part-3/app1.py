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
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
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
        return df
    except Exception as e:
        st.error(f"Error loading data from the database: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error


# Set up the Streamlit app
st.set_page_config(page_title="Dynamic Heatmap Dashboard", layout="wide")
st.title("Dynamic Heatmap Dashboard")

# Load data
data = load_data()

# Check if data is loaded
if not data.empty:
    # Create a sidebar for user interaction
    st.sidebar.header("Filter Options")

    # Filter by category
    categories = data['category_name'].unique()
    selected_categories = st.sidebar.multiselect(
        "Select Categories", options=categories, default=categories)

    # Filter by vendor phone
    vendors = data['vendor_phone'].unique()
    selected_vendors = st.sidebar.multiselect(
        "Select Vendors", options=vendors, default=vendors)

    # Filter data based on selections
    filtered_data = data[data['category_name'].isin(
        selected_categories) & data['vendor_phone'].isin(selected_vendors)]

    # Display the raw data
    if st.sidebar.checkbox("Show Raw Data"):
        st.subheader("Filtered Raw Data")
        st.write(filtered_data)

    # Pivot the data to create a heatmap-friendly format
    if not filtered_data.empty:
        pivot_table = filtered_data.pivot(
            index='category_name', columns='vendor_phone', values='total_order_contribution').fillna(0)

        # Heatmap customization options
        st.sidebar.header("Heatmap Customization")
        color_palette = st.sidebar.selectbox("Select Color Palette", options=[
                                             'YlGnBu', 'coolwarm', 'viridis', 'plasma'], index=0)
        annot_option = st.sidebar.checkbox("Show Annotations", value=True)

        # Create a heatmap
        plt.figure(figsize=(14, 10))
        sns.heatmap(
            pivot_table,
            annot=annot_option,
            fmt=".1f",
            cmap=color_palette,
            linewidths=0.5,
            cbar_kws={'label': 'Order Contribution'}
        )
        plt.title(
            "Heatmap of Order Contributions by Product Categories and Vendors", fontsize=16)
        plt.xlabel("Vendor Phone", fontsize=12)
        plt.ylabel("Category Name", fontsize=12)

        # Display the heatmap in Streamlit
        st.pyplot(plt)

        # Download option for filtered data
        csv = filtered_data.to_csv(index=False)
        st.sidebar.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available for the selected filters.")
else:
    st.error("No data available to display.")
