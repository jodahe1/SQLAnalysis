# Create a reusable Python class to preprocess and normalize data for all tables 
# (e.g., handling NULLs, encoding categorical variables, aggregating timestamps 
# to periods).

import psycopg2
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sklearn.preprocessing import LabelEncoder
from dateutil import parser


class DataPreprocessor:
    def __init__(self, db_config):
        db_string = "postgresql://{}:{}@{}:{}/{}".format(
            db_config['user'], db_config['password'], db_config['host'], '5432', db_config['database'])
        self.engine = create_engine(db_string)
        self.inspector = inspect(self.engine)
        self.table_configs = {}

    def auto_generate_config(self, table_name):
        columns = self.inspector.get_columns(table_name)
        config = {'categorical_cols': [], 'timestamp_cols': []}
        for col in columns:
            col_name = col['name']

            col_type = str(col['type'])

            if 'VARCHAR' in col_type or 'TEXT' in col_type and col['name'] not in ['description', 'notes', 'comments']:
                config['categorical_cols'].append(col_name)
            if 'TIMESTAMP' in col_type or 'DATE' in col_type:
                config['timestamp_cols'].append(col_name)
        return config

    def add_table_config(self, table_name, config):
        self.table_configs[table_name] = config

    def preprocess_table(self, table_name):
        if table_name not in self.table_configs:
            print(
                f"Warning: No configuration found for table '{table_name}'. Using auto-generated config.")
            self.table_configs[table_name] = self.auto_generate_config(
                table_name)

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


table_names = preprocessor.inspector.get_table_names()

for table_name in table_names:
    preprocessed_df = preprocessor.preprocess_table(table_name)
    if preprocessed_df is not None:
        preprocessed_df.to_csv(f"{table_name}_preprocessed.csv", index=False)
        print(f"Preprocessed '{table_name}' successfully.")

preprocessor.close_connection()
