"""
scraper.py — Scrape all Pokémon from pokemondb.net/pokedex/all

Collects every entry in the full Pokédex table (~1200 rows including forms):
  number, name, type1, type2, total, hp, attack, defense,
  sp_atk, sp_def, speed, generation, is_legendary
Saves raw output to data/raw_pokemon.csv.
"""

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

POKEDEX_URL = "https://pokemondb.net/pokedex/all"
RAW_OUTPUT  = Path(__file__).parent.parent / "data" / "raw_pokemon.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

# Legendary and Mythical Pokémon by National Dex number (Gens 1-9)
LEGENDARY_NUMBERS = {
    # Gen 1
    144, 145, 146, 150, 151,
    # Gen 2
    243, 244, 245, 249, 250, 251,
    # Gen 3
    377, 378, 379, 380, 381, 382, 383, 384, 385, 386,
    # Gen 4
    480, 481, 482, 483, 484, 485, 486, 487, 488,
    489, 490, 491, 492, 493,
    # Gen 5
    638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649,
    # Gen 6
    716, 717, 718, 719, 720, 721,
    # Gen 7
    772, 773, 785, 786, 787, 788, 789, 790, 791, 792,
    793, 794, 795, 796, 797, 798, 799, 800, 801, 802,
    804, 805, 806, 807, 808, 809,
    # Gen 8
    888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898,
    # Gen 9
    1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010,
}


def get_soup(url: str, retries: int = 3) -> BeautifulSoup:
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except requests.RequestException as e:
            print(f"  Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(2)
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts")


def assign_generation(number: int) -> int:
    if number <= 151:   return 1
    if number <= 251:   return 2
    if number <= 386:   return 3
    if number <= 493:   return 4
    if number <= 649:   return 5
    if number <= 721:   return 6
    if number <= 809:   return 7
    if number <= 905:   return 8
    return 9


def scrape_pokedex() -> pd.DataFrame:
    print("  Fetching Pokédex table from pokemondb.net...")
    soup  = get_soup(POKEDEX_URL)
    tbody = soup.select_one("#pokedex tbody")
    if tbody is None:
        raise RuntimeError("Could not locate #pokedex tbody on page")

    records = []
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 10:
            continue

        number  = int(cells[0].text.strip())
        name    = cells[1].select_one("a.ent-name").text.strip()
        types   = [a.text.strip() for a in cells[2].find_all("a")]
        type1   = types[0] if len(types) > 0 else "Unknown"
        type2   = types[1] if len(types) > 1 else "None"
        total   = int(cells[3].text.strip())
        hp      = int(cells[4].text.strip())
        attack  = int(cells[5].text.strip())
        defense = int(cells[6].text.strip())
        sp_atk  = int(cells[7].text.strip())
        sp_def  = int(cells[8].text.strip())
        speed   = int(cells[9].text.strip())

        records.append({
            "number":  number,
            "name":    name,
            "type1":   type1,
            "type2":   type2,
            "total":   total,
            "hp":      hp,
            "attack":  attack,
            "defense": defense,
            "sp_atk":  sp_atk,
            "sp_def":  sp_def,
            "speed":   speed,
        })

    df = pd.DataFrame(records)
    df["generation"]  = df["number"].apply(assign_generation)
    df["is_legendary"] = df["number"].isin(LEGENDARY_NUMBERS).astype(int)
    return df


def run_scraper() -> pd.DataFrame:
    print("=" * 60)
    print("STEP 1: WEB SCRAPING — pokemondb.net")
    print("=" * 60)

    df = scrape_pokedex()

    print(f"\n  Total Pokémon entries: {len(df)}")
    print(f"  Unique dex numbers:   {df['number'].nunique()}")
    print(f"  Legendary/Mythical:   {df['is_legendary'].sum()}")
    print(f"  Generations covered:  {df['generation'].nunique()} (Gen {df['generation'].min()}–{df['generation'].max()})")
    print(f"  Unique types (type1): {df['type1'].nunique()}")
    print(f"  Columns: {list(df.columns)}")
    print("\n  Sample (first 5 rows):")
    print(df.head(5).to_string())

    RAW_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_OUTPUT, index=False)
    print(f"\n  Raw data saved to: {RAW_OUTPUT}")
    return df


if __name__ == "__main__":
    run_scraper()
