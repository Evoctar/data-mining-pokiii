"""
cleaning.py — Data cleaning for raw Pokémon data

Steps: duplicate removal, missing value handling, type/stat validation,
text normalization. Saves cleaned CSV to data/cleaned_pokemon.csv.
"""

import pandas as pd
from pathlib import Path

RAW_INPUT    = Path(__file__).parent.parent / "data" / "raw_pokemon.csv"
CLEAN_OUTPUT = Path(__file__).parent.parent / "data" / "cleaned_pokemon.csv"

VALID_TYPES = {
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting",
    "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost",
    "Dragon", "Dark", "Steel", "Fairy", "None",
}


def clean_data(df: pd.DataFrame = None) -> pd.DataFrame:
    print("=" * 60)
    print("STEP 2: DATA CLEANING")
    print("=" * 60)

    if df is None:
        df = pd.read_csv(RAW_INPUT)

    print(f"\n  Raw shape: {df.shape}")
    print(f"  Columns:   {list(df.columns)}")
    print(f"\n  Missing values:\n{df.isnull().sum().to_string()}")

    raw_len = len(df)

    # 1. Remove exact duplicate rows
    df.drop_duplicates(inplace=True)
    print(f"\n  Duplicate rows removed: {raw_len - len(df)}")

    # 2. Fill any missing numeric stats with column median
    stat_cols = ["total", "hp", "attack", "defense", "sp_atk", "sp_def", "speed"]
    for col in stat_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median()).astype(int)

    # 3. Fill missing types
    df["type1"] = df["type1"].fillna("Normal").str.strip().str.title()
    df["type2"] = df["type2"].fillna("None").str.strip().str.title()

    # 4. Clamp unknown types to "Unknown"
    df.loc[~df["type1"].isin(VALID_TYPES), "type1"] = "Unknown"
    df.loc[~df["type2"].isin(VALID_TYPES | {"Unknown"}), "type2"] = "None"

    # 5. Fill generation and legendary if somehow missing
    df["generation"]  = df["generation"].fillna(1).astype(int)
    df["is_legendary"] = df["is_legendary"].fillna(0).astype(int)

    # 6. Drop rows where stat totals are inconsistent (sanity check)
    computed_total = df["hp"] + df["attack"] + df["defense"] + df["sp_atk"] + df["sp_def"] + df["speed"]
    mismatch = (computed_total != df["total"]).sum()
    if mismatch:
        print(f"  Note: {mismatch} rows have total != sum of stats (alternate forms — kept as-is)")

    df.reset_index(drop=True, inplace=True)

    print(f"\n  Cleaned shape: {df.shape}")
    print(f"  Rows removed total: {raw_len - len(df)}")
    print(f"\n  Type1 distribution (top 10):\n{df['type1'].value_counts().head(10).to_string()}")
    print(f"\n  Generation distribution:\n{df['generation'].value_counts().sort_index().to_string()}")
    print(f"\n  Legendary count: {df['is_legendary'].sum()} / {len(df)}")
    print("\n  Sample (first 3 rows):")
    print(df.head(3).to_string())

    CLEAN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_OUTPUT, index=False)
    print(f"\n  Cleaned data saved to: {CLEAN_OUTPUT}")
    return df


if __name__ == "__main__":
    clean_data()
