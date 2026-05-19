# End-to-End Web Scraping and Data Mining Pipeline
### Data Source: pokemondb.net

A complete university data mining project that scrapes Pokémon data from
[pokemondb.net/pokedex/all](https://pokemondb.net/pokedex/all), cleans and transforms it,
stores it in SQLite, and applies Frequent Pattern Mining, Clustering, and Classification.

---

## Dataset

Scraped from the full Pokédex table on pokemondb.net — 1,203 entries (base forms +
alternate/mega/regional forms) across all 9 generations.

**Features per Pokémon:**
`number`, `name`, `type1`, `type2`, `total`, `hp`, `attack`, `defense`,
`sp_atk`, `sp_def`, `speed`, `generation`, `is_legendary`

---

## Project Structure

```
project/
├── data/
│   ├── raw_pokemon.csv             ← saved by scraper
│   ├── cleaned_pokemon.csv         ← saved by cleaning step
│   └── transformed_pokemon.csv     ← saved by transformation step
├── output/
│   ├── association_rules.csv       ← Apriori results
│   ├── cluster_summary.csv         ← KMeans cluster stats
│   └── classification_report.txt   ← Random Forest metrics
├── database/
│   └── pokemon.db                  ← SQLite database
├── visuals/
│   ├── total_distribution.png
│   ├── type_counts.png
│   ├── stats_by_legendary.png
│   ├── generation_counts.png
│   ├── dashboard.png
│   ├── association_lift.png
│   ├── elbow_chart.png
│   ├── cluster_scatter.png
│   ├── confusion_matrix.png
│   └── feature_importance.png
├── reports/
│   ├── report.md                   ← auto-generated Markdown report
│   └── report.pdf                  ← styled PDF with all charts embedded
├── src/
│   ├── scraper.py
│   ├── cleaning.py
│   ├── transformation.py
│   ├── mining.py
│   ├── clustering.py
│   ├── classification.py
│   ├── database.py
│   ├── visualization.py
│   ├── report_generator.py
│   └── main.py
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the full pipeline

From inside the `project/` folder:

```bash
python src/main.py
```

**Pipeline steps:**
1. Scrape all 1,200+ entries from pokemondb.net/pokedex/all
2. Clean and validate data (remove duplicates, fix missing values)
3. Engineer features (stat tier buckets, type encoding, MinMax scaling)
4. Run Apriori association rule mining
5. KMeans clustering on base stats with elbow method
6. Random Forest classification — predict legendary status (94% accuracy)
7. Store all data in SQLite (`pokemon.db`)
8. Generate 10 charts (Matplotlib / Seaborn)
9. Write Markdown + PDF report

> The scraper fetches a single page — the full pipeline completes in **under 10 seconds**.

---

## Running Individual Steps

```bash
python src/scraper.py          # scrape only
python src/cleaning.py         # clean raw CSV
python src/transformation.py   # feature engineering
python src/mining.py           # association rules
python src/clustering.py       # clustering + charts
python src/classification.py   # classification + metrics
python src/database.py         # populate SQLite
python src/visualization.py    # generate all charts
python src/report_generator.py # write report.md + report.pdf
```

---

## Key Results

| Metric | Value |
|--------|-------|
| Total entries scraped | 1,219 |
| After cleaning | 1,203 |
| Legendary / Mythical | 136 |
| Association rules found | 183 |
| Top rule lift | 5.44 (Legendary → Uber tier) |
| KMeans clusters | 3 |
| Classification accuracy | 94% |

---

## Expected Outputs

| Output | Location |
|--------|----------|
| Raw data | `data/raw_pokemon.csv` |
| Cleaned data | `data/cleaned_pokemon.csv` |
| Association rules | `output/association_rules.csv` |
| Cluster summary | `output/cluster_summary.csv` |
| Classification report | `output/classification_report.txt` |
| SQLite database | `database/pokemon.db` |
| 10 chart images | `visuals/*.png` |
| Markdown report | `reports/report.md` |
| PDF report | `reports/report.pdf` |

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| `requests` | HTTP requests |
| `beautifulsoup4` | HTML parsing |
| `pandas` | Data manipulation |
| `numpy` | Numerical operations |
| `scikit-learn` | Clustering, classification, encoding, scaling |
| `mlxtend` | Apriori algorithm |
| `matplotlib` | Plotting |
| `seaborn` | Statistical visualizations |
| `sqlite3` | Database (stdlib) |
| `tabulate` | Markdown table rendering |
| `markdown` | Markdown → HTML conversion |
| `xhtml2pdf` | HTML → PDF generation |
