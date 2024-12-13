# import psycopg2
# import pandas as pd
# from datetime import datetime

# # Database connection settings
# DB_CONFIG = {
#     'host': 'localhost',
#     'database': 'SQLTEST',
#     'user': 'postgres',
#     'password': 'Admin'
# }


# def fetch_user_data():
#     """
#     Connects to the PostgreSQL database and fetches user data for cohort analysis.
#     """
#     query = """
# SELECT
#     users.id AS user_id,
#     users.created_at AS signup_date,
#     groups.created_at AS participation_date
# FROM
#     users
# JOIN
#     groups ON users.id = groups.created_by
# WHERE
#     users.created_at IS NOT NULL
#     AND groups.created_at IS NOT NULL;
# """

#     try:
#         # Connect to the database
#         conn = psycopg2.connect(**DB_CONFIG)
#         # Load data into a Pandas DataFrame
#         df = pd.read_sql_query(query, conn)
#         conn.close()
#         return df
#     except Exception as e:
#         print("Error fetching data:", e)
#         return None


# def preprocess_data(df):
#     """
#     Preprocess the data to extract monthly cohorts and participation flags.
#     """
#     # Convert dates to datetime
#     df['signup_date'] = pd.to_datetime(df['signup_date'])
#     df['participation_date'] = pd.to_datetime(df['participation_date'])

#     # Extract signup month as cohort
#     df['cohort_month'] = df['signup_date'].dt.to_period('M')

#     # Calculate the month difference between signup and deal participation
#     df['months_after_signup'] = (
#         df['participation_date'] - df['signup_date']).dt.days // 30

#     return df


# def calculate_cohorts(df):
#     """
#     Calculate monthly cohort retention based on participation in group deals.
#     """
#     # Group users by cohort month and participation month
#     cohort_pivot = df.pivot_table(
#         index='cohort_month',
#         columns='months_after_signup',
#         values='user_id',
#         aggfunc='count'
#     )

#     # Rename columns to start at Month 1 instead of Month 0
#     cohort_pivot.columns = [f"Month {i+1}" for i in cohort_pivot.columns]

#     # Calculate retention percentages
#     cohort_size = cohort_pivot.iloc[:, 0]  # First column contains cohort size
#     retention = cohort_pivot.divide(cohort_size, axis=0) * 100  # Convert to percentage

#     return retention


# def save_to_csv(df, filename):
#     """
#     Save the retention DataFrame to a CSV file.
#     """
#     df.to_csv(filename)
#     print(f"Retention analysis saved to {filename}")


# def main():
#     # Fetch data from the database
#     user_data = fetch_user_data()
#     if user_data is None:
#         return

#     # Preprocess the data
#     processed_data = preprocess_data(user_data)

#     # Calculate cohorts
#     retention_df = calculate_cohorts(processed_data)

#     # Save the analysis to a CSV file
#     save_to_csv(retention_df, 'monthly_cohort_analysis.csv')


# if __name__ == '__main__':
#     main()


import psycopg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection settings
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
        # Convert dates to datetime
        df['signup_date'] = pd.to_datetime(df['signup_date'])
        df['participation_date'] = pd.to_datetime(df['participation_date'])

        # Extract signup month as cohort
        df['cohort_month'] = df['signup_date'].dt.to_period('M')

        # Calculate the month difference between signup and deal participation
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
        # Group users by cohort month and participation month
        cohort_pivot = df.pivot_table(
            index='cohort_month',
            columns='months_after_signup',
            values='user_id',
            aggfunc='count'
        )

        # Fill missing values with 0
        cohort_pivot = cohort_pivot.fillna(0)

        # Rename columns to start at Month 1 instead of Month 0
        cohort_pivot.columns = [f"Month {i+1}" for i in cohort_pivot.columns]

        # Calculate retention percentages
        # First column contains cohort size
        cohort_size = cohort_pivot.iloc[:, 0]
        retention = cohort_pivot.divide(
            cohort_size, axis=0) * 100  # Convert to percentage

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
    # Fetch data from the database
    user_data = fetch_user_data()
    if user_data is None:
        return

    # Preprocess the data
    processed_data = preprocess_data(user_data)
    if processed_data is None:
        return

    # Calculate cohorts
    retention_df, cohort_pivot = calculate_cohorts(processed_data)
    if retention_df is None:
        return

    # Save the analysis to a CSV file
    save_to_csv(retention_df, 'monthly_cohort_analysis.csv')

    # Visualize the retention analysis
    visualize_cohorts(retention_df)


if __name__ == '__main__':
    main()
