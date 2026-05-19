"""
mining.py — Frequent Pattern Mining with Apriori algorithm

Each Pokémon becomes a basket of item tokens:
  primary type, secondary type presence, stat tier, generation group, legendary status.
Applies Apriori and generates association rules sorted by lift.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from pathlib import Path

CLEAN_INPUT  = Path(__file__).parent.parent / "data" / "cleaned_pokemon.csv"
RULES_OUTPUT = Path(__file__).parent.parent / "output" / "association_rules.csv"
LIFT_CHART   = Path(__file__).parent.parent / "visuals" / "association_lift.png"


def build_transactions(df: pd.DataFrame) -> list[list[str]]:
    transactions = []
    for _, row in df.iterrows():
        total = row["total"]
        if total < 300:
            tier_tok = "tier=VeryWeak"
        elif total < 400:
            tier_tok = "tier=Weak"
        elif total < 500:
            tier_tok = "tier=Average"
        elif total < 600:
            tier_tok = "tier=Strong"
        else:
            tier_tok = "tier=Uber"

        gen = int(row["generation"])
        if gen <= 3:
            gen_tok = "gen=Early(1-3)"
        elif gen <= 6:
            gen_tok = "gen=Mid(4-6)"
        else:
            gen_tok = "gen=Recent(7-9)"

        items = [
            f"type1={row['type1']}",
            tier_tok,
            gen_tok,
            f"dual_type={'Yes' if row['type2'] != 'None' else 'No'}",
            f"legendary={'Yes' if int(row['is_legendary']) == 1 else 'No'}",
        ]
        transactions.append(items)
    return transactions


def run_apriori(df: pd.DataFrame = None) -> pd.DataFrame:
    print("=" * 60)
    print("STEP 4: FREQUENT PATTERN MINING (Apriori)")
    print("=" * 60)

    if df is None:
        df = pd.read_csv(CLEAN_INPUT)

    transactions = build_transactions(df)
    print(f"\n  Total transactions: {len(transactions)}")
    print(f"  Sample basket: {transactions[0]}")

    te = TransactionEncoder()
    basket_df = pd.DataFrame(te.fit_transform(transactions), columns=te.columns_)
    print(f"  One-hot matrix shape: {basket_df.shape}")

    frequent_itemsets = apriori(basket_df, min_support=0.05, use_colnames=True)
    frequent_itemsets["length"] = frequent_itemsets["itemsets"].apply(len)
    print(f"\n  Frequent itemsets found: {len(frequent_itemsets)}")

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.3)
    rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)
    print(f"  Association rules generated: {len(rules)}")

    cols = ["antecedents", "consequents", "support", "confidence", "lift"]
    print("\n  --- Top 5 rules by lift ---")
    print(rules[cols].head(5).to_string())

    RULES_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rules_csv = rules.copy()
    rules_csv["antecedents"] = rules_csv["antecedents"].apply(lambda x: ", ".join(sorted(x)))
    rules_csv["consequents"] = rules_csv["consequents"].apply(lambda x: ", ".join(sorted(x)))
    rules_csv.to_csv(RULES_OUTPUT, index=False)
    print(f"\n  Rules saved to: {RULES_OUTPUT}")

    _plot_lift(rules.head(15))
    return rules


def _plot_lift(rules: pd.DataFrame):
    LIFT_CHART.parent.mkdir(parents=True, exist_ok=True)
    plot_df = rules.copy()
    plot_df["rule_label"] = (
        plot_df["antecedents"].apply(lambda x: ", ".join(sorted(x)))
        + " → "
        + plot_df["consequents"].apply(lambda x: ", ".join(sorted(x)))
    )

    fig, ax = plt.subplots(figsize=(14, 7))
    colors = sns.color_palette("viridis", len(plot_df))
    bars   = ax.barh(plot_df["rule_label"], plot_df["lift"], color=colors)
    ax.axvline(x=1.0, color="red", linestyle="--", linewidth=1.2, label="Lift = 1 (random)")
    ax.set_xlabel("Lift", fontsize=13)
    ax.set_title("Top Association Rules by Lift — Pokémon", fontsize=15, fontweight="bold")
    ax.legend()
    ax.invert_yaxis()

    for bar, val in zip(bars, plot_df["lift"]):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(LIFT_CHART, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Lift chart saved to: {LIFT_CHART}")


if __name__ == "__main__":
    run_apriori()
