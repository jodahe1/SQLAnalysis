import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
from dateutil import parser


class DataPreprocessor:
    def __init__(self, db_config):

        db_string = "postgresql://{}:{}@{}:{}/{}".format(
            db_config['user'], db_config['password'], db_config['host'], '5432', db_config['database'])
        self.engine = create_engine(db_string)
        self.table_configs = {}

    def add_table_config(self, table_name, config):
        self.table_configs[table_name] = config

    def preprocess_table(self, table_name):
        if table_name not in self.table_configs:
            raise ValueError(
                f"No configuration found for table '{table_name}'")

        config = self.table_configs[table_name]
        try:

            df = pd.read_sql_table(table_name, self.engine)

            for col in df.columns:
                if df[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = df[col].fillna(0)
                    else:
                        df[col] = df[col].fillna('')

            for col in config.get('categorical_cols', []):
                if col in df.columns:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col])
                else:
                    print(
                        f"Warning: Column '{col}' not found in table '{table_name}'. Skipping encoding.")

            for col in config.get('timestamp_cols', []):
                if col in df.columns:
                    try:
                        df[col] = pd.to_datetime(df[col])
                        df[col] = df[col].dt.date
                    except:
                        print(
                            f"Warning: Could not convert column '{col}' to datetime in table '{table_name}'. Check data type.")
                else:
                    print(
                        f"Warning: Column '{col}' not found in table '{table_name}'. Skipping timestamp aggregation.")

            return df
        except Exception as e:
            print(f"Error reading or processing table '{table_name}': {e}")
            return None

    def close_connection(self):
        self.engine.dispose()


db_config = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}

preprocessor = DataPreprocessor(db_config)


preprocessor.add_table_config('products', {

    'categorical_cols': ['category_id', 'vendor_id'],

    'timestamp_cols': ['created_at', 'updated_at']
})

preprocessor.add_table_config('orders', {

    'categorical_cols': ['status', 'payment_method_id'],

    'timestamp_cols': ['order_date', 'delivery_date']
})


for table_name in preprocessor.table_configs:
    preprocessed_df = preprocessor.preprocess_table(table_name)
    if preprocessed_df is not None:
        preprocessed_df.to_csv(f"{table_name}_preprocessed.csv", index=False)
        print(f"Preprocessed '{table_name}' successfully.")

preprocessor.close_connection()
