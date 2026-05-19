# CLAUDE.md — Project Context for Future Sessions

## What This Project Is

A complete university Data Mining pipeline that scrapes **books.toscrape.com**, cleans and transforms the data, runs three mining techniques, stores results in SQLite, generates visualizations, and auto-produces a Markdown report.

---

## Project Structure

```
project/
├── src/
│   ├── main.py              # Pipeline orchestrator — runs all 9 steps
│   ├── scraper.py           # Step 1: HTML scraping (books.toscrape.com)
│   ├── cleaning.py          # Step 2: Data cleaning
│   ├── transformation.py    # Step 3: Feature engineering + encoding
│   ├── mining.py            # Step 4: Apriori association rules
│   ├── clustering.py        # Step 5: KMeans clustering
│   ├── classification.py    # Step 6: Random Forest classification
│   ├── database.py          # Step 7: SQLite storage
│   ├── visualization.py     # Step 8: Matplotlib/Seaborn charts
│   └── report_generator.py  # Step 9: Auto-generate reports/report.md
├── data/
│   ├── raw_books.csv         # Output of scraper
│   ├── cleaned_books.csv     # Output of cleaning
│   └── transformed_books.csv # Output of transformation
├── output/
│   ├── association_rules.csv
│   ├── cluster_summary.csv
│   └── classification_report.txt
├── database/
│   └── books.db              # SQLite database
├── visuals/                  # 10 chart PNGs
├── reports/
│   └── report.md             # Auto-generated Markdown report
├── requirements.txt
└── venv/                     # Python 3.13.2 virtual environment
```

---

## How to Run

```powershell
cd "j:/Code/Data Mining/project"
venv/Scripts/python src/main.py
```

The full pipeline takes a few minutes (scraping ~1000 books + 1000 detail pages).

---

## Key Design Decisions

### Website Choice
- **books.toscrape.com** — chosen because it is a sandbox site built for scraping practice (returns 200 OK, no bot protection).
- **BGG (boardgamegeek.com)** was attempted but rejected: HTML pages return 403, XML API returns 401 Unauthorized (BGG now requires authentication for all API access, even with full browser headers and session cookies).
- **pcpartpicker.com** was rejected upfront due to Cloudflare protection.

### Scraper (scraper.py)
- Scrapes all 50 catalogue pages (20 books each ≈ 1000 books)
- Extracts: title, price (£ stripped → float), rating (CSS class word → int via RATING_MAP), availability, category (from detail page breadcrumb)
- Delays: 0.5s between pages, 0.1s between detail pages, up to 3 retries with 2s back-off
- `BASE_URL = "https://books.toscrape.com/catalogue/"`

### Cleaning (cleaning.py)
- Removes duplicates
- Fills missing: median price, mode rating (3), "Unknown" category
- Normalizes availability → "In stock" / "Out of stock"
- Casts types; title-cases category

### Transformation (transformation.py)
- `price_bucket`: Low (<£20) / Medium (£20–40) / High (>£40) via `pd.cut`
- `category_encoded`: LabelEncoder
- `availability_binary`: 1 = In stock, 0 = Out of stock
- `price_scaled`, `rating_scaled`: MinMaxScaler to [0, 1]

### Mining (mining.py)
- Apriori (mlxtend), min_support=0.05, min_confidence=0.30
- Basket per book: [price=bucket, rating=N, avail=X, cat=Y]
- Output: association_rules.csv, visuals/association_lift.png

### Clustering (clustering.py)
- Features: price_scaled + rating_scaled
- Elbow method (k=2..8) to pick optimal k
- PCA 2D projection for scatter plot
- Output: cluster_summary.csv, elbow_chart.png, cluster_scatter.png

### Classification (classification.py)
- Target: price_bucket (Low/Medium/High)
- Features: rating, category_encoded, availability_binary
- Random Forest (100 trees), 80/20 stratified split
- Output: classification_report.txt, confusion_matrix.png, feature_importance.png

### Database (database.py)
- SQLite at database/books.db, table `books`
- Columns: id, title, price, rating, rating_word, availability, category
- Runs 4 example analytical queries on creation

### Visualizations (visualization.py)
- Uses `matplotlib.use("Agg")` (non-interactive, file-only output)
- Generates: price_distribution.png, rating_vs_price.png, category_counts.png, raw_vs_cleaned.png, dashboard.png

### Report (report_generator.py)
- Reads all output CSVs + classification_report.txt
- Uses `.to_markdown()` (requires tabulate package) for tables
- Saves to reports/report.md

---

## Dependencies (requirements.txt)

```
requests==2.32.3
beautifulsoup4==4.12.3
pandas==2.2.3
numpy==1.26.4
scikit-learn==1.5.2
mlxtend==0.23.1
matplotlib==3.9.2
seaborn==0.13.2
tabulate==0.9.0
```

All installed in `venv/` (Python 3.13.2).

---

## Known Issues Fixed

- **NameError in report_generator.py**: f-string contained `{n}` (BGG page number) which Python tried to evaluate. Fixed by converting to plain text.
- **BGG API 401**: Not a fixable issue — BGG requires auth. Reverted to books.toscrape.com.
- **Cascading FileNotFoundError**: If scraper fails, all downstream steps fail (no CSV). They fail gracefully via try/except in `run_step()`.

---

## Pipeline Status (as of last run)

The pipeline was executing against books.toscrape.com. If output files exist in `data/`, `output/`, `visuals/`, `database/`, and `reports/`, the pipeline completed successfully. Check with:

```powershell
ls "j:/Code/Data Mining/project/data"
ls "j:/Code/Data Mining/project/output"
ls "j:/Code/Data Mining/project/visuals"
```
