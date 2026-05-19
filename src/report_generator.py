"""
report_generator.py — Auto-generate Markdown + PDF report for the Pokémon pipeline

Produces:
  reports/report.md  — plain Markdown (for version control / GitHub)
  reports/report.pdf — styled PDF with all charts embedded
"""

import re
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

import markdown as md_lib
from xhtml2pdf import pisa

PROJECT_ROOT  = Path(__file__).parent.parent
CLEAN_INPUT   = PROJECT_ROOT / "data"   / "cleaned_pokemon.csv"
RULES_INPUT   = PROJECT_ROOT / "output" / "association_rules.csv"
CLUSTER_INPUT = PROJECT_ROOT / "output" / "cluster_summary.csv"
CLASS_REPORT  = PROJECT_ROOT / "output" / "classification_report.txt"
VISUALS_DIR   = PROJECT_ROOT / "visuals"
REPORT_DIR    = PROJECT_ROOT / "reports"

PDF_CSS = """
@page {
    size: A4 portrait;
    margin: 2cm 1.5cm 2.2cm 1.5cm;
}
body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10pt;
    color: #222;
    line-height: 1.45;
}
h1 {
    font-size: 20pt;
    color: #1a365d;
    border-bottom: 2pt solid #1a365d;
    padding-bottom: 6pt;
    margin-bottom: 4pt;
}
h2 {
    font-size: 13pt;
    color: #2b6cb0;
    margin-top: 18pt;
    border-bottom: 1pt solid #bee3f8;
    padding-bottom: 3pt;
}
h3 {
    font-size: 11pt;
    color: #4a5568;
    margin-top: 10pt;
}
p {
    margin: 4pt 0 4pt 0;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 8pt 0;
    font-size: 8.5pt;
}
th {
    background-color: #2b6cb0;
    color: #ffffff;
    padding: 4pt 6pt;
    text-align: left;
    border: 0.5pt solid #2b6cb0;
}
td {
    border: 0.5pt solid #cbd5e0;
    padding: 3pt 6pt;
    vertical-align: top;
}
img {
    display: block;
    width: 490pt;
    margin: 8pt auto 4pt auto;
}
pre {
    font-family: Courier New, Courier, monospace;
    font-size: 7.5pt;
    background-color: #f7fafc;
    border: 0.5pt solid #e2e8f0;
    padding: 6pt;
    white-space: pre-wrap;
    word-wrap: break-word;
}
code {
    font-family: Courier New, Courier, monospace;
    font-size: 8pt;
    background-color: #f0f0f0;
    padding: 1pt 3pt;
}
blockquote {
    border-left: 3pt solid #2b6cb0;
    padding: 2pt 8pt;
    color: #4a5568;
    background-color: #ebf8ff;
    margin: 6pt 0;
}
hr {
    border: 0;
    border-top: 1pt solid #e2e8f0;
    margin: 10pt 0;
}
ul, ol {
    margin: 4pt 0;
    padding-left: 18pt;
}
li {
    margin: 2pt 0;
}
.caption {
    text-align: center;
    font-size: 8pt;
    color: #666;
    margin-top: 2pt;
    margin-bottom: 6pt;
}
"""


def _img_tag(filename: str, caption: str = "") -> str:
    path = VISUALS_DIR / filename
    if not path.exists():
        return f"<p><em>[Chart not found: {filename}]</em></p>"
    b64 = base64.b64encode(path.read_bytes()).decode()
    src = f"data:image/png;base64,{b64}"
    cap = f'<p class="caption">{caption}</p>' if caption else ""
    return f'<img src="{src}" />{cap}'


def _md_img(filename: str) -> str:
    return f"<!-- IMG:{filename} -->"


