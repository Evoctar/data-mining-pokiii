# End-to-End Web Scraping and Data Mining Pipeline
### Data Source: BoardGameGeek (BGG)

A complete university data mining project that scrapes board game data from
[boardgamegeek.com](https://boardgamegeek.com), cleans it, stores it in SQLite,
and applies Frequent Pattern Mining, Clustering, and Classification.

---

## How Data is Collected

**Phase 1 — HTML scraping:**
Scrapes BGG browse/ranking pages with `requests` + `BeautifulSoup4` to collect
game IDs and ranks.

**Phase 2 — BGG XML API:**
Fetches detailed stats (rating, complexity, players, playtime, category, mechanics)
for each game via `https://boardgamegeek.com/xmlapi2/thing?id=...&stats=1`.
Parsed with Python's built-in `xml.etree.ElementTree`.

**Dataset features per game:**
`game_id`, `name`, `year_published`, `min/max_players`, `min/max_playtime`,
`avg_playtime`, `min_age`, `avg_rating`, `num_voters`, `complexity`, `bgg_rank`,
`primary_category`, `primary_mechanic`

---

## Project Structure

```
project/
├── data/
│   ├── raw_games.csv             ← saved by scraper
│   ├── cleaned_games.csv         ← saved by cleaning step
│   └── transformed_games.csv     ← saved by transformation step
├── output/
│   ├── association_rules.csv     ← Apriori results
│   ├── cluster_summary.csv       ← KMeans cluster stats
│   └── classification_report.txt ← Random Forest metrics
├── database/
│   └── games.db                  ← SQLite database
├── visuals/
│   ├── rating_distribution.png
│   ├── complexity_vs_rating.png
│   ├── top_categories.png
│   ├── playtime_by_complexity.png
│   ├── raw_vs_cleaned.png
│   ├── dashboard.png
│   ├── association_lift.png
│   ├── elbow_chart.png
│   ├── cluster_scatter.png
│   ├── confusion_matrix.png
│   └── feature_importance.png
├── reports/
│   └── report.md                 ← auto-generated markdown report
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
1. Scrape ~400 board game IDs from BGG browse pages
2. Fetch detailed stats for each game via BGG XML API
3. Clean and validate data
4. Engineer features (buckets, encodings, scaling)
5. Run Apriori association rule mining
6. KMeans clustering with elbow method
7. Random Forest classification (predict rating bucket)
8. Store all data in SQLite
9. Generate 11 charts
10. Write Markdown report

> **Note:** The scraper makes ~30 API batch requests with 1.5 s delays.
> Expect the full pipeline to take **3–8 minutes** on first run.
> To re-run without re-scraping, comment out the scraping step in `main.py`.

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
python src/report_generator.py # write report.md
```

---

## Expected Outputs

| Output | Location |
|--------|----------|
| Raw data | `data/raw_games.csv` |
| Cleaned data | `data/cleaned_games.csv` |
| Association rules | `output/association_rules.csv` |
| Cluster summary | `output/cluster_summary.csv` |
| Classification report | `output/classification_report.txt` |
| SQLite database | `database/games.db` |
| 11 chart images | `visuals/*.png` |
| Markdown report | `reports/report.md` |

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| `requests` | HTTP requests (browse pages + API) |
| `beautifulsoup4` | HTML parsing of browse pages |
| `xml.etree.ElementTree` | XML API response parsing (stdlib) |
| `pandas` | Data manipulation |
| `numpy` | Numerical operations |
| `scikit-learn` | ML (clustering, classification, encoding, scaling) |
| `mlxtend` | Apriori algorithm |
| `matplotlib` | Plotting |
| `seaborn` | Statistical visualizations |
| `sqlite3` | Database (stdlib — no install needed) |
| `tabulate` | Markdown table rendering in reports |
