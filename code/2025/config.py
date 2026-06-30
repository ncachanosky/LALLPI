"""
config.py

Shared configuration for the 2025-vintage LALLPI pipeline.

Lives in code/2025/ alongside that year's numbered pipeline scripts.
Each future index vintage gets its own code/<year>/ folder with its own
copy of this file (INDEX_YEAR updated accordingly) -- vintages are kept
self-contained rather than sharing one global config, since a given
year's pipeline should keep working unmodified even if a later year's
pipeline changes its data sources or structure.

Centralizes file paths and run-wide constants so individual pipeline
scripts (01_..., 02_..., etc.) never hardcode a directory path.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Vintage. Bump this (and copy this whole code/<year>/ folder) to start a
# new index year rather than editing data sources in place.
# ---------------------------------------------------------------------------
INDEX_YEAR = "2025"

# ---------------------------------------------------------------------------
# Project root: two levels up from this file (code/<year>/config.py ->
# code/<year> -> code -> repo root). Using __file__ instead of a hardcoded
# string means the pipeline runs correctly no matter where the repo is
# cloned on a collaborator's machine.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Data directories, all nested under this vintage's data/<year>/ folder.
# ---------------------------------------------------------------------------
DATA_DIR = PROJECT_ROOT / "data" / INDEX_YEAR

# Raw third-party source files (V-Party, V-Dem, Heritage, EFW). NOT tracked
# in git -- see README for download instructions and licensing notes.
RAW_DIR = DATA_DIR / "raw"

# Intermediate outputs written by each numbered pipeline script. Gitignored
# and fully regenerable by rerunning the pipeline from data in RAW_DIR.
INTERIM_DIR = DATA_DIR / "interim"

# Final published outputs (csv/xlsx/dta + missing-data report). Tracked in
# git -- this is what the website and downstream Stata users consume.
OUTPUT_DIR = DATA_DIR / "output"

# Country metadata table (ISO codes, region, LDC/LLDC/SIDS flags).
# Year-versioned: each vintage can adjust its own country list.
COUNTRIES_FILE = DATA_DIR / "countries.csv"

# ---------------------------------------------------------------------------
# Panel coverage
# ---------------------------------------------------------------------------
START_YEAR = 2000
END_YEAR = 2020


def ensure_dirs() -> None:
    """Create the interim and output directories if they don't exist yet.

    Raw/reference directories are NOT created here -- if they're missing,
    that's a signal the user hasn't placed the source data yet, and a
    script should fail with a clear error rather than silently proceeding.
    """
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)