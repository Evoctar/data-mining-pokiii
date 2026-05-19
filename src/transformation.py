"""
transformation.py — Feature engineering and encoding for Pokémon data

Adds stat_tier bucket, encodes types and generation,
adds has_second_type flag, and scales numeric stats to [0, 1].
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from pathlib import Path

CLEAN_INPUT        = Path(__file__).parent.parent / "data" / "cleaned_pokemon.csv"
TRANSFORMED_OUTPUT = Path(__file__).parent.parent / "data" / "transformed_pokemon.csv"

STAT_BINS   = [0, 299, 399, 499, 599, float("inf")]
STAT_LABELS = ["Very Weak", "Weak", "Average", "Strong", "Uber"]


def add_stat_tier(df: pd.DataFrame) -> pd.DataFrame:
    df["stat_tier"] = pd.cut(
        df["total"],
        bins=STAT_BINS,
        labels=STAT_LABELS,
        right=True,
    )
    return df


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    le_type1 = LabelEncoder()
    df["type1_encoded"] = le_type1.fit_transform(df["type1"])
    df["has_second_type"] = (df["type2"] != "None").astype(int)
    print(f"  Type1 classes ({len(le_type1.classes_)}): {list(le_type1.classes_)}")
    return df


def scale_features(df: pd.DataFrame) -> pd.DataFrame:
    stat_cols  = ["hp", "attack", "defense", "sp_atk", "sp_def", "speed", "total"]
    scaled_names = [f"{c}_scaled" for c in stat_cols]
    scaler = MinMaxScaler()
    df[scaled_names] = scaler.fit_transform(df[stat_cols])
    return df


def transform_data(df: pd.DataFrame = None) -> pd.DataFrame:
    print("=" * 60)
    print("STEP 3: DATA TRANSFORMATION")
    print("=" * 60)

    if df is None:
        df = pd.read_csv(CLEAN_INPUT)

    df = add_stat_tier(df)
    print(f"\n  Stat tier distribution:\n{df['stat_tier'].value_counts().sort_index().to_string()}")

    df = encode_features(df)
    df = scale_features(df)

    print(f"\n  Final columns: {list(df.columns)}")

    TRANSFORMED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(TRANSFORMED_OUTPUT, index=False)
    print(f"\n  Transformed data saved to: {TRANSFORMED_OUTPUT}")
    return df


if __name__ == "__main__":
    transform_data()
