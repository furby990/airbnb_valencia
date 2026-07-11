# 🏠 Valencia Airbnb Investment Intelligence
### Where, when and how to invest in short-term rentals in Valencia
**Ironhack Data Analytics Bootcamp — Final Project**

> An investor-focused analysis of the Valencia Airbnb market that answers a single business question: **where, when and how to invest to maximize profitability.**

---

## 🔗 Links

| Resource | Link |
|---|---|
| 📊 **Presentation (Prezi)** | [View presentation](https://prezi.com/craft/room/1lowimnnzk8q?referral_token=4ovMpylnB3FN) |
| 💻 **Interactive Dashboard** | Runs locally with Plotly Dash — see [How to run the dashboard](#-how-to-run-the-dashboard) |
| 📁 **Dataset** | [Inside Airbnb — Valencia](https://insideairbnb.com/get-the-data/) |

---

## 🎯 Business Problem

An investor wants to enter the Valencia Airbnb market but doesn't know **where** to buy, **when** to do it, or **how** to operate. Existing analyses describe the market but don't recommend — there's a gap between raw data and strategic decision-making.

This project closes that gap by building a **composite Investment Score** per neighbourhood that combines real revenue, occupancy, demand growth, competition and price.

### Research Questions

| # | Question | Technique |
|---|---|---|
| RQ1 | What factors determine price? | Spearman correlation + p-values |
| RQ2 | Which neighbourhoods offer the best real profitability? | Weighted composite score (5 components) |
| RQ3 | Do Superhosts generate significantly more revenue? | Mann-Whitney U test |
| RQ4 | How does demand vary by season and neighbourhood? | Time series + heatmaps |
| RQ5 | Which host profile maximizes profitability? | Segmentation + Kruskal-Wallis |

---

## 📊 The Data

**Source:** [Inside Airbnb](https://insideairbnb.com) — Valencia, Spain (September 2025 snapshot)

| File | Rows | Columns | Use |
|---|---|---|---|
| `listings.csv` | 14,041 (7,780 after cleaning) | 79 | Main analysis |
| `calendar.csv` | 2,863,060 | 7 | Seasonality (Sep 2025 → Sep 2026) |
| `reviews.csv` | 416,827 (405,009 after cleaning) | 6 | Demand trend (2010–2025) |
| `neighbourhoods.csv` | 88 | 2 | Neighbourhood reference |
| `neighbourhoods.geojson` | — | — | Choropleth maps |

**Key differentiator:** this project exploits `estimated_revenue_l365d` and `estimated_occupancy_l365d` — real estimated revenue and occupancy per listing that most Airbnb analyses ignore.

---

## 🔑 Key Findings

### 1. A high price does not mean profitability
Price is not normally distributed (skewness 3.56). The #1 price driver is **accommodation capacity** (Spearman ρ = 0.62). Surprise case: **Poblats del Sud** has one of the highest prices but one of the lowest occupancy rates — occupancy matters as much as price.

### 2. The Superhost effect
Superhosts generate a median of **14,136 EUR/year** vs **2,904 EUR/year** for regular hosts — a **+386% uplift**, statistically significant (Mann-Whitney U, p < 0.0001). Becoming a Superhost is the single most profitable operational decision.

### 3. Seasonality
High season (June–September) reaches **58.3% occupancy** vs **44.3%** the rest of the year, concentrating **42.3% of annual demand**. Surprise: El Pla del Real leads annual occupancy (58.6%); Ciutat Vella is only 8th.

### 4. The Investment Score ranking

| Rank | Neighbourhood | Score | Revenue/year | Occupancy | Price/night |
|---|---|---|---|---|---|
| 🥇 1 | **Ciutat Vella** | 74.5 | 9,900 € | 66 nights | 122 € |
| 🥈 2 | **L'Eixample** | 68.9 | 7,920 € | 66 nights | 121 € |
| 🥉 3 | **Camins al Grau** | 66.6 | 6,630 € | 66 nights | 97 € |
| 4 | Quatre Carreres | 63.2 | 6,327 € | 60 nights | 98 € |
| 5 | Poblats Maritims | 60.9 | 6,578 € | 60 nights | 106 € |

**Key insight:** Camins al Grau has the same occupancy as the top 2 but a 20% lower entry price — the best value-for-money option for investors with less capital.

---

## 🧮 Investment Score Methodology

The score is a weighted composite of 5 normalized (min-max, 0–1) components:

| Component | Weight | Metric |
|---|---|---|
| Real Revenue | **35%** | Median `estimated_revenue_l365d` |
| Occupancy | **25%** | Median `estimated_occupancy_l365d` |
| YoY Demand Growth | **20%** | Year-over-year review growth |
| Inverse Competition | **10%** | Inverse of listing density |
| Relative Price | **10%** | Neighbourhood price / market median |

**Final score = weighted sum × 100** → 0–100 scale. Weights are defined in `config/config.py` (no hard-coded values elsewhere).

---

## 📐 Statistical Analysis

All tests use **α = 0.05**. Non-parametric tests were chosen because price is not normally distributed (confirmed by D'Agostino-Pearson, p < 0.001).

| Test | H0 | Result | p-value |
|---|---|---|---|
| Mann-Whitney U | Superhost = Regular revenue | **Rejected** | < 0.0001 |
| Kruskal-Wallis | Price equal across room types | **Rejected** | < 0.000001 |
| Kruskal-Wallis | Price equal across neighbourhoods | **Rejected** | < 0.000001 |
| Kruskal-Wallis | Revenue equal across host segments | **Rejected** | < 0.000001 |

---

## 🏗️ Project Structure

```
airbnb_valencia/
├── config/
│   └── config.py               # Central configuration — no hard-coded values
├── src/
│   ├── data_loader.py          # Data loading functions
│   ├── cleaning.py             # Cleaning & wrangling pipeline
│   ├── features.py             # Feature engineering + Investment Score
│   └── analysis.py             # Statistical analysis + hypothesis tests
├── sql/
│   ├── schema.sql              # Database schema
│   ├── queries_basic.sql       # Basic queries
│   └── queries_advanced.sql    # Window functions + subqueries
├── notebooks/
│   ├── 01_EDA.ipynb            # Exploratory data analysis
│   ├── 02_statistical_analysis.ipynb  # Hypothesis testing
│   ├── 03_seasonality.ipynb    # Seasonality analysis
│   ├── 04_host_analysis.ipynb  # Host segmentation
│   └── 05_investment_score.ipynb  # Final investment score
├── dashboard/
│   └── app.py                  # Interactive Plotly Dash dashboard
├── data/
│   ├── raw/                    # Original data (not versioned)
│   └── processed/              # Clean data + SQLite DB
├── reports/figures/            # Exported charts
├── load_mysql.py               # SQLite → MySQL migration script
├── requirements.txt
└── README.md
```

---

## 💾 SQL

Data is stored in both **SQLite** (used by the notebooks) and **MySQL** (Workbench):
- Tables: `listings` (7,780), `reviews` (405,009), `investment_scores` (19)
- Advanced queries include window functions (`RANK`, `PERCENT_RANK`, `LAG`, moving averages) and subqueries
- See `sql/queries_advanced.sql`

Migrate SQLite → MySQL with:
```bash
python load_mysql.py
```

---

## 📊 The Dashboard

An interactive dashboard built with **Plotly Dash**, featuring 4 tabs:

1. **Investment Score** — KPIs, visual ranking and interactive table
2. **Market by Neighbourhood** — 3 multi-select filters (room type, neighbourhood, host segment) + 4 charts. Select 2+ neighbourhoods to compare them side by side.
3. **Seasonality** — neighbourhood selector, monthly demand and historical trend
4. **Host Analysis** — segment comparison + investor recommendations panel

---

## ⚙️ Installation

```bash
git clone https://github.com/dfornero/Final-proyect-diego-fornero.git
cd Final-proyect-diego-fornero
pip install -r requirements.txt
```

Download the datasets from [Inside Airbnb — Valencia](https://insideairbnb.com/get-the-data/) and place them in `data/raw/`.

Run the notebooks in order: `01` → `02` → `03` → `04` → `05`.

### ▶️ How to run the dashboard

```bash
python dashboard/app.py
```

Then open **http://127.0.0.1:8050** in your browser.

> Note: the dashboard runs locally. It requires the processed data files generated by the notebooks (`data/processed/`).

---

## 📦 Requirements

```
pandas
numpy
matplotlib
seaborn
plotly
dash
scipy
scikit-learn
sqlalchemy
pymysql
jupyter
```

---

## 📝 Limitations & Next Steps

**Limitations:**
- `estimated_revenue_l365d` is an Inside Airbnb estimate, not official Airbnb data
- The calendar does not include per-date prices (empty column in this scrape)
- Data is a single point-in-time snapshot, not a longitudinal panel

**Next steps:**
- ML price prediction model (Case Study 1) as a natural extension
- Multi-quarter data for more robust trend analysis
- Deploy the dashboard publicly (Render / Railway)

---

## 👤 Author

**Diego Fornero** — Ironhack Data Analytics Bootcamp 2026
📊 [Presentation](https://prezi.com/craft/room/1lowimnnzk8q?referral_token=4ovMpylnB3FN)
