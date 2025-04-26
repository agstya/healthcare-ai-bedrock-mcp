import pandas as pd
import psycopg2
from psycopg2 import sql
import os
import glob

def load_csv_to_postgres(csv_file_path, schema="public", db_config=None):
    """
    Load a CSV file into a PostgreSQL database table within a specified schema. Creates the table if it doesn't exist.

    Args:
        csv_file_path (str): Path to the CSV file.
        schema (str): Schema name where the table will be created. Defaults to "public".
        db_config (dict): Database configuration with keys: host, dbname, user, password, port.
    """
    # Set table name to the CSV file name (without extension)
    table_name = os.path.splitext(os.path.basename(csv_file_path))[0]

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        host=db_config['host'],
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        port=db_config['port']
    )
    cursor = conn.cursor()

    # Ensure the schema exists
    cursor.execute(sql.SQL(f"CREATE SCHEMA IF NOT EXISTS {schema};"))

    # Create the table if it doesn't exist
    columns = ", ".join([f"{col} TEXT" for col in df.columns])
    create_table_query = sql.SQL(
        f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} ({columns});"
    )
    cursor.execute(create_table_query)

    # Insert data into the table
    for _, row in df.iterrows():
        placeholders = ", ".join(["%s"] * len(row))
        insert_query = sql.SQL(
            f"INSERT INTO {schema}.{table_name} VALUES ({placeholders});"
        )
        cursor.execute(insert_query, tuple(row))

    # Commit changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

def load_all_csvs_in_folder(folder_path, schema="public", db_config=None):
    """
    Load all CSV files in a folder into a PostgreSQL database.

    Args:
        folder_path (str): Path to the folder containing CSV files.
        schema (str): Schema name where the tables will be created. Defaults to "public".
        db_config (dict): Database configuration with keys: host, dbname, user, password, port.
    """
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    for csv_file in csv_files:
        print(f"Loading {csv_file} into schema '{schema}'...")
        load_csv_to_postgres(csv_file, schema=schema, db_config=db_config)

# Example usage
if __name__ == "__main__":
    db_config = {
        "host": "localhost",
        "dbname": "synthea",
        "user": "postgres",
        "password": "postgres",
        "port": 5432
    }
    folder_path = "data/synthea/synthea_sample_data_csv_latest"
    
    # Load all CSV files in the folder into the "public" schema
    load_all_csvs_in_folder(folder_path, schema="public", db_config=db_config)
