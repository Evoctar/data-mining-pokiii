"""
database.py — SQLite storage for cleaned Pokémon data

Creates database/pokemon.db, inserts all records,
and runs 4 example analytical SQL queries.
"""

import sqlite3
import pandas as pd
from pathlib import Path

CLEAN_INPUT = Path(__file__).parent.parent / "data" / "cleaned_pokemon.csv"
DB_PATH     = Path(__file__).parent.parent / "database" / "pokemon.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS pokemon (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    number       INTEGER NOT NULL,
    name         TEXT    NOT NULL,
    type1        TEXT    NOT NULL,
    type2        TEXT,
    total        INTEGER NOT NULL,
    hp           INTEGER NOT NULL,
    attack       INTEGER NOT NULL,
    defense      INTEGER NOT NULL,
    sp_atk       INTEGER NOT NULL,
    sp_def       INTEGER NOT NULL,
    speed        INTEGER NOT NULL,
    generation   INTEGER NOT NULL,
    is_legendary INTEGER NOT NULL DEFAULT 0
);
"""

EXAMPLE_QUERIES = [
    (
        "Top 10 highest base-stat total Pokémon",
        """SELECT name, total, type1, type2
           FROM pokemon ORDER BY total DESC LIMIT 10;""",
    ),
    (
        "Average stats by primary type",
        """SELECT type1,
                  COUNT(*)        AS count,
                  ROUND(AVG(total),1)   AS avg_total,
                  ROUND(AVG(attack),1)  AS avg_attack,
                  ROUND(AVG(speed),1)   AS avg_speed
           FROM pokemon GROUP BY type1 ORDER BY avg_total DESC LIMIT 10;""",
    ),
    (
        "Legendary count per generation",
        """SELECT generation,
                  COUNT(*) AS total_pokemon,
                  SUM(is_legendary) AS legendary_count
           FROM pokemon GROUP BY generation ORDER BY generation;""",
    ),
    (
        "Dual-type vs mono-type breakdown",
        """SELECT
             CASE WHEN type2 = 'None' THEN 'Mono-type' ELSE 'Dual-type' END AS typing,
             COUNT(*) AS count
           FROM pokemon GROUP BY typing;""",
    ),
]

DB_COLS = ["number", "name", "type1", "type2", "total", "hp", "attack",
           "defense", "sp_atk", "sp_def", "speed", "generation", "is_legendary"]


def run_database(df: pd.DataFrame = None):
    print("=" * 60)
    print("STEP 7: SQLITE DATABASE")
    print("=" * 60)

    if df is None:
        df = pd.read_csv(CLEAN_INPUT)

    cols  = [c for c in DB_COLS if c in df.columns]
    df_db = df[cols].copy()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    print(f"\n  Database created at: {DB_PATH}")

    placeholders = ", ".join("?" for _ in cols)
    insert_sql   = f"INSERT INTO pokemon ({', '.join(cols)}) VALUES ({placeholders});"
    cursor.executemany(insert_sql, df_db.itertuples(index=False, name=None))
    conn.commit()
    print(f"  Inserted {len(df_db)} rows into 'pokemon' table.")

    print("\n  --- Example SQL Queries ---")
    for description, query in EXAMPLE_QUERIES:
        print(f"\n  >> {description}")
        print(pd.read_sql_query(query, conn).to_string(index=False))

    conn.close()
    print(f"\n  Database closed. File: {DB_PATH}")


if __name__ == "__main__":
    run_database()