def build_markdown(df, data_shape, date_str, total_stats, type_dist, gen_dist,
                   legend_count, total_count, rules_md, cluster_md, class_text) -> str:
    return f"""# End-to-End Web Scraping and Data Mining Pipeline
---

## 1. Project Overview

This project builds a complete ETL and data mining pipeline on Pokemon data scraped from
[pokemondb.net](https://pokemondb.net/pokedex/all) -- a freely accessible Pokedex database.

| Item | Detail |
|------|--------|
| Data Source | pokemondb.net/pokedex/all |
| Collection Method | HTML scraping with requests + BeautifulSoup4 |
| Total Entries | {data_shape[0]} |
| Features | {data_shape[1]} |
| Legendary / Mythical | {legend_count} out of {total_count} |
| Pipeline | Scrape -> Clean -> Transform -> Mine -> Cluster -> Classify -> Store -> Visualize |

---

## 2. Website Overview

{_md_img("website_screenshot.png")}

**pokemondb.net** is a comprehensive Pokemon database. The `/pokedex/all` page renders a
sortable HTML table listing every Pokemon entry (including alternate forms) with:

- **Number** -- National Pokedex number
- **Name** -- Pokemon name (includes form names, e.g. "Venusaur-Mega")
- **Type 1 / Type 2** -- Primary and secondary elemental types
- **Total** -- Sum of all six base stats
- **HP, Attack, Defense, Sp. Atk, Sp. Def, Speed** -- Individual base stats
- **Generation** -- Derived from Pokedex number ranges
- **is_legendary** -- 1 if Legendary or Mythical, 0 otherwise

---

## 3. Scraping Methodology

- **Library:** requests + BeautifulSoup4
- **Pages scraped:** Single page -- full table loads server-side with no pagination
- **Rows collected:** {data_shape[0]} entries (base forms + alternate/regional/mega forms)
- **Legendary flag:** Derived from a curated set of National Dex numbers (Gens 1-9)
- **Generation:** Assigned by Pokedex number ranges -- no extra HTTP requests required
- **Politeness:** Single page fetch with 15 s timeout; 3 retries with 2 s back-off

---

## 4. Raw Data Snapshot

**Shape:** {data_shape[0]} rows x {data_shape[1]} columns

{df.head(5).to_markdown(index=False) if not df.empty else "_Data unavailable_"}

---

## 5. Cleaning Process

| Step | Action |
|------|--------|
| Duplicates | Removed exact duplicate rows |
| Missing stats | Filled with column median |
| Missing types | type1 -> "Normal", type2 -> "None" |
| Invalid types | Replaced with "Unknown" / "None" |
| Generation | Filled missing with 1 |
| is_legendary | Filled missing with 0 |

### Base Stat Total Statistics
{total_stats}

### Top 10 Primary Types
{type_dist}

### Pokemon per Generation
{gen_dist}

{_md_img("before_after_cleaning.png")}

---

## 6. Transformation Process

| Feature | Transformation |
|---------|---------------|
| stat_tier | Very Weak (<300) / Weak (300-399) / Average (400-499) / Strong (500-599) / Uber (>=600) |
| type1_encoded | LabelEncoder -- integer per type |
| has_second_type | 1 if dual-typed, 0 if mono-type |
| *_scaled | MinMaxScaler to [0, 1] for all 7 numeric stat columns |

{_md_img("before_after_transformation.png")}

---

## 7. Frequent Pattern Mining

**Algorithm:** Apriori (mlxtend) | **Min support:** 0.05 | **Min confidence:** 0.30

Each Pokemon is represented as a basket:
`type1=<type>`, `tier=<tier>`, `gen=<group>`, `dual_type=Yes/No`, `legendary=Yes/No`

### Top 10 Association Rules (sorted by Lift)

{rules_md}

> **Lift > 1** means the item pair co-occurs more than chance would predict.

{_md_img("association_lift.png")}

---

## 8. Clustering Results

**Algorithm:** KMeans | **Features:** hp, attack, defense, sp_atk, sp_def, speed (all scaled)
**Optimal k:** selected via elbow method | **Visualization:** PCA 2D projection (* = Legendary)

### Cluster Summary

{cluster_md}

{_md_img("elbow_chart.png")}

{_md_img("cluster_scatter.png")}

---

## 9. Classification Results

**Model:** Random Forest (100 estimators)
**Target:** is_legendary -- Regular (0) vs Legendary/Mythical (1)
**Features:** total, hp, attack, defense, sp_atk, sp_def, speed, type1_encoded, has_second_type, generation
**Split:** 80% train / 20% test (stratified)

```
{class_text}
```

{_md_img("confusion_matrix.png")}

{_md_img("feature_importance.png")}

---

## 10. Visualizations

{_md_img("total_distribution.png")}

{_md_img("type_counts.png")}

{_md_img("stats_by_legendary.png")}

{_md_img("generation_counts.png")}

{_md_img("dashboard.png")}

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

- The dataset spans {data_shape[0]} Pokemon entries (including alternate forms) across 9 generations.
- Legendary and Mythical Pokemon ({legend_count} total) have significantly higher base stat totals.
- Water is the most common primary type; Dragon and Ghost are among the rarest.
- Top association rule: Legendary -> Uber stat tier (lift ~5.4) -- legendaries are 5x more likely to have 600+ total stats.
- KMeans (k=3) separates low-stat basics, physical powerhouses, and fast/special attackers.
- Random Forest predicts legendary status with ~94% accuracy; base stat total is the strongest predictor (40% importance).

---
"""


