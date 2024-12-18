import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Function to load data from CSV files


def load_data(categories_file, vendors_file, product_names_file, products_file, product_ratings_file, orders_file):
    try:
        # Load CSV files
        categories = pd.read_csv(categories_file)
        vendors = pd.read_csv(vendors_file)
        product_names = pd.read_csv(product_names_file)
        products = pd.read_csv(products_file)
        product_ratings = pd.read_csv(product_ratings_file)
        orders = pd.read_csv(orders_file)

        # Rename columns to remove trailing spaces
        categories.rename(columns=lambda x: x.strip(), inplace=True)
        vendors.rename(columns=lambda x: x.strip(), inplace=True)
        product_names.rename(columns=lambda x: x.strip(), inplace=True)
        products.rename(columns=lambda x: x.strip(), inplace=True)
        product_ratings.rename(columns=lambda x: x.strip(), inplace=True)
        orders.rename(columns=lambda x: x.strip(), inplace=True)

        # Join tables to create the final dataset
        data = (
            product_names.merge(categories, how="left",
                                left_on="category_id", right_on="category_id")
            .merge(products, how="left", left_on="product_names_id", right_on="name_id")
            .merge(vendors, how="left", left_on="vendor_id", right_on="vendor_id")
            .merge(product_ratings, how="left", left_on="product_id", right_on="product_id")
            .merge(orders, how="left", left_on="order_id", right_on="order_id")
        )

        # Filter out deleted orders
        data = data[data["deleted_at"].isnull()]

        # Calculate total order contribution
        data = (
            data.groupby(["name", "phone"])["total_amount"]
            .sum()
            .reset_index()
            .rename(columns={"name": "category_name", "phone": "vendor_phone", "total_amount": "total_order_contribution"})
        )

        return data

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Function to load cleaned data


def load_cleaned_data(file_path="orders_cleaned.csv"):
    return pd.read_csv(file_path)

# Function to detect anomalies


def detect_anomalies(data):
    threshold = 3
    data['z_score'] = (data['total_amount'] -
                       data['total_amount'].mean()) / data['total_amount'].std()
    anomalies = data[data['z_score'].abs() > threshold]
    return anomalies


# Set up the Streamlit app
st.set_page_config(page_title="Advanced Multi-Tab Dashboard", layout="wide")

# Navigation sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", [
    "Home", "Dynamic Heatmap", "Order Trends Forecasting", "Anomaly Detection", "Order Distribution Analysis"])

# Home Page
if page == "Home":
    st.title("Welcome to the Advanced Dashboard")
    st.image("https://via.placeholder.com/800x300.png?text=Welcome+to+the+Dashboard",
             use_column_width=True)

    # Load data for summary metrics
    data = load_data(
        "categories.csv",
        "vendors.csv",
        "product_names.csv",
        "products.csv",
        "product_ratings.csv",
        "orders.csv",
    )

    if not data.empty:
        st.header("Key Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue",
                      f"${data['total_order_contribution'].sum():,.2f}")
        with col2:
            st.metric("Total Categories", len(data['category_name'].unique()))
        with col3:
            st.metric("Total Vendors", len(data['vendor_phone'].unique()))

        st.header("Recent Data Preview")
        st.dataframe(data.head(10))  # Display the first 10 rows of data
    else:
        st.warning("No data available for preview.")

# Dynamic Heatmap Tab
elif page == "Dynamic Heatmap":
    st.header("Dynamic Heatmap Dashboard")

    with st.sidebar:
        st.subheader("Filters")
        # Load data
        data = load_data(
            "categories.csv",
            "vendors.csv",
            "product_names.csv",
            "products.csv",
            "product_ratings.csv",
            "orders.csv",
        )

        if not data.empty:
            # Filter by category
            categories = data['category_name'].unique()
            selected_categories = st.multiselect(
                "Select Categories", options=categories, default=categories)

            # Filter by vendor phone
            vendors = data['vendor_phone'].unique()
            selected_vendors = st.multiselect(
                "Select Vendors", options=vendors, default=vendors)

    if not data.empty:
        # Filter data based on selections
        filtered_data = data[data['category_name'].isin(
            selected_categories) & data['vendor_phone'].isin(selected_vendors)]

        if not filtered_data.empty:
            # Pivot the data to create a heatmap-friendly format
            pivot_table = filtered_data.pivot(
                index='category_name', columns='vendor_phone', values='total_order_contribution').fillna(0)

            # Heatmap customization options
            color_palette = st.sidebar.selectbox("Select Color Palette", options=[
                                                 'YlGnBu', 'coolwarm', 'viridis', 'plasma'], index=0)
            annot_option = st.sidebar.checkbox("Show Annotations", value=True)

            # Create a heatmap
            plt.figure(figsize=(14, 10))
            sns.heatmap(pivot_table, annot=annot_option, fmt=".1f", cmap=color_palette,
                        linewidths=0.5, cbar_kws={'label': 'Order Contribution'})
            plt.title(
                "Heatmap of Order Contributions by Product Categories and Vendors", fontsize=16)
            plt.xlabel("Vendor Phone", fontsize=12)
            plt.ylabel("Category Name", fontsize=12)

            # Display the heatmap in Streamlit
            st.pyplot(plt)

            # Drilldown feature
            st.sidebar.subheader("Drilldown")
            selected_category = st.sidebar.selectbox(
                "Select a Category", options=pivot_table.index)
            selected_vendor = st.sidebar.selectbox(
                "Select a Vendor", options=pivot_table.columns)

            # Filter and display detailed data based on selections
            if selected_category and selected_vendor:
                detailed_data = filtered_data[(filtered_data['category_name'] == selected_category) &
                                              (filtered_data['vendor_phone'] == selected_vendor)]
                if not detailed_data.empty:
                    st.subheader(
                        f"Detailed Data for {selected_category} - {selected_vendor}")
                    st.write(detailed_data)
                else:
                    st.warning(
                        "No detailed data available for the selected category and vendor.")

            # Download option for filtered data
            csv = filtered_data.to_csv(index=False)
            st.download_button(label="Download Filtered Data as CSV",
                               data=csv, file_name="filtered_data.csv", mime="text/csv")
        else:
            st.warning("No data available for the selected filters.")
    else:
        st.error("No data available to display.")

