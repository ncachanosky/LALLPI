"""
04_load_external.py

Loads V-Dem (institutional variables), Heritage's Index of Economic
Freedom (IEF), and Fraser's Economic Freedom of the World (EFW), and
merges them onto the V-Party-merged panel from 03_vparty_merge.py.

All three sources are rescaled here to a common [0, 100] *populism
direction* scale: higher = more consistent with populist policy/
institutional behavior, regardless of which direction the source
variable's own scale runs. See the named scale-factor constants below
for exactly how each source's native scale maps to that.

Input
-----
data/2025/interim/03_vparty_merged.csv   (from 03_vparty_merge.py)
data/2025/raw/V-Dem-13.dta
data/2025/raw/heritage.xlsx
data/2025/raw/efw.xlsx
    (raw third-party files; not tracked in git -- see README)

Output
------
data/2025/interim/04_external_merged.csv
    The 03 panel with VDEM_1..VDEM_6, HERITAGE_1..HERITAGE_6, and
    EFW_1..EFW_6 attached (NaN where a source has no match for that
    country-year).

Join keys
---------
V-Dem and EFW are merged on (ISO3, YEAR). Heritage is merged on
(ISO2, YEAR) -- its source file identifies countries by two-letter
code, not three-letter. This matches the original script's behavior;
flagging here since it's easy to assume every source joins the same
way and get a silent key mismatch.
"""

import pandas as pd

import config

# V-Dem variables: most are on a native [0, 1] scale.
VDEM_UNIT_SCALE = 100

# v2mecenefm_osp (freedom of expression) is on a native ~[0, 4] scale,
# not [0, 1] like the other V-Dem variables used here -- confirmed
# against the actual data (observed range ~0.02-3.94).
VDEM_FREEDOM_EXPRESSION_SCALE = 25

# Heritage IEF sub-indices are already scored 0-100 by construction;
# only an inversion (100 - x) is needed, no rescale factor.

# Fraser EFW sub-indices are scored 0-10 by construction.
EFW_SCALE = 10


def load_vdem(path) -> pd.DataFrame:
    """Load V-Dem institutional variables, rescaled to [0, 100] populism direction.

    Rule of law, judiciary constraints, and legislative constraints are
    inverted (strong constraints on the executive = less populist
    behavior). Corruption and neopatrimonialism are not inverted (more
    of either = more populist behavior, already in the right direction).
    Freedom of expression is inverted like the constraint variables.
    """
    if not path.exists():
        raise FileNotFoundError(f"{path} not found -- see README for source/version.")

    raw = pd.read_stata(path)
    raw = raw.rename(columns={"country_text_id": "ISO3", "year": "YEAR"})

    source_cols = {
        "v2x_rule": "VDEM_1",        # Rule of law (inverted)
        "v2x_jucon": "VDEM_2",       # Judiciary constraints on the executive (inverted)
        "v2xlg_legcon": "VDEM_3",    # Legislative constraints on the executive (inverted)
        "v2x_execorr": "VDEM_4",     # Corruption (not inverted)
        "v2x_neopat": "VDEM_5",      # Neopatrimonialism (not inverted)
        "v2mecenefm_osp": "VDEM_6",  # Freedom of expression (inverted)
    }
    missing = [c for c in source_cols if c not in raw.columns]
    if missing:
        raise ValueError(f"V-Dem file is missing expected column(s): {missing}")

    df = raw[["ISO3", "YEAR", *source_cols.keys()]].rename(columns=source_cols)

    for col in ["VDEM_1", "VDEM_2", "VDEM_3"]:
        df[col] = 100 - df[col] * VDEM_UNIT_SCALE
    for col in ["VDEM_4", "VDEM_5"]:
        df[col] = df[col] * VDEM_UNIT_SCALE
    df["VDEM_6"] = 100 - df["VDEM_6"] * VDEM_FREEDOM_EXPRESSION_SCALE

    return df


