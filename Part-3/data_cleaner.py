import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine

# PostgreSQL connection details
db_config = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}

# Connect to PostgreSQL and fetch data
def fetch_data_from_db():
    try:
        # Create the connection string
        conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        
        # Create a connection using SQLAlchemy
        engine = create_engine(conn_str)
        query = "SELECT created_at, total_amount FROM orders"  # Replace with your actual table name and columns
        
        # Fetch data into a pandas DataFrame
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Data cleaning function
def clean_data(df):
    if df is None:
        raise ValueError("No data fetched from the database.")

    # Ensure 'created_at' is a datetime column
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    
    # Remove rows with invalid dates (NaT)
    df = df.dropna(subset=['created_at'])

    # Group by the date (ignoring time) and sum 'total_amount' for each day
    df_daily = df.groupby(df['created_at'].dt.date)['total_amount'].sum().reset_index()

    # Rename columns to match Prophet's requirements
    df_daily.columns = ['date', 'total_amount']

    # Remove rows with non-positive 'total_amount'
    df_daily = df_daily[df_daily['total_amount'] > 0]

    # Apply log transformation to stabilize variance
    df_daily['total_amount'] = np.log1p(df_daily['total_amount'])

    return df_daily

# Save the cleaned data to a CSV file
def save_cleaned_data(df, output_file="orders_cleaned.csv"):
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")
    return df

# Main function to execute the process
def main():
    # Fetch data from PostgreSQL database
    df = fetch_data_from_db()

    # Clean the data
    cleaned_data = clean_data(df)

    # Save cleaned data
    save_cleaned_data(cleaned_data)

if __name__ == "__main__":
    main()
