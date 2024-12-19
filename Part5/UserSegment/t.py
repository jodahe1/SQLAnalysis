import pandas as pd

# Function to get columns of a CSV file


def get_columns_from_csv(file_path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Return the columns of the DataFrame
    return df.columns.tolist()


# File paths
groups_carts_file = 'C:/Users/huawei/Desktop/SQLAnalysis/Part5/UserSegment/groups_carts.csv'
orders_file = 'C:/Users/huawei/Desktop/SQLAnalysis/Part5/UserSegment/orders.csv'

# Get columns from both CSVs
groups_carts_columns = get_columns_from_csv(groups_carts_file)
orders_columns = get_columns_from_csv(orders_file)

# Print the columns
print(f"Columns in groups_carts.csv: {groups_carts_columns}")
print(f"Columns in orders.csv: {orders_columns}")
