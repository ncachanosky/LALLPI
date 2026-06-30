"""
02_vparty_prepare.py

Loads V-Party's populism (rhetoric) score, filters to the countries this
index covers, and interpolates missing observations within each
country/party series.

This step does NOT yet decide which party governed in years with a
change of government -- that human judgment call is applied in
03_vparty_merge.py via the data/2025/vparty_overrides.csv file. This
script's job is only to prepare the candidate data for that decision.

Input
-----
data/2025/raw/V-Party-2.dta
    Raw V-Party dataset (download separately -- see README; not tracked
    in git). Must contain country_text_id, year, v2paid, v2paenname,
    v2pashname, v2xpa_popul.
data/2025/countries.csv
    Used as the single source of truth for which ISO3 codes belong to
    this index, instead of a second hardcoded country list.

Output
------
data/2025/interim/02_vparty_interpolated.csv
    Tidy long format: ISO3, YEAR, v2paid, v2paenname, v2pashname, VPARTY.
    One row per (country, party, year) with non-null v2xpa_popul at any
    point in that party's series. Most country-years have several rows
    -- one per active party in that country's system that year -- since
    V-Party scores every party, not just the one in government. Picking
    out the governing party for each country-year is a human research
    task applied in 03_vparty_merge.py via vparty_overrides.csv, not
    something this script can infer.

Known data note
----------------
countries.csv currently lists Aruba's ISO3 code as "SBW". The real ISO
3166-1 alpha-3 code for Aruba is "ABW", which is what V-Party actually
uses. This mismatch means Aruba rows have never matched between the
skeleton and V-Party in the original script either (the merge step
silently drops them) -- flagging here since this script is where the
mismatch first becomes visible, but not changing countries.csv without
sign-off, since it's possible something else depends on the existing
code.
"""

from pathlib import Path

import pandas as pd

import config

MIN_YEAR = 1990


def load_vparty_raw(path: Path) -> pd.DataFrame:
    """Load the raw V-Party file and select/rename only the columns this index needs."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Download V-Party-2.dta and place it in {path.parent} "
            "(see README for the source/version to use; not tracked in git)."
        )

    raw = pd.read_stata(path)
    raw = raw.rename(columns={"country_text_id": "ISO3", "year": "YEAR"})

    keep_cols = ["ISO3", "YEAR", "v2paid", "v2paenname", "v2pashname", "v2xpa_popul"]
    missing = [c for c in keep_cols if c not in raw.columns]
    if missing:
        raise ValueError(f"V-Party file is missing expected column(s): {missing}")

    return raw[keep_cols]


def filter_to_index_countries(
    df: pd.DataFrame,
    countries_file: Path = config.COUNTRIES_FILE,
    min_year: int = MIN_YEAR,
) -> pd.DataFrame:
    """Restrict to this index's countries (via countries.csv) and years >= min_year."""
    countries = pd.read_csv(countries_file, keep_default_na=False, na_values=[""])
    index_iso3 = countries["ISO3"].unique().tolist()

    filtered = df[(df["YEAR"] >= min_year) & (df["ISO3"].isin(index_iso3))].copy()
    return filtered


def interpolate_vparty(df: pd.DataFrame) -> pd.DataFrame:
    """Interpolate each (country, party) populism series across years.

    Returns a tidy long-format DataFrame: ISO3, YEAR, v2paid, v2paenname,
    v2pashname, VPARTY -- one row per (country, party, year) that the
    party has any non-null value for, after interpolating internal gaps.
    """
    df = df.sort_values(["ISO3", "v2paenname", "YEAR"])

    wide = df.pivot(
        index="YEAR",
        values="v2xpa_popul",
        columns=["ISO3", "v2paid", "v2paenname", "v2pashname"],
    )
    wide = wide.interpolate()
    wide = wide.sort_index(axis=1)

    long = wide.stack(["ISO3", "v2paid", "v2paenname", "v2pashname"], future_stack=True)
    long = long.rename("VPARTY").reset_index()
    long = long.dropna(subset=["VPARTY"])

    return long.sort_values(["ISO3", "YEAR", "v2paid"]).reset_index(drop=True)


def main() -> None:
    config.ensure_dirs()

    raw_path = config.RAW_DIR / "V-Party-2.dta"
    raw = load_vparty_raw(raw_path)
    print(f"Loaded {len(raw)} raw V-Party rows")

    filtered = filter_to_index_countries(raw)
    print(f"Filtered to {len(filtered)} rows for index countries, YEAR >= {MIN_YEAR}")

    interpolated = interpolate_vparty(filtered)
    print(f"Interpolated to {len(interpolated)} (country, party, year) rows")

    n_country_years = interpolated.groupby(["ISO3", "YEAR"]).ngroups
    print(
        f"{n_country_years} distinct country-years, with multiple active parties "
        "in most of them (this is normal V-Party structure -- every party in the "
        "system gets a score, not just the one in government). Picking the "
        "governing party for each country-year is the job of "
        "vparty_overrides.csv in 03_vparty_merge.py."
    )

    out_path = config.INTERIM_DIR / "02_vparty_interpolated.csv"
    interpolated.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()