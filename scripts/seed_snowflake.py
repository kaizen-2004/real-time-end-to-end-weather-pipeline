import os
import snowflake.connector
from pathlib import Path

SNOWFLAKE_CONFIG = {
    "account": os.environ["SNOWFLAKE_ACCOUNT"],
    "user": os.environ["SNOWFLAKE_USER"],
    "password": os.environ["SNOWFLAKE_PASSWORD"],
}

SQL_DIR = Path(__file__).parent.parent / "sql" / "snowflake"


def run_sql_file(conn, filepath: Path):
    print(f"Running {filepath.name}...")
    with open(filepath) as f:
        sql = f.read()
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.cursor().execute(statement)
    print(f"  Completed {filepath.name}")


def main():
    # Connect without database to create it
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    try:
        cursor = conn.cursor()
        
        # Create database if not exists
        db_name = os.environ["SNOWFLAKE_DATABASE"]
        print(f"Creating database {db_name}...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"  Database {db_name} ready")
        
        # Create warehouse if not exists
        wh_name = os.environ.get("SNOWFLAKE_WAREHOUSE", "WEATHER_WH")
        print(f"Creating warehouse {wh_name}...")
        cursor.execute(f"""
            CREATE WAREHOUSE IF NOT EXISTS {wh_name}
            WITH WAREHOUSE_SIZE = 'XSMALL'
            AUTO_SUSPEND = 60
            AUTO_RESUME = TRUE
        """)
        print(f"  Warehouse {wh_name} ready")
        
        # Now connect to the database for schema creation
        conn.close()
        
        db_config = {**SNOWFLAKE_CONFIG, "database": db_name, "warehouse": wh_name}
        conn = snowflake.connector.connect(**db_config)
        
        for sql_file in sorted(SQL_DIR.glob("*.sql")):
            run_sql_file(conn, sql_file)
        
        print("\nSnowflake initialization complete!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
