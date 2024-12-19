# Write a Python script that fetches data from the database to calculate a monthly 
# cohort analysis of users, grouping them by their signup month (created_at) 
# and showing retention percentages based on their group deal participation over 
# the next 3 months.

import psycopg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


DB_CONFIG = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}


def fetch_user_data():
    """
    Connects to the PostgreSQL database and fetches user data for cohort analysis.
    Filters for participation data within 3 months of signup.
    """
    query = """
    SELECT 
        users.id AS user_id,
        users.created_at AS signup_date,
        groups.created_at AS participation_date
    FROM 
        users
    JOIN 
        groups ON users.id = groups.created_by
    WHERE 
        users.created_at IS NOT NULL
        AND groups.created_at IS NOT NULL
        AND groups.created_at <= users.created_at + INTERVAL '3 months';
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        df = pd.read_sql_query(query, conn)
        conn.close()
        logging.info("Data fetched successfully from the database.")
        return df
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return None


def preprocess_data(df):
    """
    Preprocess the data to extract monthly cohorts and participation flags.
    """
    try:

        df['signup_date'] = pd.to_datetime(df['signup_date'])
        df['participation_date'] = pd.to_datetime(df['participation_date'])
        df['cohort_month'] = df['signup_date'].dt.to_period('M')
        df['months_after_signup'] = (
            df['participation_date'] - df['signup_date']).dt.days // 30

        logging.info("Data preprocessing completed.")
        return df
    except Exception as e:
        logging.error(f"Error during data preprocessing: {e}")
        return None


def calculate_cohorts(df):
    """
    Calculate monthly cohort retention based on participation in group deals.
    """
    try:
        cohort_pivot = df.pivot_table(
            index='cohort_month',
            columns='months_after_signup',
            values='user_id',
            aggfunc='count'
        )
        cohort_pivot = cohort_pivot.fillna(0)

        cohort_pivot.columns = [f"Month {i+1}" for i in cohort_pivot.columns]
        cohort_size = cohort_pivot.iloc[:, 0]
        retention = cohort_pivot.divide(
            cohort_size, axis=0) * 100

        logging.info("Cohort retention calculation completed.")
        return retention, cohort_pivot
    except Exception as e:
        logging.error(f"Error during cohort calculation: {e}")
        return None, None


def save_to_csv(df, filename):
    """
    Save the retention DataFrame to a CSV file.
    """
    try:
        df.to_csv(filename)
        logging.info(f"Retention analysis saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")


def visualize_cohorts(retention):
    """
    Generate a heatmap for cohort retention analysis.
    """
    try:
        plt.figure(figsize=(10, 6))
        sns.heatmap(retention, annot=True, fmt=".1f", cmap="YlGnBu")
        plt.title("Monthly Cohort Retention Analysis")
        plt.xlabel("Months After Signup")
        plt.ylabel("Cohort Month")
        plt.tight_layout()
        plt.savefig('cohort_retention_heatmap.png')
        plt.show()
        logging.info("Heatmap saved as cohort_retention_heatmap.png.")
    except Exception as e:
        logging.error(f"Error during visualization: {e}")


def main():
    user_data = fetch_user_data()
    if user_data is None:
        return

    processed_data = preprocess_data(user_data)
    if processed_data is None:
        return

    retention_df, cohort_pivot = calculate_cohorts(processed_data)
    if retention_df is None:
        return

    save_to_csv(retention_df, 'monthly_cohort_analysis.csv')
    visualize_cohorts(retention_df)


if __name__ == '__main__':
    main()
