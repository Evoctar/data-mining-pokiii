"""
classification.py — Predict whether a Pokémon is Legendary/Mythical

Target:  is_legendary (binary: 0 / 1)
Features: total, hp, attack, defense, sp_atk, sp_def, speed,
          type1_encoded, has_second_type, generation
Model:    Random Forest (100 trees)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from pathlib import Path

CLEAN_INPUT            = Path(__file__).parent.parent / "data" / "cleaned_pokemon.csv"
CONFUSION_MATRIX_CHART = Path(__file__).parent.parent / "visuals" / "confusion_matrix.png"
FEATURE_IMP_CHART      = Path(__file__).parent.parent / "visuals" / "feature_importance.png"
REPORT_OUTPUT          = Path(__file__).parent.parent / "output" / "classification_report.txt"

FEATURE_COLS = ["total", "hp", "attack", "defense", "sp_atk", "sp_def",
                "speed", "type1_encoded", "has_second_type", "generation"]


def prepare_features(df: pd.DataFrame):
    df = df.copy()
    le = LabelEncoder()
    df["type1_encoded"]  = le.fit_transform(df["type1"].astype(str))
    df["has_second_type"] = (df["type2"] != "None").astype(int)
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available]
    y = df["is_legendary"].astype(int)
    return X, y


def run_classification(df: pd.DataFrame = None) -> dict:
    print("=" * 60)
    print("STEP 6: CLASSIFICATION (Random Forest)")
    print("=" * 60)

    if df is None:
        df = pd.read_csv(CLEAN_INPUT)

    X, y = prepare_features(df)
    print(f"\n  Target distribution:\n{y.value_counts().rename({0: 'Regular', 1: 'Legendary'}).to_string()}")
    print(f"  Features: {list(X.columns)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n  Train: {len(X_train)} | Test: {len(X_test)}")

    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    acc    = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Regular", "Legendary"])
    print(f"\n  Accuracy: {acc:.4f}")
    print(f"\n  Classification Report:\n{report}")

    importances = pd.Series(clf.feature_importances_, index=X.columns).sort_values(ascending=False)
    print(f"  Feature importances:\n{importances.to_string()}")

    REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUTPUT.write_text(
        f"Random Forest Classification Report\n"
        f"Target: is_legendary (0=Regular, 1=Legendary/Mythical)\n"
        f"{'=' * 50}\n"
        f"Accuracy: {acc:.4f}\n\n{report}\n"
        f"Feature Importances:\n{importances.to_string()}\n",
        encoding="utf-8",
    )
    print(f"\n  Report saved to: {REPORT_OUTPUT}")

    labels_ordered = [0, 1]
    label_names    = ["Regular", "Legendary"]
    cm = confusion_matrix(y_test, y_pred, labels=labels_ordered)
    _plot_confusion_matrix(cm, label_names)
    _plot_feature_importance(importances)

    return {"accuracy": acc, "report": report, "model": clf}


def _plot_confusion_matrix(cm, labels):
    CONFUSION_MATRIX_CHART.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels,
                linewidths=0.5, ax=ax)
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("True", fontsize=12)
    ax.set_title("Confusion Matrix — Legendary Classification", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_CHART, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Confusion matrix saved to: {CONFUSION_MATRIX_CHART}")


def _plot_feature_importance(importances):
    FEATURE_IMP_CHART.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = sns.color_palette("Blues_r", len(importances))
    ax.barh(importances.index[::-1], importances.values[::-1], color=colors[::-1])
    ax.set_xlabel("Importance Score", fontsize=12)
    ax.set_title("Random Forest — Feature Importances\n(Predicting Legendary Status)",
                 fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FEATURE_IMP_CHART, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Feature importance chart saved to: {FEATURE_IMP_CHART}")


if __name__ == "__main__":
    run_classification()
