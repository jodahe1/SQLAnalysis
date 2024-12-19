import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np

# Set up page configurations
st.set_page_config(
    page_title="User Clustering Dashboard",
    layout="wide"
)

pages = ["Home", "Clustering Dashboard", "Orders Overview",
         "Vendor Performance", "Trend Analysis"]
page = st.sidebar.radio("Navigate", pages)

# Load data from CSV files


@st.cache_data
def load_data():
    groups_carts = pd.read_csv('groups_carts.csv')
    orders = pd.read_csv('orders.csv')
    return groups_carts, orders


groups_carts, orders = load_data()

# Process data to create user order stats


@st.cache_data
def create_user_order_stats(groups_carts, orders):
    user_order_stats = (
        groups_carts.merge(orders, left_on='id',
                           right_on='groups_carts_id', how='inner')
        .groupby('user_id')
        .agg(order_count=('id_y', 'count'), total_order_amount=('total_amount', 'sum'))
        .reset_index()
    )
    return user_order_stats


data = create_user_order_stats(groups_carts, orders)

data = data.dropna().drop_duplicates()

if page == "Home":
    st.title("Welcome to the User Clustering Dashboard")
    st.markdown("""
        <style>
            .big-font {
                font-size: 30px;
                color: #4CAF50;
                font-weight: bold;
            }
            .highlight {
                background-color: #f9f9f9;
                border-radius: 5px;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">Analyze User Behavior Effectively!</p>',
                unsafe_allow_html=True)
    st.write("This application segments users based on their purchasing behavior. Explore different pages to view clustering results, order summaries, vendor performance, and more.")
    st.write("Use the sidebar to navigate through the app.")

    st.subheader("Key Features:")
    st.markdown("""
        - **Clustering Dashboard**: Visualize user segments based on order behavior.
        - **Orders Overview**: Get insights into total revenue and order counts.
        - **Vendor Performance**: Analyze revenue contributions from different vendors.
        - **Trend Analysis**: Observe trends in order amounts over time.
    """)

    st.markdown('<div class="highlight">Explore user segments and make data-driven decisions!</div>',
                unsafe_allow_html=True)

elif page == "Clustering Dashboard":
    st.title("Clustering Dashboard")

    st.sidebar.header("Clustering Settings")
    n_clusters = st.sidebar.slider(
        "Number of Clusters", min_value=2, max_value=10, value=3, step=1)
    random_state = st.sidebar.number_input("Random State", value=42, step=1)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    data['cluster'] = kmeans.fit_predict(
        data[['order_count', 'total_order_amount']])

    st.header("Clustering Results")
    st.dataframe(data)

    st.header("Visualizations")
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(data['order_count'], data['total_order_amount'],
                         c=data['cluster'], cmap='viridis', alpha=0.7)
    centers = kmeans.cluster_centers_
    ax.scatter(centers[:, 0], centers[:, 1], c='red',
               marker='X', s=200, label='Cluster Centers')
    ax.set_xlabel('Order Count')
    ax.set_ylabel('Total Order Amount')
    ax.set_title('User Clustering')
    ax.legend()
    st.pyplot(fig)

    st.subheader("Cluster Distributions")
    cluster_col = st.selectbox("Choose a feature to analyze", [
                               "order_count", "total_order_amount"], index=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    for cluster in data['cluster'].unique():
        subset = data[data['cluster'] == cluster]
        ax.hist(subset[cluster_col], bins=20,
                alpha=0.5, label=f'Cluster {cluster}')
    ax.set_xlabel(cluster_col.replace("_", " ").title())
    ax.set_ylabel('Frequency')
    ax.set_title(
        f'Distribution of {cluster_col.replace("_", " ").title()} by Cluster')
    ax.legend()
    st.pyplot(fig)

elif page == "Orders Overview":
    st.title("Orders Overview")
    st.write("Get a quick overview of all orders.")

    total_revenue = data['total_order_amount'].sum()
    total_orders = data['order_count'].sum()

    st.metric("Total Revenue", f"${total_revenue:,.2f}")
    st.metric("Total Orders", f"{total_orders}")

    st.subheader("Revenue Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data['total_order_amount'], bins=20, color='green', alpha=0.7)
    ax.set_xlabel('Order Amount')
    ax.set_ylabel('Frequency')
    ax.set_title('Revenue Distribution')
    st.pyplot(fig)

elif page == "Vendor Performance":
    st.title("Vendor Performance")
    st.write("Analyze revenue contributions by vendors.")

    vendors_data = pd.DataFrame({
        'vendor_id': ['V1', 'V2', 'V3', 'V4'],
        'revenue': [15000, 22000, 18000, 25000]
    })

    st.dataframe(vendors_data)

    st.subheader("Revenue by Vendor")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(vendors_data['vendor_id'], vendors_data['revenue'], color='purple')
    ax.set_xlabel('Vendor ID')
    ax.set_ylabel('Revenue')
    ax.set_title('Revenue Contribution by Vendor')
    st.pyplot(fig)

elif page == "Trend Analysis":
    st.title("Trend Analysis")
    st.write("Visualize trends in order amounts over time.")

    # Simulating time series data
    time_series_data = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=100),
        'total_amount': (1000 * np.random.rand(100)).cumsum()
    })

    st.line_chart(time_series_data.set_index('date')['total_amount'])
    st.subheader("Daily Order Amounts")
    st.write("This chart shows the cumulative total order amounts over time.")