# Order Distribution Analysis Tab
elif page == "Order Distribution Analysis":
    st.header("Order Distribution Analysis")

    with st.sidebar:
        st.subheader("Filters")
        # Load data
        data = load_data(
            "categories.csv",
            "vendors.csv",
            "product_names.csv",
            "products.csv",
            "product_ratings.csv",
            "orders.csv",
        )

        # Filter by categories
        if not data.empty:
            categories = data['category_name'].unique()
            selected_categories = st.multiselect(
                "Select Categories", options=categories, default=categories)

    if not data.empty:
        # Apply category filter
        filtered_data = data[data['category_name'].isin(selected_categories)]

        if not filtered_data.empty:
            # Category-wise Contribution (Pie Chart)
            st.subheader("Category-wise Contribution")
            category_contribution = filtered_data.groupby("category_name")[
                "total_order_contribution"].sum().reset_index()
            plt.figure(figsize=(8, 8))
            plt.pie(category_contribution["total_order_contribution"], labels=category_contribution["category_name"],
                    autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
            plt.title("Contribution by Category")
            st.pyplot(plt)

            # Vendor Performance (Bar Chart)
            st.subheader("Top 10 Vendors by Contribution")
            top_vendors = filtered_data.groupby("vendor_phone")["total_order_contribution"].sum().sort_values(
                ascending=False).head(10)
            plt.figure(figsize=(10, 6))
            sns.barplot(x=top_vendors.values,
                        y=top_vendors.index, palette="Blues_d")
            plt.title("Top 10 Vendors by Total Order Contribution")
            plt.xlabel("Total Contribution")
            plt.ylabel("Vendor Phone")
            st.pyplot(plt)
        else:
            st.warning("No data available for the selected filters.")
    else:
        st.error("No data available for analysis.")

# Order Trends Forecasting Tab
elif page == "Order Trends Forecasting":
    st.header("Order Trends Forecasting (ARIMA)")

    # User Inputs for ARIMA Model
    col1, col2 = st.columns([1, 3])

    with col1:
        p = st.number_input("AR Parameter (p):", min_value=0, value=1)
        d = st.number_input("Differencing Parameter (d):",
                            min_value=0, value=1)
        q = st.number_input("MA Parameter (q):", min_value=0, value=1)
        forecast_steps = st.number_input(
            "Number of days to forecast:", min_value=1, value=30)

    with col2:
        # Load the cleaned data
        orders = load_cleaned_data()

        # Data Summary and Display
        st.write("Data Summary:", orders.describe())
        st.line_chart(orders.set_index('date')['total_amount'])

        # Rename columns for ARIMA
        orders = orders.rename(columns={'date': 'ds', 'total_amount': 'y'})
        orders['ds'] = pd.to_datetime(orders['ds'], errors='coerce')
        orders['y'] = pd.to_numeric(orders['y'], errors='coerce')
        orders.dropna(subset=['ds', 'y'], inplace=True)
        orders = orders[orders['y'] > 0]
        orders['y'] = np.log1p(orders['y'])
        orders.set_index('ds', inplace=True)

        # --- ARIMA Model --- #
        try:
            arima_model = ARIMA(orders['y'], order=(p, d, q))
            arima_model_fit = arima_model.fit()
            arima_forecast = arima_model_fit.forecast(steps=forecast_steps)
            arima_forecast = np.expm1(arima_forecast)

            forecast_index = pd.date_range(
                start=orders.index[-1] + pd.Timedelta(days=1), periods=forecast_steps)
            arima_forecast_df = pd.DataFrame(
                {'ds': forecast_index, 'yhat': arima_forecast})

            st.write("Forecasted Order Trends (ARIMA)")
            st.line_chart(arima_forecast_df.set_index('ds')['yhat'])

        except Exception as e:
            st.error(f"ARIMA Model fitting failed: {e}")

# Anomaly Detection Tab
elif page == "Anomaly Detection":
    st.header("Anomaly Detection")

    # Load the cleaned data
    data = load_cleaned_data()

    if not data.empty:
        # Detect anomalies in the data
        anomalies = detect_anomalies(data)
        st.subheader("Detected Anomalies")
        st.write(anomalies)
