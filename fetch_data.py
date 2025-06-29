# fetch_data.py
"""
Download the latest Gaza casualty dataset and keep TWO copies:
1. An archive copy stamped with today’s date (e.g., gaza_daily_2025-06-28.csv)
2. A single, always-overwritten file – gaza_daily.csv – that Tableau (or anything
   else) can point to for automatic refreshes.

Usage
-----
>>> from fetch_data import get_data
>>> df = get_data()          # pulls fresh data if needed, returns DataFrame
>>> df.head()
"""
import io
from pathlib import Path
import requests, pandas as pd, pathlib, datetime as dt

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

CSV_URL   = "https://data.techforpalestine.org/api/v2/casualties_daily.csv"
JSON_URL  = "https://raw.githubusercontent.com/TechForPalestine/palestine-datasets/main/casualties_daily.json"
HEADERS   = {"User-Agent": "Mozilla/5.0"}                # pretend we’re a browser

# Filename that Tableau will use
STATIC_FILE = RAW_DIR / "casualties_daily.csv"


# --------------------------------------------------------------------------- #
# Main helper
# --------------------------------------------------------------------------- #
def get_data(refresh: bool = False) -> pd.DataFrame:
    """
    Return a DataFrame of Gaza casualty data, refreshing from the web only when
    *refresh* is True or the static file doesn’t exist/looks stale.

    Parameters
    ----------
    refresh : bool, default False
        Force a download even if today's data already exists.

    Returns
    -------
    pandas.DataFrame
        Sorted by report_date ascending.
    """
    today = pd.Timestamp.now().normalize()               # midnight today
    archive_file = RAW_DIR / f"gaza_daily_{today.date()}.csv"

    # ------------------------------------------------------------------ #
    # Short-circuit: if we already have a static file modified today and
    # refresh=False, just read it.
    # ------------------------------------------------------------------ #
    # if (
    #     STATIC_FILE.exists()
    #     and not refresh
    #     and pd.Timestamp(STATIC_FILE.stat().st_mtime, unit="s") >= today
    # ):
    #     return (
    #         pd.read_csv(STATIC_FILE, parse_dates=["report_date"])
    #         .sort_values("report_date")
    #     )

    # ------------------------------------------------------------------ #
    # Helper for downloading from a URL into a DataFrame
    # ------------------------------------------------------------------ #
    def _download_csv(url: str) -> pd.DataFrame:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return pd.read_csv(io.BytesIO(resp.content), parse_dates=["report_date"])

    # Try primary CSV ---------------------------------------------------- #
    try:
        print("🔄  Fetching CSV from primary source …")
        df = _download_csv(CSV_URL)

    except Exception as exc_csv:
        print(f"⚠️  CSV fetch failed ({exc_csv}); trying JSON fallback …")
        try:
            resp = requests.get(JSON_URL, timeout=15)
            resp.raise_for_status()
            df = pd.read_json(resp.content)
            df["report_date"] = pd.to_datetime(df["report_date"])
        except Exception as exc_json:
            raise RuntimeError(
                "Failed to load data from both CSV and JSON sources."
            ) from exc_json

    # ------------------------------------------------------------------ #
    # Save copies: archive + static (overwrite)
    # ------------------------------------------------------------------ #
    df.sort_values("report_date", inplace=True)
    df.to_csv(archive_file, index=False)   # keep a dated snapshot
    df.to_csv(STATIC_FILE, index=False)    # Tableau-friendly path (overwrite)

    return df


# fetch_data.py  (bottom of file)
# ------------------------------------------------------------ #
# --------------------------------------------------------------------------- #
# “Killed in Gaza” – victims-level dataset
# --------------------------------------------------------------------------- #
NAMES_URL = "https://data.techforpalestine.org/api/v2/killed-in-gaza.csv"
CACHE     = RAW_DIR / "killed_names.csv"      # same folder as other raw data
TTL       = dt.timedelta(hours=12)            # refresh at most twice a day

# ── column aliases (dataset has changed a few times) ────────────────────────
ALIASES: dict[str, list[str]] = {
    "id":      ["id", "ID", "victim_id"],
    "english": ["en_name", "english", "english_name"],
    "arabic":  ["name", "arabic_name"],
    "age":     ["age", "Age"],
    "sex":     ["sex", "gender", "Sex"],
    "dob":     ["dob", "date_of_birth", "DoB"],
    "source":  ["source", "Src"],
    "date":    ["report_date", "date", "Date"],
}


# def _find(colset: set[str], options: list[str]) -> str | None:
#     """Return the first option present in *colset* (else None)."""
#     return next((c for c in options if c in colset), None)


# --------------------------------------------------------------------------- #
# Helper: load / cache the victims file
# --------------------------------------------------------------------------- #
def get_names_df(refresh: bool = False) -> pd.DataFrame:
    ...
    df = pd.read_csv(
        CACHE,
        engine="python", on_bad_lines="skip", encoding="utf-8"
    )

    # keep & rename only existing columns
    keep = {
        "id":        "id",
        "en_name":   "english_name",
        "age":       "age",
        "sex":       "sex",
        "dob":       "dob",          # keep date-of-birth
        "source":    "source",
    }
    df = df[list(keep)].rename(columns=keep)

    df["id"]  = pd.to_numeric(df["id"],  errors="coerce")
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["dob"] = pd.to_datetime(df["dob"], errors="coerce")   # optional

    # no report_date to sort by → just reset the index
    df = df.reset_index(drop=True)
    return df
