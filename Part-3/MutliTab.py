import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import psycopg2

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
                o.deleted_at IS NULL
            GROUP BY 
                c.name, v.phone
            ORDER BY 
                c.name, v.phone;
            """
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading data from the database: {e}")
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
st.set_page_config(page_title="Multi-Tab Dashboard", layout="wide")

# Navigation sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", [
                        "Home", "Dynamic Heatmap", "Order Trends Forecasting", "Anomaly Detection"])

# Home Page
if page == "Home":
    st.title("Welcome to the Multi-Tab Dashboard")
    st.write("""
        This dashboard provides insights into order data through various visualizations.
        Use the navigation on the left to explore different sections of the dashboard.
        - **Dynamic Heatmap**: Visualize order contributions across categories and vendors.
        - **Order Trends Forecasting**: Forecast future order trends using the ARIMA model.
        - **Anomaly Detection**: Identify and visualize anomalies in the order data.
    """)
    st.image("https://via.placeholder.com/800x300.png?text=Dashboard+Overview")  # Placeholder for an image

# Dynamic Heatmap Tab
elif page == "Dynamic Heatmap":
    st.header("Dynamic Heatmap Dashboard")

    # Layout with filters on the left
    col1, col2 = st.columns([1, 3])

    with col1:
        # Load data
        data = load_data()

        if not data.empty:
            # Filter by category
            categories = data['category_name'].unique()
            selected_categories = st.multiselect(
                "Select Categories", options=categories, default=categories)

            # Filter by vendor phone
            vendors = data['vendor_phone'].unique()
            selected_vendors = st.multiselect(
                "Select Vendors", options=vendors, default=vendors)

    with col2:
        if not data.empty:
            # Filter data based on selections
            filtered_data = data[data['category_name'].isin(
                selected_categories) & data['vendor_phone'].isin(selected_vendors)]

            # Display the raw data
            if st.checkbox("Show Raw Data"):
                st.subheader("Filtered Raw Data")
                st.write(filtered_data)

            # Pivot the data to create a heatmap-friendly format
            if not filtered_data.empty:
                pivot_table = filtered_data.pivot(
                    index='category_name', columns='vendor_phone', values='total_order_contribution').fillna(0)

                # Heatmap customization options
                color_palette = st.selectbox("Select Color Palette", options=[
                                             'YlGnBu', 'coolwarm', 'viridis', 'plasma'], index=0)
                annot_option = st.checkbox("Show Annotations", value=True)

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

                # Drill-Down Feature
                st.write("Click on any heatmap cell to see detailed data.")
                selected_category = st.selectbox(
                    "Select a Category", options=pivot_table.index)
                selected_vendor = st.selectbox(
                    "Select a Vendor", options=pivot_table.columns)

                # Filter and display detailed data based on selections
                if selected_category and selected_vendor:
                    detailed_data = filtered_data[(filtered_data['category_name'] == selected_category) & (
                        filtered_data['vendor_phone'] == selected_vendor)]
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

# Order Trends Forecasting Tab
elif page == "Order Trends Forecasting":
    st.header("Order Trends Forecasting (ARIMA)")

    # Layout with filters on the left
    col1, col2 = st.columns([1, 3])

    with col1:
        # User Inputs for ARIMA Model
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

        # Prepare data for ARIMA
        orders.set_index('ds', inplace=True)

        # --- ARIMA Model --- #
        try:
            arima_model = ARIMA(orders['y'], order=(p, d, q))
            arima_model_fit = arima_model.fit()

            # Forecast the specified number of days
            arima_forecast = arima_model_fit.forecast(steps=forecast_steps)
            # Reverse the log transformation
            arima_forecast = np.expm1(arima_forecast)

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

            # Drill-Down Feature
            selected_date = st.selectbox(
                "Select a Date to See Details", options=orders.index.date)
            if selected_date:
                detailed_orders = orders[orders.index.date == selected_date]
                if not detailed_orders.empty:
                    st.subheader(f"Detailed Orders for {selected_date}")
                    st.write(detailed_orders)
                else:
                    st.warning("No orders available for the selected date.")

        except Exception as e:
            st.error(f"ARIMA Model fitting failed: {e}")

# Anomaly Detection Tab
elif page == "Anomaly Detection":
    st.header("Anomaly Detection in Order Data")

    # Load the cleaned data
    orders = load_cleaned_data()

    # Detect anomalies
    if not orders.empty:
        anomalies = detect_anomalies(orders)

        # Plotting the time series with anomalies
        plt.figure(figsize=(14, 7))
        plt.plot(orders['date'], orders['total_amount'],
                 label='Total Amount', color='blue')

        # Highlight anomalies
        if not anomalies.empty:
            plt.scatter(anomalies['date'], anomalies['total_amount'],
                        color='red', label='Anomalies', zorder=5)
            for i in range(len(anomalies)):
                plt.annotate(f'Anomaly: {anomalies["total_amount"].iloc[i]:.2f}',
                             (anomalies['date'].iloc[i],
                              anomalies['total_amount'].iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', fontsize=8, color='red')

        plt.title("Time Series Data with Anomaly Detection")
        plt.xlabel("Date")
        plt.ylabel("Total Amount")
        plt.legend()
        st.pyplot(plt)
    else:
        st.warning("No data available for anomaly detection.")
