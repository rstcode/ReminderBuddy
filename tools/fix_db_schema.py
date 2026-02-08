import sqlite3
from datetime import datetime
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so 'app' package imports work when running this script
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app.core.config import settings
DATABASE_URL = settings.DATABASE_URL


def get_db_path(url: str) -> str:
    # expects sqlite:///./reminder.db or sqlite:///absolute/path
    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "")
        return os.path.abspath(path)
    raise ValueError("Unsupported DATABASE_URL format")


def column_exists(conn, table: str, column: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    return column in cols


def add_column(conn, table: str, column_def: str):
    sql = f"ALTER TABLE {table} ADD COLUMN {column_def}"
    conn.execute(sql)


def main():
    db_path = get_db_path(DATABASE_URL)
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    try:
        added = []
        if not column_exists(conn, "reminder", "created_at"):
            add_column(conn, "reminder", "created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)")
            added.append("created_at")

        if not column_exists(conn, "reminder", "updated_at"):
            add_column(conn, "reminder", "updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP)")
            added.append("updated_at")

        if added:
            # set existing NULLs to current time
            now = datetime.utcnow().isoformat(sep=" ")
            conn.execute("UPDATE reminder SET created_at = ? WHERE created_at IS NULL", (now,))
            conn.execute("UPDATE reminder SET updated_at = ? WHERE updated_at IS NULL", (now,))
            conn.commit()
            print(f"Added columns: {', '.join(added)} and updated existing rows.")
        else:
            print("No changes needed; columns already exist.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
