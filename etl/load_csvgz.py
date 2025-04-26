import os
import gzip
import pandas as pd
import psycopg2
from psycopg2 import sql

# --- PLACEHOLDER: Fill in your Postgres connection details ---
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'mimiciv'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'


def get_csv_gz_files(directory):
    """Return a list of all .csv.gz files in the directory."""
    return [f for f in os.listdir(directory) if f.endswith('.csv.gz')]


def get_table_name(filename):
    """Generate table name from filename (remove .csv.gz)."""
    return os.path.splitext(os.path.splitext(filename)[0])[0]


def create_table_if_not_exists(conn, table_name, columns):
    """Create a table with the given columns if it does not exist."""
    col_defs = ', '.join([f'"{col}" TEXT' for col in columns])
    query = sql.SQL('CREATE TABLE IF NOT EXISTS {} ({});').format(
        sql.Identifier(table_name),
        sql.SQL(col_defs)
    )
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()


def load_csv_to_postgres(conn, table_name, df):
    """Bulk load a DataFrame into the specified Postgres table."""
    from io import StringIO
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    with conn.cursor() as cur:
        cur.copy_expert(
            sql.SQL('COPY {} FROM STDIN WITH CSV').format(sql.Identifier(table_name)),
            buffer
        )
    conn.commit()


def main():
    directory = '.'
    files = get_csv_gz_files(directory)
    if not files:
        print(f'{YELLOW}No .csv.gz files found in the current directory.{RESET}')
        return

    print(f'{CYAN}Connecting to the database...{RESET}')
    # Connect to the database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    for idx, filename in enumerate(files, 1):
        table_name = get_table_name(filename)
        print(f'{CYAN}[{idx}/{len(files)}] Processing {filename} into table {table_name}...{RESET}')
        with gzip.open(os.path.join(directory, filename), 'rt') as f:
            df = pd.read_csv(f)
        create_table_if_not_exists(conn, table_name, df.columns)
        load_csv_to_postgres(conn, table_name, df)
        print(f'{GREEN}Loaded {len(df)} rows into {table_name}.{RESET}')

    conn.close()
    print(f'{GREEN}All files loaded successfully!{RESET}')

if __name__ == '__main__':
    main()
