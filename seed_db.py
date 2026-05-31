"""Fallback DB seeding script that uses sqlite3 directly (no SQLAlchemy required).
Run with: python3 seed_db.py
"""
import os
import sqlite3

INITIAL_HISTORY = [
    ["milk", "bread", "eggs", "apples"],
    ["milk", "bread", "cereal"],
    ["eggs", "bread", "butter"],
    ["milk", "bread", "eggs", "butter"],
    ["milk", "cereal", "apples"],
    ["eggs", "butter"],
    ["milk", "bread", "eggs"],
]


def main():
    cwd = os.getcwd()
    db_path = os.path.join(cwd, 'shopper.db')
    print('Using DB:', db_path)
    if not os.path.exists(db_path):
        print('DB file not found; create tables using your app or Alembic and re-run this script.')
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Insert products
    all_names = set(name.strip().lower() for trip in INITIAL_HISTORY for name in trip)
    for name in all_names:
        cur.execute('INSERT OR IGNORE INTO products(name) VALUES (?)', (name,))

    # build name->id map
    cur.execute('SELECT id, name FROM products')
    prod_map = {name: pid for (pid, name) in cur.fetchall()}

    # insert trips and associations
    for trip_items in INITIAL_HISTORY:
        cur.execute('INSERT INTO trips DEFAULT VALUES')
        trip_id = cur.lastrowid
        for name in trip_items:
            pid = prod_map[name.strip().lower()]
            cur.execute('INSERT INTO trip_products(trip_id, product_id) VALUES (?, ?)', (trip_id, pid))

    conn.commit()

    cur.execute("SELECT count(*) FROM trips")
    print('trips after:', cur.fetchone()[0])
    cur.execute("SELECT count(*) FROM products")
    print('products after:', cur.fetchone()[0])
    cur.execute("SELECT count(*) FROM trip_products")
    print('trip_products after:', cur.fetchone()[0])

    conn.close()


if __name__ == '__main__':
    main()
