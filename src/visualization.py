"""
visualization.py — Summary visualizations for Pokémon dataset

Generates: total distribution, type counts, stats by legendary status,
generation distribution, and a 4-panel summary dashboard.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

CLEAN_INPUT = Path(__file__).parent.parent / "data" / "cleaned_pokemon.csv"
VISUALS_DIR = Path(__file__).parent.parent / "visuals"


def plot_total_distribution(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(df["total"], bins=30, kde=True, color="steelblue", ax=ax)
    ax.axvline(df["total"].mean(), color="red", linestyle="--",
               label=f"Mean = {df['total'].mean():.0f}")
    ax.set_xlabel("Base Stat Total", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Distribution of Pokémon Base Stat Totals", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    path = VISUALS_DIR / "total_distribution.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_type_counts(df: pd.DataFrame):
    counts = df["type1"].value_counts()
    palette = sns.color_palette("tab20", len(counts))
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(counts.index, counts.values, color=palette)
    ax.set_xlabel("Primary Type", fontsize=12)
    ax.set_ylabel("Number of Pokémon", fontsize=12)
    ax.set_title("Pokémon Count by Primary Type", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    path = VISUALS_DIR / "type_counts.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_stats_by_legendary(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    palette = {0: "steelblue", 1: "gold"}
    labels  = {0: "Regular", 1: "Legendary / Mythical"}
    for val in [0, 1]:
        subset = df[df["is_legendary"] == val]["total"]
        ax.hist(subset, bins=25, alpha=0.65, label=labels[val],
                color=palette[val], edgecolor="white", linewidth=0.4)
    ax.set_xlabel("Base Stat Total", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Base Stat Total — Regular vs Legendary Pokémon",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    path = VISUALS_DIR / "stats_by_legendary.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_generation_counts(df: pd.DataFrame):
    counts = df["generation"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([f"Gen {g}" for g in counts.index], counts.values,
           color=sns.color_palette("muted", len(counts)))
    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Number of Entries", fontsize=12)
    ax.set_title("Pokémon Entries per Generation", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    path = VISUALS_DIR / "generation_counts.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_dashboard(df: pd.DataFrame):
    fig = plt.figure(figsize=(16, 10))
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # Panel 1: total distribution
    ax1 = fig.add_subplot(gs[0, 0])
    sns.histplot(df["total"], bins=25, kde=True, color="steelblue", ax=ax1)
    ax1.set_title("Base Stat Total Distribution", fontweight="bold")
    ax1.set_xlabel("Total")

    # Panel 2: type counts (top 10)
    ax2 = fig.add_subplot(gs[0, 1])
    top_types = df["type1"].value_counts().head(10)
    ax2.barh(top_types.index[::-1], top_types.values[::-1],
             color=sns.color_palette("tab10", 10)[::-1])
    ax2.set_title("Top 10 Primary Types", fontweight="bold")
    ax2.set_xlabel("Count")

    # Panel 3: generation bar
    ax3 = fig.add_subplot(gs[1, 0])
    gen_counts = df["generation"].value_counts().sort_index()
    ax3.bar([f"G{g}" for g in gen_counts.index], gen_counts.values,
            color=sns.color_palette("muted", len(gen_counts)))
    ax3.set_title("Pokémon per Generation", fontweight="bold")
    ax3.set_xlabel("Generation")

    # Panel 4: legendary pie
    ax4 = fig.add_subplot(gs[1, 1])
    leg_counts = df["is_legendary"].value_counts().sort_index()
    ax4.pie(leg_counts.values,
            labels=["Regular", "Legendary/Mythical"],
            autopct="%1.1f%%",
            colors=["steelblue", "gold"],
            startangle=90,
            textprops={"fontsize": 11})
    ax4.set_title("Legendary Breakdown", fontweight="bold")

    fig.suptitle("Pokémon Dataset — Summary Dashboard", fontsize=18, fontweight="bold")
    path = VISUALS_DIR / "dashboard.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def run_visualizations(clean_df: pd.DataFrame = None, raw_df: pd.DataFrame = None):
    print("=" * 60)
    print("STEP 8: VISUALIZATIONS")
    print("=" * 60)

    VISUALS_DIR.mkdir(parents=True, exist_ok=True)

    if clean_df is None:
        clean_df = pd.read_csv(CLEAN_INPUT)

    print()
    plot_total_distribution(clean_df)
    plot_type_counts(clean_df)
    plot_stats_by_legendary(clean_df)
    plot_generation_counts(clean_df)
    plot_dashboard(clean_df)

    print("\n  All visualizations saved to visuals/")


if __name__ == "__main__":
    run_visualizations()
