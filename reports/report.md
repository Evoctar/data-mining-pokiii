# End-to-End Web Scraping and Data Mining Pipeline
**Generated:** 2026-05-20 00:45

---

## 1. Project Overview

This project builds a complete ETL and data mining pipeline on Pokémon data scraped from
[pokemondb.net](https://pokemondb.net/pokedex/all) — a freely accessible Pokédex database.

| Item | Detail |
|------|--------|
| Data Source | pokemondb.net/pokedex/all |
| Collection Method | HTML scraping with requests + BeautifulSoup4 |
| Total Entries | 1203 |
| Features | 13 |
| Legendary / Mythical | 136 out of 1203 |
| Pipeline | Scrape → Clean → Transform → Mine → Cluster → Classify → Store → Visualize |

---

## 2. Website Overview

**pokemondb.net** is a comprehensive Pokémon database. The `/pokedex/all` page renders a
sortable HTML table listing every Pokémon entry (including alternate forms) with:

- **Number** — National Pokédex number
- **Name** — Pokémon name (includes form names, e.g. "Venusaur-Mega")
- **Type 1 / Type 2** — Primary and secondary elemental types
- **Total** — Sum of all six base stats
- **HP, Attack, Defense, Sp. Atk, Sp. Def, Speed** — Individual base stats
- **Generation** — Derived from Pokédex number ranges
- **is_legendary** — 1 if Legendary or Mythical, 0 otherwise

---

## 3. Scraping Methodology

- **Library:** requests + BeautifulSoup4
- **Pages scraped:** Single page — full table loads server-side with no pagination
- **Rows collected:** 1203 entries (base forms + alternate/regional/mega forms)
- **Legendary flag:** Derived from a curated set of National Dex numbers (Gens 1–9)
- **Generation:** Assigned by Pokédex number ranges — no extra HTTP requests required
- **Politeness:** Single page fetch with 15 s timeout; 3 retries with 2 s back-off

---

## 4. Raw Data Snapshot

**Shape:** 1203 rows × 13 columns

|   number | name       | type1   | type2   |   total |   hp |   attack |   defense |   sp_atk |   sp_def |   speed |   generation |   is_legendary |
|---------:|:-----------|:--------|:--------|--------:|-----:|---------:|----------:|---------:|---------:|--------:|-------------:|---------------:|
|        1 | Bulbasaur  | Grass   | Poison  |     318 |   45 |       49 |        49 |       65 |       65 |      45 |            1 |              0 |
|        2 | Ivysaur    | Grass   | Poison  |     405 |   60 |       62 |        63 |       80 |       80 |      60 |            1 |              0 |
|        3 | Venusaur   | Grass   | Poison  |     525 |   80 |       82 |        83 |      100 |      100 |      80 |            1 |              0 |
|        3 | Venusaur   | Grass   | Poison  |     625 |   80 |      100 |       123 |      122 |      120 |      80 |            1 |              0 |
|        4 | Charmander | Fire    | nan     |     309 |   39 |       52 |        43 |       60 |       50 |      65 |            1 |              0 |

---

## 5. Cleaning Process

| Step | Action |
|------|--------|
| Duplicates | Removed exact duplicate rows |
| Missing stats | Filled with column median |
| Missing types | type1 → "Normal", type2 → "None" |
| Invalid types | Replaced with "Unknown" / "None" |
| Generation | Filled missing with 1 |
| is_legendary | Filled missing with 0 |

### Base Stat Total Statistics
|       |   total |
|:------|--------:|
| count |  1203   |
| mean  |   443.9 |
| std   |   121.7 |
| min   |   175   |
| 25%   |   332   |
| 50%   |   466   |
| 75%   |   525   |
| max   |  1125   |

### Top 10 Primary Types
| type1    |   count |
|:---------|--------:|
| Water    |     147 |
| Normal   |     129 |
| Grass    |     114 |
| Bug      |      89 |
| Psychic  |      81 |
| Fire     |      76 |
| Electric |      72 |
| Rock     |      67 |
| Dark     |      57 |
| Fighting |      51 |

### Pokémon per Generation
|   generation |   count |
|-------------:|--------:|
|            1 |     206 |
|            2 |     112 |
|            3 |     165 |
|            4 |     123 |
|            5 |     174 |
|            6 |      89 |
|            7 |      99 |
|            8 |     107 |
|            9 |     128 |

---

## 6. Transformation Process

| Feature | Transformation |
|---------|---------------|
| stat_tier | Very Weak (<300) / Weak (300–399) / Average (400–499) / Strong (500–599) / Uber (>=600) |
| type1_encoded | LabelEncoder — integer per type |
| has_second_type | 1 if dual-typed, 0 if mono-type |
| *_scaled | MinMaxScaler to [0, 1] for all 7 numeric stat columns |

---

## 7. Frequent Pattern Mining

**Algorithm:** Apriori (mlxtend) | **Min support:** 0.05 | **Min confidence:** 0.30

Each Pokémon is represented as a basket:
`type1=<type>`, `tier=<tier>`, `gen=<group>`, `dual_type=Yes/No`, `legendary=Yes/No`

### Top 10 Association Rules (sorted by Lift)

| antecedents                                  | consequents                    |   support |   confidence |    lift |
|:---------------------------------------------|:-------------------------------|----------:|-------------:|--------:|
| legendary=Yes                                | tier=Uber                      | 0.0623441 |     0.551471 | 5.43786 |
| tier=Uber                                    | legendary=Yes                  | 0.0623441 |     0.614754 | 5.43786 |
| tier=Strong                                  | dual_type=Yes, gen=Recent(7-9) | 0.0798005 |     0.322148 | 1.96723 |
| dual_type=Yes, gen=Recent(7-9)               | tier=Strong                    | 0.0798005 |     0.48731  | 1.96723 |
| dual_type=Yes, gen=Recent(7-9), legendary=No | tier=Strong                    | 0.0598504 |     0.458599 | 1.85132 |
| dual_type=Yes, gen=Recent(7-9)               | legendary=No, tier=Strong      | 0.0598504 |     0.365482 | 1.80936 |
| dual_type=Yes, tier=Strong                   | gen=Recent(7-9)                | 0.0798005 |     0.472906 | 1.70331 |
| dual_type=Yes, legendary=No, tier=Strong     | gen=Recent(7-9)                | 0.0598504 |     0.431138 | 1.55287 |
| dual_type=Yes, tier=Strong                   | gen=Recent(7-9), legendary=No  | 0.0598504 |     0.35468  | 1.53482 |
| tier=VeryWeak                                | dual_type=No, legendary=No     | 0.078138  |     0.614379 | 1.49918 |

> **Lift > 1** means the item pair co-occurs more than chance would predict.

<!-- IMG:association_lift.png -->

---

## 8. Clustering Results

**Algorithm:** KMeans | **Features:** hp, attack, defense, sp_atk, sp_def, speed (all scaled)
**Optimal k:** selected via elbow method | **Visualization:** PCA 2D projection (legendaries marked *)

### Cluster Summary

|   cluster |   count |   avg_total |   avg_hp |   avg_attack |   avg_defense |   avg_speed |   legendary_count | top_type   |
|----------:|--------:|------------:|---------:|-------------:|--------------:|------------:|------------------:|:-----------|
|         0 |     449 |       314.1 |     52.6 |         54.3 |          53.4 |        51.6 |                 4 | Normal     |
|         1 |     402 |       492.5 |     81.5 |        102.8 |          93.8 |        69.7 |                29 | Normal     |
|         2 |     352 |       554.1 |     83.4 |         91.4 |          81.9 |        93.6 |               103 | Psychic    |

<!-- IMG:elbow_chart.png -->

<!-- IMG:cluster_scatter.png -->

---

## 9. Classification Results

**Model:** Random Forest (100 estimators)
**Target:** is_legendary — Regular (0) vs Legendary/Mythical (1)
**Features:** total, hp, attack, defense, sp_atk, sp_def, speed, type1_encoded, has_second_type, generation
**Split:** 80% train / 20% test (stratified)

```
Random Forest Classification Report
Target: is_legendary (0=Regular, 1=Legendary/Mythical)
==================================================
Accuracy: 0.9378

              precision    recall  f1-score   support

     Regular       0.97      0.96      0.96       214
   Legendary       0.71      0.74      0.73        27

    accuracy                           0.94       241
   macro avg       0.84      0.85      0.85       241
weighted avg       0.94      0.94      0.94       241

Feature Importances:
total              0.398791
sp_atk             0.103571
speed              0.097169
hp                 0.086298
attack             0.078405
sp_def             0.072013
generation         0.069130
defense            0.051572
type1_encoded      0.035627
has_second_type    0.007424

```

<!-- IMG:confusion_matrix.png -->

<!-- IMG:feature_importance.png -->

---

## 10. Visualizations

<!-- IMG:total_distribution.png -->

<!-- IMG:type_counts.png -->

<!-- IMG:stats_by_legendary.png -->

<!-- IMG:generation_counts.png -->

<!-- IMG:dashboard.png -->

---

## 11. Database

Data stored in **SQLite** (`database/pokemon.db`, table `pokemon`).

```sql
CREATE TABLE pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER, name TEXT,
    type1 TEXT, type2 TEXT,
    total INTEGER, hp INTEGER, attack INTEGER,
    defense INTEGER, sp_atk INTEGER, sp_def INTEGER, speed INTEGER,
    generation INTEGER, is_legendary INTEGER
);
```

---

## 12. Final Findings

- The dataset spans 1203 Pokémon entries (including alternate forms) across 9 generations.
- Legendary and Mythical Pokémon (136 total) have significantly higher base stat totals.
- Water is the most common primary type; Dragon and Ghost are among the rarest.
- Top association rule: Legendary → Uber stat tier (lift ≈ 5.4) — legendaries are 5× more likely to have 600+ total stats.
- KMeans (k=3) separates low-stat basics, physical powerhouses, and fast/special attackers.
- Random Forest predicts legendary status with ~94% accuracy; base stat total is the strongest predictor (40% importance).

---

*Report auto-generated by src/report_generator.py*