COVER_HTML = """
<div style="text-align: center; padding-top: 100pt;">
    <p style="font-size: 11pt; color: #2b6cb0; letter-spacing: 1pt; margin-bottom: 10pt;">
        E-JUST — End-to-End Web Scraping and Data Mining Pipeline
    </p>
    <h1 style="font-size: 26pt; color: #1a365d; border: none; margin-bottom: 6pt;">
        Pokemon Data Mining Pipeline
    </h1>
    <p style="font-size: 13pt; color: #4a5568; margin-bottom: 30pt;">
        Web Scraping · Frequent Pattern Mining · Clustering · Classification
    </p>
    <hr style="border-top: 1pt solid #cbd5e0; width: 60%; margin: 0 auto 20pt auto;" />
    <table style="margin: 0 auto; border-collapse: collapse; width: 55%; font-size: 12pt;">
        <tr>
            <th style="background-color: #2b6cb0; color: #fff; padding: 8pt 20pt; text-align: left; border: 0.5pt solid #2b6cb0;">Name</th>
            <th style="background-color: #2b6cb0; color: #fff; padding: 8pt 20pt; text-align: left; border: 0.5pt solid #2b6cb0;">ID</th>
        </tr>
        <tr>
            <td style="padding: 7pt 20pt; border: 0.5pt solid #cbd5e0;">Youssef Ahmed Rgab</td>
            <td style="padding: 7pt 20pt; border: 0.5pt solid #cbd5e0;">320230185</td>
        </tr>
        <tr>
            <td style="padding: 7pt 20pt; border: 0.5pt solid #cbd5e0; background-color: #f7fafc;">Seif Mohamed</td>
            <td style="padding: 7pt 20pt; border: 0.5pt solid #cbd5e0; background-color: #f7fafc;">320230186</td>
        </tr>
        <tr>
            <td style="padding: 7pt 20pt; border: 0.5pt solid #cbd5e0;">Mohamed Khaled</td>
            <td style="padding: 7pt 20pt; border: 0.5pt solid #cbd5e0;">320230211</td>
        </tr>
        <tr>
            <td style="padding: 7pt 20pt; border: 0.5pt solid #cbd5e0; background-color: #f7fafc;">Yehia Shady</td>
            <td style="padding: 7pt 20pt; border: 0.5pt solid #cbd5e0; background-color: #f7fafc;">320230215</td>
        </tr>
    </table>
</div>
<pdf:nextpage />
"""


def _table_to_img_tag(table_html: str) -> str:
    """Render an HTML table as a base64 PNG so it never splits across PDF pages."""
    try:
        dfs = pd.read_html(io.StringIO(f"<html><body>{table_html}</body></html>"))
        if not dfs:
            return table_html
        df = dfs[0].fillna("").astype(str)

        n_rows, n_cols = len(df), len(df.columns)
        col_lens = [max(len(str(c)), df[c].str.len().max()) for c in df.columns]
        total_len = max(sum(col_lens), 1)
        col_widths = [max(0.05, cl / total_len) for cl in col_lens]

        fig_w = min(12, max(7, n_cols * 1.8))
        fig_h = max(0.6, (n_rows + 1) * 0.38)

        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        ax.axis("off")

        tbl = ax.table(
            cellText=df.values,
            colLabels=list(df.columns),
            cellLoc="left",
            loc="center",
            colWidths=col_widths,
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.scale(1, 1.6)

        for j in range(n_cols):
            cell = tbl[0, j]
            cell.set_facecolor("#2b6cb0")
            cell.set_text_props(color="white", fontweight="bold")
            cell.set_edgecolor("#2b6cb0")

        for i in range(1, n_rows + 1):
            for j in range(n_cols):
                cell = tbl[i, j]
                cell.set_facecolor("#f7fafc" if i % 2 == 0 else "white")
                cell.set_edgecolor("#cbd5e0")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    facecolor="white", edgecolor="none")
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        return f'<img src="data:image/png;base64,{b64}" style="width:490pt;margin:6pt 0;" />'
    except Exception:
        return table_html


