"""
01_build_skeleton.py

Builds the empty country/year panel skeleton that every later pipeline
step merges data onto.

Input
-----
data/countries.csv
    Versioned country metadata: ISO2, ISO3, COUNTRY, REGION, and the
    LDC/LLDC/SIDS flags. One row per country (no year dimension).

Output
------
data/interim/01_skeleton.csv
    One row per (country, year) for YEAR in [config.START_YEAR,
    config.END_YEAR], inclusive. Columns: ISO2, ISO3, YEAR, COUNTRY,
    REGION, LDC, LLDC, SIDS.

Notes
-----
The ISO2 column uses the literal string "NA" to mean "this territory has
no ISO 3166-1 alpha-2 code" (e.g. Bouvet Island, the Falklands). Pandas'
read_csv treats "NA" as a missing-value marker by default, which would
silently turn those rows into real NaN instead of the string "NA". We
disable that default here with keep_default_na=False.
"""

import pandas as pd

import config


def build_country_skeleton(
    countries_file=config.COUNTRIES_FILE,
    start_year: int = config.START_YEAR,
    end_year: int = config.END_YEAR,
) -> pd.DataFrame:
    """Cross-join country metadata with a year range to build the panel skeleton.

    Parameters
    ----------
    countries_file : Path
        Path to the country metadata CSV (no year column).
    start_year, end_year : int
        Inclusive year range for the panel.

    Returns
    -------
    pd.DataFrame
        One row per (country, year), columns:
        ISO2, ISO3, YEAR, COUNTRY, REGION, LDC, LLDC, SIDS.
    """
    countries = pd.read_csv(
        countries_file,
        keep_default_na=False,  # see module docstring: "NA" is a real ISO2 value here
        na_values=[""],         # only an empty cell counts as missing
    )

    expected_cols = {"ISO2", "ISO3", "COUNTRY", "REGION", "LDC", "LLDC", "SIDS"}
    missing_cols = expected_cols - set(countries.columns)
    if missing_cols:
        raise ValueError(
            f"{countries_file} is missing expected column(s): {sorted(missing_cols)}"
        )

    years = pd.DataFrame({"YEAR": range(start_year, end_year + 1)})

    skeleton = countries.merge(years, how="cross")

    column_order = ["ISO2", "ISO3", "YEAR", "COUNTRY", "REGION", "LDC", "LLDC", "SIDS"]
    skeleton = skeleton[column_order].sort_values(["COUNTRY", "YEAR"]).reset_index(drop=True)

    return skeleton


def main() -> None:
    config.ensure_dirs()

    skeleton = build_country_skeleton()

    n_countries = skeleton["ISO3"].nunique()
    n_years = skeleton["YEAR"].nunique()
    expected_rows = n_countries * n_years
    assert len(skeleton) == expected_rows, (
        f"Skeleton has {len(skeleton)} rows, expected {n_countries} countries "
        f"x {n_years} years = {expected_rows}. Check countries.csv for duplicate ISO3 codes."
    )

    out_path = config.INTERIM_DIR / "01_skeleton.csv"
    skeleton.to_csv(out_path, index=False)
    print(f"Wrote {len(skeleton)} rows ({n_countries} countries x {n_years} years) to {out_path}")


if __name__ == "__main__":
    main()