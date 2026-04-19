# database.py
# Handles all database operations: connect, query, fetch table info

import sqlite3
import pandas as pd
import traceback


def get_connection(db_path="company.db"):
    """Returns a sqlite3 connection object."""
    return sqlite3.connect(db_path)


def execute_query(sql: str, db_path="company.db"):
    """
    Executes a SQL query and returns:
      - (DataFrame, None)   on success
      - (None, error_str)   on failure
    """
    try:
        conn = get_connection(db_path)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, f"SQL Error: {str(e)}\n\n{traceback.format_exc()}"


def get_all_tables(db_path="company.db"):
    """Returns a list of all table names in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_table_preview(table_name: str, db_path="company.db", limit=5):
    """Returns the first `limit` rows of a table as a DataFrame."""
    df, err = execute_query(f"SELECT * FROM {table_name} LIMIT {limit};", db_path)
    return df, err


def get_table_columns(table_name: str, db_path="company.db"):
    """Returns column names and types for a given table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    cols = cursor.fetchall()
    conn.close()
    # Returns list of (cid, name, type, notnull, default, pk)
    return [(c[1], c[2]) for c in cols]


def is_safe_query(sql: str) -> bool:
    """
    Basic safety check — only allow SELECT statements.
    Blocks DROP, DELETE, INSERT, UPDATE, etc.
    """
    sql_upper = sql.strip().upper()
    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "CREATE"]
    if not sql_upper.startswith("SELECT"):
        return False
    for keyword in dangerous:
        if keyword in sql_upper:
            return False
    return True


if __name__ == "__main__":
    # Quick test
    from sample_data import create_sample_database
    create_sample_database()

    print("Tables:", get_all_tables())
    print("\nEmployee columns:", get_table_columns("employees"))

    df, err = execute_query("SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 5;")
    if err:
        print("Error:", err)
    else:
        print("\nTop 5 Earners:")
        print(df.to_string(index=False))