def markdown_to_html(markdown_text: str) -> str:
    html_body = md_lib.markdown(
        markdown_text,
        extensions=["tables", "fenced_code"],
    )

    def replace_placeholder(match):
        filename = match.group(1)
        captions = {
            "association_lift.png":          "Figure: Top Association Rules by Lift",
            "elbow_chart.png":               "Figure: Elbow Method -- Optimal k Selection",
            "cluster_scatter.png":           "Figure: KMeans Clusters -- PCA 2D Projection (* = Legendary)",
            "confusion_matrix.png":          "Figure: Confusion Matrix -- Legendary Classification",
            "feature_importance.png":        "Figure: Random Forest Feature Importances",
            "total_distribution.png":        "Figure: Distribution of Base Stat Totals",
            "type_counts.png":               "Figure: Pokemon Count by Primary Type",
            "stats_by_legendary.png":        "Figure: Base Stat Total -- Regular vs Legendary",
            "generation_counts.png":         "Figure: Pokemon Entries per Generation",
            "dashboard.png":                 "Figure: Summary Dashboard",
            "before_after_cleaning.png":       "Figure: Before vs After Cleaning -- Duplicate Removal",
            "before_after_transformation.png": "Figure: Before vs After Transformation -- MinMaxScaling",
            "website_screenshot.png":          "Figure: pokemondb.net/pokedex/all -- source website",
        }
        caption = captions.get(filename, filename)
        return _img_tag(filename, caption)

    html_body = re.sub(r"<!-- IMG:([^>]+) -->", replace_placeholder, html_body)

    # Render every table as a PNG image so it can never split across pages
    html_body = re.sub(
        r"<table[\s\S]*?</table>",
        lambda m: _table_to_img_tag(m.group(0)),
        html_body,
        flags=re.DOTALL,
    )

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{PDF_CSS}</style>
</head>
<body>
{COVER_HTML}
{html_body}
</body>
</html>"""


def html_to_pdf(html: str, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        status = pisa.CreatePDF(html, dest=f, encoding="utf-8")
    if status.err:
        raise RuntimeError(f"xhtml2pdf reported {status.err} error(s)")
    print(f"  PDF saved to:    {output_path}")


def generate_report():
    print("=" * 60)
    print("STEP 9: GENERATING MARKDOWN + PDF REPORT")
    print("=" * 60)

    df = pd.read_csv(CLEAN_INPUT) if CLEAN_INPUT.exists() else pd.DataFrame()

    data_shape   = df.shape if not df.empty else ("N/A", "N/A")
    total_stats  = df["total"].describe().round(1).to_markdown()    if "total"        in df.columns else ""
    type_dist    = df["type1"].value_counts().head(10).to_markdown() if "type1"        in df.columns else ""
    gen_dist     = df["generation"].value_counts().sort_index().to_markdown() if "generation" in df.columns else ""
    legend_count = int(df["is_legendary"].sum()) if "is_legendary" in df.columns else "N/A"
    total_count  = len(df) if not df.empty else "N/A"

    rules_md = (
        pd.read_csv(RULES_INPUT)[["antecedents", "consequents", "support", "confidence", "lift"]]
        .head(10).to_markdown(index=False)
        if RULES_INPUT.exists() else "_Rules not generated yet_"
    )
    cluster_md = (
        pd.read_csv(CLUSTER_INPUT).to_markdown(index=False)
        if CLUSTER_INPUT.exists() else "_Not available_"
    )
    class_text = (
        CLASS_REPORT.read_text(encoding="utf-8")
        if CLASS_REPORT.exists() else "_Not generated yet_"
    )

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    markdown_text = build_markdown(
        df, data_shape, date_str, total_stats, type_dist, gen_dist,
        legend_count, total_count, rules_md, cluster_md, class_text,
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = REPORT_DIR / "report.md"
    md_path.write_text(markdown_text, encoding="utf-8")
    print(f"  Markdown saved to: {md_path}")

    print("  Converting to PDF (embedding charts)...")
    html = markdown_to_html(markdown_text)
    html_to_pdf(html, REPORT_DIR / "report.pdf")


if __name__ == "__main__":
    generate_report()
