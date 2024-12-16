# user Segment 2 used
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from io import BytesIO

# Streamlit dashboard
st.title("User Clustering Dashboard")

# Sidebar for database connection
st.sidebar.header("Database Connection")
db_url = st.sidebar.text_input(
    "Database URL", "postgresql+psycopg2://postgres:Admin@localhost:5432/SQLTEST")

# Connect to database


@st.cache_data
def fetch_data():
    engine = create_engine(db_url)
    query = """
    WITH UserOrderStats AS (
        SELECT 
            gc.user_id,
            COUNT(o.id) AS order_count,
            SUM(o.total_amount) AS total_order_amount
        FROM 
            public.orders o
        JOIN 
            public.groups_carts gc ON o.groups_carts_id = gc.id
        GROUP BY 
            gc.user_id
    )
    SELECT 
        user_id, 
        order_count, 
        total_order_amount
    FROM 
        UserOrderStats;
    """
    return pd.read_sql(query, engine)


try:
    data = fetch_data()
    st.sidebar.success("Data fetched successfully!")
except Exception as e:
    st.sidebar.error(f"Error connecting to the database: {e}")
    st.stop()

# Sidebar for clustering settings
st.sidebar.header("Clustering Settings")
n_clusters = st.sidebar.slider(
    "Number of Clusters", min_value=2, max_value=10, value=3, step=1)
random_state = st.sidebar.number_input("Random State", value=42, step=1)

# Preprocess data
data = data.dropna().drop_duplicates()

# Apply K-Means clustering
kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
data['cluster'] = kmeans.fit_predict(
    data[['order_count', 'total_order_amount']])

# Display clustering data
st.header("Clustering Results")
st.dataframe(data)

# Visualize clusters
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

# Additional visualizations
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

# Save clustering results
if st.sidebar.button("Save Clustering Results"):
    engine = create_engine(db_url)
    data[['user_id', 'cluster']].to_sql(
        'user_clusters', engine, if_exists='replace', index=False)
    st.sidebar.success("Clustering results saved to database!")

# Download results as CSV
st.sidebar.header("Download Results")


@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')


csv_data = convert_df_to_csv(data)
st.sidebar.download_button(label="Download CSV", data=csv_data,
                           file_name="user_clusters.csv", mime="text/csv")
