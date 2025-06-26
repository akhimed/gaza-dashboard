# fetch_data.py
import pandas as pd
from pathlib import Path
import requests
import io

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Primary & fallback sources
CSV_URL = "https://data.techforpalestine.org/api/v2/casualties_daily.csv"
JSON_URL = "https://raw.githubusercontent.com/TechForPalestine/palestine-datasets/main/casualties_daily.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}  # Trick server into treating us like a browser

def get_data(refresh: bool = False) -> pd.DataFrame:
    today_str = pd.Timestamp.today().strftime("%Y-%m-%d")
    local_file = RAW_DIR / f"gaza_daily_{today_str}.csv"

    # if local file already exists
    if not refresh and local_file.exists():
        return pd.read_csv(local_file, parse_dates=["report_date"]).sort_values("report_date")

    # attempt CSV pull
    try:
        print("Trying primary CSV source...")
        response = requests.get(CSV_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        df = pd.read_csv(io.BytesIO(response.content), parse_dates=["report_date"])
        df.to_csv(local_file, index=False)
        return df.sort_values("report_date")

    except Exception as e:
        print(f"CSV fetch failed, falling back to JSON: {e}")

    # fallback to JSON
    try:
        print("Trying fallback JSON source...")
        response = requests.get(JSON_URL, timeout=15)
        response.raise_for_status()
        df = pd.read_json(response.content)
        df["report_date"] = pd.to_datetime(df["report_date"])
        df.to_csv(local_file, index=False)
        return df.sort_values("report_date")

    except Exception as e:
        raise RuntimeError(f"Failed to load data from both CSV and JSON sources.\nError: {e}")
