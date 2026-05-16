#!/usr/bin/env python3
"""Delete all contacts from the Field Day database."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db

def main():
    answer = input("Delete ALL contacts from the database? [y/N]: ").strip().lower()
    if answer != "y":
        print("Aborted.")
        return

    with db._connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM DXLOG").fetchone()[0]
        conn.execute("DELETE FROM DXLOG")
        conn.commit()

    print(f"Deleted {count} contact(s).")

if __name__ == "__main__":
    main()
