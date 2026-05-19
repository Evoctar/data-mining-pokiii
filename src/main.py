"""
main.py — Pipeline orchestrator for the Pokémon data mining project

Runs all 9 steps in order with per-step timing and error handling.
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scraper          import run_scraper
from cleaning         import clean_data
from transformation   import transform_data
from mining           import run_apriori
from clustering       import run_clustering
from classification   import run_classification
from database         import run_database
from visualization    import run_visualizations
from report_generator import generate_report


def run_step(name: str, func, *args, **kwargs):
    """Execute a pipeline step with timing and graceful error handling."""
    t0     = time.time()
    result = None
    try:
        result  = func(*args, **kwargs)
        elapsed = time.time() - t0
        print(f"\n  [OK] {name} completed in {elapsed:.1f}s\n")
    except Exception as exc:
        elapsed = time.time() - t0
        print(f"\n  [ERROR] {name} failed after {elapsed:.1f}s: {exc}\n")
        import traceback
        traceback.print_exc()
    return result


def main():
    total_start = time.time()

    print("\n" + "=" * 60)
    print("  DATA MINING PIPELINE — pokemondb.net")
    print("=" * 60 + "\n")

    # Step 1: Scrape pokemondb.net full Pokédex table
    raw_df = run_step("Web Scraping", run_scraper)

    # Step 2: Clean
    clean_df = run_step("Data Cleaning", clean_data, raw_df)

    # Step 3: Transform (encode, scale, bucket)
    transformed_df = run_step("Data Transformation", transform_data, clean_df)

    # Step 4: Association rule mining
    run_step("Frequent Pattern Mining", run_apriori, clean_df)

    # Step 5: KMeans clustering on stat profiles
    run_step("Clustering", run_clustering, clean_df)

    # Step 6: Random Forest — predict legendary status
    run_step("Classification", run_classification, clean_df)

    # Step 7: SQLite database
    run_step("SQLite Database", run_database, clean_df)

    # Step 8: All visualizations
    run_step("Visualizations", run_visualizations, clean_df, raw_df)

    # Step 9: Markdown report
    run_step("Report Generation", generate_report)

    total = time.time() - total_start
    print("=" * 60)
    print(f"  Pipeline complete in {total:.1f}s")
    print("  Results:")
    print("    data/         — raw_pokemon.csv, cleaned_pokemon.csv, transformed_pokemon.csv")
    print("    output/       — association_rules.csv, cluster_summary.csv, classification_report.txt")
    print("    database/     — pokemon.db (SQLite)")
    print("    visuals/      — 10 chart images")
    print("    reports/      — report.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
