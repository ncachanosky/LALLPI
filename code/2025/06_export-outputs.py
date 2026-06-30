"""
06_export_outputs.py

Final pipeline step: filters the panel down to country-years with real
data, selects and orders the published columns, exports the three
output formats (csv/xlsx/dta), and builds the missing-data report.

Input
-----
data/2025/interim/05_index_built.csv

Output
------
data/2025/output/index_2025.csv
data/2025/output/index_2025.xlsx
data/2025/output/index_2025.dta
data/2025/output/missing_data_2025.xlsx

Coverage filter
----------------
Per project decision: only country-years with at least one real data
point (EP, IP, or POP_R) are published -- the 568 (of 1,092) skeleton
rows with zero data from any source are micro-territories that were
never part of this index's real coverage. This matches the original
script's effective behavior (it used inner joins, which excluded
those rows implicitly along the way). The original script also
explicitly dropped Suriname and Guyana by name; both already have
zero real data in this panel, so that explicit drop turns out to be
redundant rather than removing real numbers -- not replicated as a
separate rule here, since the generic filter already covers it. This
may be revisited for a future index version depending on user
feedback.
"""

import pandas as pd

import config

PUBLISHED_COLUMNS = [
    "ISO2", "ISO3", "COUNTRY", "REGION", "LDC", "LLDC", "SIDS", "YEAR",
    "POP", "POP_RANK", "POP_PERCENTILE",
    "PIP", "PIP_RANK", "PIP_PERCENTILE",
    "IP", "IP_1", "IP_2", "IP_3", "IP_4", "IP_5", "IP_6",
    "PEP", "PEP_RANK", "PEP_PERCENTILE",
    "EP", "EP_1", "EP_2", "EP_3", "EP_4",
    "POP_R", "POP_R_RANK", "POP_R_PERCENTILE",
    "PARTY_CODE", "PARTY_NAME",
]

# Unicode dashes/apostrophes in party names that don't round-trip cleanly
# through Stata's fixed-width string encoding.
TEXT_REPLACEMENTS = {"\u2013": "-", "\u2019": "-"}


def filter_to_real_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only country-years with at least one real data point (EP, IP, or POP_R)."""
    has_data = df["EP"].notna() | df["IP"].notna() | df["POP_R"].notna()
    return df[has_data].copy()


def select_and_order_columns(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in PUBLISHED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Expected published column(s) missing from panel: {missing}")
    return df[PUBLISHED_COLUMNS].sort_values(["YEAR", "COUNTRY"]).reset_index(drop=True)


def clean_party_text(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize unicode dashes in PARTY_CODE/PARTY_NAME (see TEXT_REPLACEMENTS)."""
    df = df.copy()
    df["PARTY_CODE"] = df["PARTY_CODE"].replace(TEXT_REPLACEMENTS, regex=True)
    df["PARTY_NAME"] = df["PARTY_NAME"].replace(TEXT_REPLACEMENTS, regex=True)
    return df


def export_main_outputs(df: pd.DataFrame, output_dir) -> None:
    # NOTE: the original script's to_csv() call omitted index=False, leaving
    # a stray unnamed index column in the published CSV. That looked like an
    # oversight (not a cited/documented column) rather than intentional, so
    # it's fixed here -- flagging in case anything downstream depended on it.
    df.to_csv(output_dir / "index_2025.csv", index=False, encoding="utf-8")
    df.to_excel(output_dir / "index_2025.xlsx", index=False)
    df.to_stata(output_dir / "index_2025.dta", write_index=False)


def build_missing_data_report(df: pd.DataFrame) -> pd.DataFrame:
    """X / blank table showing which of POP, PIP, PEP, POP_R are present, by country-year."""
    keep = ["COUNTRY", "YEAR", "POP", "PIP", "PEP", "POP_R"]
    table = df[keep]
    missing = table.set_index(["COUNTRY", "YEAR"]).notna()
    missing = missing.replace({True: "X", False: ""})
    missing = missing.reset_index()
    return missing[keep]


def main() -> None:
    config.ensure_dirs()

    df = pd.read_csv(
        config.INTERIM_DIR / "05_index_built.csv", keep_default_na=False, na_values=[""]
    )
    print(f"Loaded {len(df)}-row panel from 05_build_index.py")

    df = filter_to_real_coverage(df)
    print(f"Filtered to {len(df)} country-years with real coverage")

    df = select_and_order_columns(df)
    df = clean_party_text(df)

    export_main_outputs(df, config.OUTPUT_DIR)
    print(f"Wrote index_2025.csv/.xlsx/.dta to {config.OUTPUT_DIR}")

    missing_table = build_missing_data_report(df)
    missing_path = config.OUTPUT_DIR / "missing_data_2025.xlsx"
    missing_table.to_excel(missing_path, index=False)
    print(f"Wrote {missing_path}")

    print(f"Final published panel: {df['ISO3'].nunique()} countries, "
          f"{df['YEAR'].min()}-{df['YEAR'].max()}, {len(df)} country-year rows")


if __name__ == "__main__":
    main()