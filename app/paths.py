from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_S1_DIR = BASE_DIR / "data" / "scraper_1"
DATA_S2_DIR = BASE_DIR / "data" / "scraper_2"
LOGS_S1_FILE = BASE_DIR / "scrapers" / "scraper_1" / "logs" / "logs.csv"
LOGS_S2_FILE = BASE_DIR / "scrapers" / "scraper_2" / "logs" / "logs.csv"
