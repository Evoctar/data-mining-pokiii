"""
clustering.py — KMeans clustering on Pokémon stat profiles

Features: all 6 base stats (hp, attack, defense, sp_atk, sp_def, speed) scaled.
Elbow method selects optimal k. PCA projects to 2D for visualization.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path

CLEAN_INPUT            = Path(__file__).parent.parent / "data" / "cleaned_pokemon.csv"
CLUSTER_SCATTER        = Path(__file__).parent.parent / "visuals" / "cluster_scatter.png"
ELBOW_CHART            = Path(__file__).parent.parent / "visuals" / "elbow_chart.png"
CLUSTER_SUMMARY_OUTPUT = Path(__file__).parent.parent / "output" / "cluster_summary.csv"

STAT_FEATURES = ["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]


def find_optimal_k(X: np.ndarray, k_range: range) -> int:
    inertias = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X)
        inertias.append(km.inertia_)

    ELBOW_CHART.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(list(k_range), inertias, marker="o", linewidth=2, color="steelblue")
    ax.set_xlabel("Number of Clusters (k)", fontsize=13)
    ax.set_ylabel("Inertia (Within-cluster SSE)", fontsize=13)
    ax.set_title("Elbow Method — Optimal k Selection (Pokémon Stats)", fontsize=14, fontweight="bold")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ELBOW_CHART, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Elbow chart saved to: {ELBOW_CHART}")

    deltas = [inertias[i] - inertias[i + 1] for i in range(len(inertias) - 1)]
    return list(k_range)[deltas.index(max(deltas)) + 1]


def run_clustering(df: pd.DataFrame = None) -> pd.DataFrame:
    print("=" * 60)
    print("STEP 5: CLUSTERING (KMeans)")
    print("=" * 60)

    if df is None:
        df = pd.read_csv(CLEAN_INPUT)

    scaler = MinMaxScaler()
    X = scaler.fit_transform(df[STAT_FEATURES])

    print("\n  Running elbow method (k = 2 to 8)...")
    optimal_k = find_optimal_k(X, range(2, 9))
    print(f"  Suggested optimal k: {optimal_k}")

    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X)

    summary = df.groupby("cluster").agg(
        count=("name", "count"),
        avg_total=("total", "mean"),
        avg_hp=("hp", "mean"),
        avg_attack=("attack", "mean"),
        avg_defense=("defense", "mean"),
        avg_speed=("speed", "mean"),
        legendary_count=("is_legendary", "sum"),
        top_type=("type1", lambda x: x.mode()[0]),
    ).round(1)
    print(f"\n  Cluster Summary:\n{summary.to_string()}")

    CLUSTER_SUMMARY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(CLUSTER_SUMMARY_OUTPUT)
    print(f"\n  Cluster summary saved to: {CLUSTER_SUMMARY_OUTPUT}")

    pca = PCA(n_components=2, random_state=42)
    X_pca    = pca.fit_transform(X)
    explained = pca.explained_variance_ratio_
    print(f"  PCA explained variance: PC1={explained[0]:.2%}, PC2={explained[1]:.2%}")

    _plot_clusters(X_pca, df["cluster"], df["is_legendary"], optimal_k, explained)
    return df


def _plot_clusters(X_pca, labels, legendary, k, explained):
    CLUSTER_SCATTER.parent.mkdir(parents=True, exist_ok=True)
    palette = sns.color_palette("tab10", k)

    fig, ax = plt.subplots(figsize=(10, 7))
    for cid in range(k):
        mask = labels == cid
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
                   c=[palette[cid]], label=f"Cluster {cid}",
                   alpha=0.5, s=30, edgecolors="none")

    # Highlight legendaries
    leg_mask = legendary == 1
    ax.scatter(X_pca[leg_mask, 0], X_pca[leg_mask, 1],
               c="gold", marker="*", s=120, zorder=5,
               label="Legendary/Mythical", edgecolors="black", linewidths=0.4)

    ax.set_xlabel(f"PC1 ({explained[0]:.1%} var)", fontsize=12)
    ax.set_ylabel(f"PC2 ({explained[1]:.1%} var)", fontsize=12)
    ax.set_title(f"KMeans Clustering (k={k}) — Pokémon Stat Profiles (PCA)",
                 fontsize=14, fontweight="bold")
    ax.legend(title="Cluster", fontsize=9)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(CLUSTER_SCATTER, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Cluster scatter saved to: {CLUSTER_SCATTER}")


if __name__ == "__main__":
    run_clustering()
