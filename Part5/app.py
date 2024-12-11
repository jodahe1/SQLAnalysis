import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Create a database connection
engine = create_engine('postgresql+psycopg2://postgres:Admin@localhost:5432/SQLTEST')

# Load data
query = """ -- Your SQL query here """
user_data = pd.read_sql(query, engine)

# Clustering code (as shown above)

# Streamlit dashboard
st.title('User Segmentation Dashboard')

# Display user data
st.subheader('User Data')
st.write(user_data)

# Visualize clusters
sns.scatterplot(data=user_data, x='order_count', y='total_order_amount', hue='cluster', palette='viridis')
st.pyplot()