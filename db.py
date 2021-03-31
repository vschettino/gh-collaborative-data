# Module Imports
import os
import sys

import mariadb
from retry import retry


# Connect to MariaDB Platform
@retry(tries=3, delay=2)
def connection() -> "mariadb.connection":
    try:
        conn = mariadb.connect(
            user="root",
            password=os.getenv("MYSQL_ROOT_PASSWORD"),
            host="db",
            port=3306,
            database="mysql",
        )
        print(type(conn))
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
