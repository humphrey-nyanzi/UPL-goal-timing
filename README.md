# UPL Goal Data Analysis Project

<a target="_blank" href="https://datalumina.com/">
    <img src="https://img.shields.io/badge/Datalumina-Project%20Template-2856f7" alt="Datalumina Project" />
</a>

## Project Overview

This project analyzes goal-scoring data from the Premier League of Uganda (UPL) across multiple seasons (2019/20 - 2024/25). The pipeline includes:

1. **Data Scraping** (`notebooks/scraping.ipynb`): Web scraping UPL match data from official website
2. **Data Cleaning** (`notebooks/cleaning.ipynb`): Consolidating, standardizing, and enriching data
3. **Analysis & Visualization** (`notebooks/analysis.ipynb`): Exploratory analysis and reporting

## Recent Improvements (Phase 1 & 2 Refactoring)

This project has been refactored to follow best practices:

### ✅ Code Organization
- **Extracted reusable functions** from notebooks into `src/` modules
- **Separated concerns**: Dataset loading, data cleaning, and visualization
- **Centralized configuration**: All paths and constants in `src/config.py`

### ✅ File Structure
- **Raw data** now stored in `data/raw/` (one CSV per season)
- **Processed data** in `data/processed/` (cleaned & final outputs)
- **.gitignore** updated to exclude large CSV files and database files

### ✅ Module Documentation
- Comprehensive docstrings with examples
- Type hints for better IDE support
- Error handling for robustness

## Project Organization

```
├── LICENSE            <- Open-source license
├── README.md          <- Project documentation
├── pyproject.toml     <- Project metadata & dependencies (PEP 621)
├── requirements.txt   <- Legacy requirements file (deprecated - use pyproject.toml)
│
├── data/
│   ├── raw/           <- Original, immutable season CSVs (scraper output)
│   ├── processed/     <- Final cleaned & aggregated data
│   ├── interim/       <- Intermediate transformations (as needed)
│   └── external/      <- Reference data (team info, stadiums, etc.)
│
├── models/            <- Trained models, predictions
│
├── notebooks/         <- Jupyter notebooks (in execution order)
│   ├── scraping.ipynb    <- Fetch UPL data from web
│   ├── cleaning.ipynb    <- Clean, standardize, enrich
│   └── analysis.ipynb    <- Exploratory analysis & visualizations
│
├── src/               <- Reusable Python modules
│   ├── __init__.py
│   ├── config.py         <- Configuration, paths, constants
│   ├── dataset.py        <- Data loading & consolidation
│   ├── cleaning.py       <- Data cleaning & normalization
│   ├── plots.py          <- Visualization functions
│   ├── modeling/         <- (Placeholder for ML code)
│   └── services/         <- (Placeholder for API integrations)
│
├── reports/           <- Generated analysis & figures
│   └── figures/
│
└── references/        <- Documentation, data dictionaries
```

## Usage

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd magic_minutes
   ```

2. **Set up Python environment** (Python 3.12+)
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   # or from pyproject.toml: pip install -e .
   ```

### Running the Pipeline

Each notebook should be run in order:

1. **Scraping** (`notebooks/scraping.ipynb`)
   - Fetches current season match data from UPL website
   - Outputs to `data/raw/upl_goals_YYYY_YY.csv`

2. **Cleaning** (`notebooks/cleaning.ipynb`)
   - Consolidates all season files from `data/raw/`
   - Standardizes team names, cleans goal data
   - Outputs to `data/processed/upl_goals_2019_2025_cleaned.csv`

3. **Analysis** (`notebooks/analysis.ipynb`)
   - Loads cleaned data from `data/processed/`
   - Generates visualizations and statistics
   - Outputs figures to `reports/figures/`

### Using the Modules Programmatically

```python
from src.config import RAW_SEASON_FILES, CLEANED_CSV
from src.dataset import consolidate_seasons, save_dataframe
from src.cleaning import clean_dataframe
from src.plots import plot_goals_by_team

# Load & consolidate seasons
df_raw = consolidate_seasons(RAW_SEASON_FILES)

# Clean the data
df_clean = clean_dataframe(df_raw)

# Save
save_dataframe(df_clean, CLEANED_CSV)

# Visualize
plot_goals_by_team(df_clean)
```

## Data Flow

```
scraping.ipynb
    ↓ (saves to data/raw/)
data/raw/upl_goals_*.csv
    ↓
cleaning.ipynb
    ├─ Load from data/raw/
    ├─ Consolidate + clean
    ↓ (saves to data/processed/)
data/processed/upl_goals_2019_2025_cleaned.csv
    ↓
analysis.ipynb
    ├─ Load from data/processed/
    ├─ Analyze + visualize
    ↓ (saves to reports/figures/)
reports/figures/*.png
```

## Key Modules

### `src/config.py`
Centralized configuration and constants:
- File paths (`DATA_RAW`, `DATA_PROCESSED`, `CLEANED_CSV`)
- Web scraping settings (`USER_AGENT`, `REQUEST_TIMEOUT`)
- Team name mappings and abbreviations
- Season lists

### `src/dataset.py`
Data loading and consolidation:
- `load_season_csv()`: Load individual season file
- `consolidate_seasons()`: Merge multiple seasons
- `save_dataframe()`: Save with error handling

### `src/cleaning.py`
Data cleaning pipeline:
- `split_combined_teams()`: Handle "Team A vs Team B" format
- `normalize_team_names()`: Standardize naming
- `fix_known_goal_minute_errors()`: Corrections for data issues
- `add_goal_minute_features()`: Numeric minute conversion
- `add_derived_features()`: Create analysis columns (match_id, round, etc.)
- `clean_dataframe()`: Full pipeline

### `src/plots.py`
Reusable visualizations:
- `plot_goals_by_team()`: Goals per team (bar chart)
- `plot_goals_by_season()`: Goals per season
- `plot_goals_by_minute()`: Distribution across match minutes
- `plot_goal_type_distribution()`: Penalty vs Own Goal vs Regular
- `plot_home_vs_away()`: Home advantage analysis

## Dependencies

Core dependencies (from `pyproject.toml`):
- `pandas>=2.3.3` - Data manipulation
- `numpy>=2.4.0` - Numerical computing
- `matplotlib>=3.10.8` - Static visualizations
- `seaborn>=0.13.2` - Statistical plots
- `plotly>=6.5.0` - Interactive visualizations
- `requests>=2.32.5` - Web scraping
- `beautifulsoup4>=4.14.3` - HTML parsing
- `python-dotenv>=1.1.1` - Environment variables

Dev dependencies:
- `ipykernel>=7.0.0` - Jupyter support
- `pytest>=7.0.0` - Testing
- `black>=23.0.0` - Code formatting
- `ruff>=0.1.0` - Linting

## Notes for Future Development

- **Add tests**: Unit tests for cleaning functions in `tests/` folder
- **Parameterize notebooks**: Accept season/date ranges as inputs
- **Automate pipeline**: Create a scheduler/runner script
- **Database**: Consider SQLite for larger datasets
- **API**: Expose analysis via REST API for dashboards
- **CI/CD**: Add GitHub Actions to validate notebooks on commits

## Data Note

Raw season CSV files (`data/raw/*.csv`) are excluded from git (see `.gitignore`). 
To reproduce the analysis, run `notebooks/scraping.ipynb` to fetch current data, 
or restore from a data backup.

├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
└── src                         <- Source code for this project
    │
    ├── __init__.py             <- Makes src a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    │    
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    ├── plots.py                <- Code to create visualizations 
    │
    └── services                <- Service classes to connect with external platforms, tools, or APIs
        └── __init__.py 
```