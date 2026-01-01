"""
Configuration and constants for the UPL Goal Data Analysis project.

This module centralizes file paths, constants, and configuration settings
to avoid hardcoding values in notebooks and scripts.
"""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"
DATA_EXTERNAL = DATA_DIR / "external"
DATA_INTERIM = DATA_DIR / "interim"

# Report directories
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Models directory
MODELS_DIR = PROJECT_ROOT / "models"

# Notebooks directory
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# CSV file paths
RAW_SEASON_FILES = {
    "2019_20": DATA_RAW / "upl_goals_2019_20.csv",
    "2020_21": DATA_RAW / "upl_goals_2020_21.csv",
    "2021_22": DATA_RAW / "upl_goals_2021_22.csv",
    "2022_23": DATA_RAW / "upl_goals_2022_23.csv",
    "2023_24": DATA_RAW / "upl_goals_2023_24.csv",
    "2024_25": DATA_RAW / "upl_goals_2024_25.csv",
    "2025_26": DATA_RAW / "upl_goals_2025_26.csv",
}

CLEANED_CSV = DATA_PROCESSED / "upl_goals_2019_2025_cleaned.csv"
FINAL_CSV = DATA_PROCESSED / "upl_goals_2019_2025_final.csv"

# Web scraping
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
)

UPL_BASE_URL = "https://upl.co.ug"
UPL_CALENDAR_URL = f"{UPL_BASE_URL}/calendar/{{season}}-fixtures-results/"
UPL_EVENT_URL_PREFIX = f"{UPL_BASE_URL}/event/"

# Scraping configuration
REQUEST_TIMEOUT = 10
SCRAPE_RETRY_ATTEMPTS = 3

# Team name corrections mapping
CLUB_NAME_CORRECTIONS = {
    "Vipers FC": "Vipers SC",
    "Bright Stars FC": "Soltilo Bright Stars FC",
    "Mbarara City": "Mbarara City FC",
    "Police": "Police FC",
    "Ondupraka FC": "Onduparaka FC",
    "Sc Villa": "SC Villa",
    "Gaddafi FC": "Entebbe UPPC FC",
    "Tooro United": "Tooro United FC",
    "Tooro FC": "Tooro United FC",
    "Mbaara City FC": "Mbarara City FC",
    "Onduparak FC": "Onduparaka FC",
    "Ondupararka FC": "Onduparaka FC",
    "KCCA": "KCCA FC",
}

# Uppercase abbreviations in team names
UPPERCASE_TERMS = {"fc", "sc", "kcca", "ura", "myda", "updf", "nec", "bul", "uppc"}

# Goal type constants
GOAL_TYPE_REGULAR = "Regular"
GOAL_TYPE_PENALTY = "Penalty"
GOAL_TYPE_OWN_GOAL = "Own Goal"

# Match sides
SIDE_HOME = "home"
SIDE_AWAY = "away"

# Analysis constants
SEASONS = ["2019/20", "2020/21", "2021/22", "2022/23", "2023/24", "2024/25"]