def load_heritage(path) -> pd.DataFrame:
    """Load Heritage IEF sub-indices, inverted to [0, 100] populism direction."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found -- see README for source/version.")

    raw = pd.read_excel(path)

    source_cols = {
        "ISO Code": "ISO2",
        "Index Year": "YEAR",
        "Property Rights": "HERITAGE_1",
        "Business Freedom": "HERITAGE_2",
        "Monetary Freedom": "HERITAGE_3",
        "Trade Freedom": "HERITAGE_4",
        "Financial Freedom": "HERITAGE_5",
        "Government Integrity": "HERITAGE_6",
    }
    missing = [c for c in source_cols if c not in raw.columns]
    if missing:
        raise ValueError(f"Heritage file is missing expected column(s): {missing}")

    df = raw[list(source_cols.keys())].rename(columns=source_cols)

    for col in [f"HERITAGE_{i}" for i in range(1, 7)]:
        df[col] = 100 - df[col]

    return df


def load_efw(path) -> pd.DataFrame:
    """Load Fraser EFW sub-indices, inverted and rescaled to [0, 100] populism direction.

    Selected by column letter (matching the original script) since the
    source workbook's header text has inconsistent internal spacing
    that makes exact-string matching fragile; renaming by position
    avoids depending on that text being byte-for-byte stable release
    to release.
    """
    if not path.exists():
        raise FileNotFoundError(f"{path} not found -- see README for source/version.")

    sheet = "EFW Ratings 1970-2021"
    cols = "B, D, K, T, AO, BH, BU, BZ"
    raw = pd.read_excel(path, sheet_name=sheet, skiprows=4, usecols=cols)

    expected_n_cols = 8
    if raw.shape[1] != expected_n_cols:
        raise ValueError(
            f"Expected {expected_n_cols} columns from {sheet!r} at {cols!r}, "
            f"got {raw.shape[1]}. The source workbook's layout may have changed."
        )

    # Column order is fixed by the usecols letter selection above:
    # Year, ISO3, [1B transfers/subsidies, IE state ownership,
    # 3D foreign currency accounts, 4 freedom to trade intl,
    # 5B labor market regs, 5C business regs]
    df = raw.copy()
    df.columns = ["YEAR", "ISO3", "EFW_1", "EFW_2", "EFW_3", "EFW_4", "EFW_5", "EFW_6"]

    for col in [f"EFW_{i}" for i in range(1, 7)]:
        df[col] = 100 - df[col] * EFW_SCALE

    return df


def main() -> None:
    config.ensure_dirs()

    panel = pd.read_csv(
        config.INTERIM_DIR / "03_vparty_merged.csv", keep_default_na=False, na_values=[""]
    )
    print(f"Loaded {len(panel)}-row panel from 03_vparty_merge.py")

    vdem = load_vdem(config.RAW_DIR / "V-Dem-13.dta")
    heritage = load_heritage(config.RAW_DIR / "heritage.xlsx")
    efw = load_efw(config.RAW_DIR / "efw.xlsx")
    print(f"Loaded V-Dem ({len(vdem)} rows), Heritage ({len(heritage)} rows), "
          f"EFW ({len(efw)} rows)")

    merged = panel.merge(vdem, on=["ISO3", "YEAR"], how="left")
    merged = merged.merge(heritage, on=["ISO2", "YEAR"], how="left")  # note: ISO2, not ISO3
    merged = merged.merge(efw, on=["ISO3", "YEAR"], how="left")

    assert len(merged) == len(panel), (
        f"Row count changed after merging external sources: {len(panel)} -> {len(merged)}. "
        "A source likely has duplicate (key, YEAR) rows causing a fan-out merge."
    )

    for source, cols in [
        ("V-Dem", [f"VDEM_{i}" for i in range(1, 7)]),
        ("Heritage", [f"HERITAGE_{i}" for i in range(1, 7)]),
        ("EFW", [f"EFW_{i}" for i in range(1, 7)]),
    ]:
        n_complete = merged[cols].notna().all(axis=1).sum()
        print(f"{source}: {n_complete} / {len(merged)} country-years fully populated")

    out_path = config.INTERIM_DIR / "04_external_merged.csv"
    merged.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()