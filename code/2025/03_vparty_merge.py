"""
03_vparty_merge.py

Applies the human-curated "which party governs" decision for each
country-year, resolves the corresponding V-Party populism score, and
merges the result onto the full country/year skeleton.

This replaces the original pipeline's Excel PARTY_GOV -> HLOOKUP formula
chain (see data/2025/vparty_overrides.csv header / README for why: the
formula chain silently lost its cached results whenever the workbook
was resaved by anything other than Excel itself).

Input
-----
data/2025/interim/01_skeleton.csv   (from 01_build_skeleton.py)
data/2025/interim/02_vparty_interpolated.csv   (from 02_vparty_prepare.py)
data/2025/vparty_overrides.csv
    One row per (ISO3, YEAR) this index has V-Party coverage for, naming
    which party (PARTY_GOV, a V-Party party ID) was in government that
    year. This is curated, versioned human judgment -- extend it by
    adding rows, not by editing pipeline code. Originally extracted
    from the legacy VParty (old).xlsx workbook's PARTY_GOV column
    (685 rows); maintain it directly as a CSV going forward.

Output
------
data/2025/interim/03_vparty_merged.csv
    The skeleton (1,092 rows: all countries x all years) with POP_R
    (the resolved V-Party populism score for the governing party) and
    PARTY_CODE / PARTY_NAME attached where available. POP_R is NaN for
    any country-year outside V-Party's/this index's coverage.

Known gap fixes
----------------
A handful of country-years have a correct PARTY_GOV decision but the
governing party's own V-Party series doesn't reach that year (e.g. a
newly-formed coalition with no V-Party history yet). The original
script bridged these with an explicit backward-fill from the nearest
later year. We keep that as documented, named exceptions rather than a
generic auto-fill, since silently bridging gaps elsewhere could mask
real coverage problems. Each fix is checked before being applied and
skipped (with a message) if the data no longer needs it.
"""

import pandas as pd

import config

# (country, year missing a value, year to bridge from). Matches the
# original script's ARG 2003/2004 and NIC 2002 patches.
KNOWN_GAP_FIXES = [
    ("ARG", 2003, 2005),
    ("ARG", 2004, 2005),
    ("NIC", 2002, 2003),
]


def load_overrides(path=None) -> pd.DataFrame:
    path = path or (config.DATA_DIR / "vparty_overrides.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. This file is hand-maintained -- see README."
        )
    return pd.read_csv(path)


def resolve_governing_party(interpolated: pd.DataFrame, overrides: pd.DataFrame) -> pd.DataFrame:
    """For each (ISO3, YEAR) override, look up that party's interpolated V-Party score.

    Left join from overrides (the human decision) so every curated
    country-year is preserved even if the named party happens to have
    no interpolated score that year (see KNOWN_GAP_FIXES) -- that
    situation should be visible as a NaN, not silently dropped.
    """
    resolved = overrides.merge(
        interpolated[["ISO3", "YEAR", "v2paid", "VPARTY"]],
        left_on=["ISO3", "YEAR", "PARTY_GOV"],
        right_on=["ISO3", "YEAR", "v2paid"],
        how="left",
    )
    resolved = resolved.rename(columns={"VPARTY": "POP_R"})
    return resolved[["ISO3", "YEAR", "POP_R", "PARTY_GOV", "PARTY_CODE", "PARTY_NAME"]]


def apply_known_gap_fixes(df: pd.DataFrame) -> pd.DataFrame:
    """Bridge the small set of documented, named gaps from KNOWN_GAP_FIXES."""
    df = df.copy()
    for iso3, target_year, source_year in KNOWN_GAP_FIXES:
        target_mask = (df["ISO3"] == iso3) & (df["YEAR"] == target_year)
        source_mask = (df["ISO3"] == iso3) & (df["YEAR"] == source_year)

        if not df.loc[target_mask, "POP_R"].isna().all():
            print(f"  {iso3} {target_year}: already has a value, skipping documented fix")
            continue

        source_value = df.loc[source_mask, "POP_R"]
        if source_value.empty or source_value.isna().all():
            print(f"  WARNING: {iso3} {target_year} still has no value, and source "
                  f"year {source_year} has none either -- fix did not apply")
            continue

        df.loc[target_mask, "POP_R"] = source_value.values[0]
        print(f"  {iso3} {target_year}: filled from {source_year} ({source_value.values[0]})")

    return df


def merge_onto_skeleton(skeleton: pd.DataFrame, resolved: pd.DataFrame) -> pd.DataFrame:
    merged = skeleton.merge(
        resolved.drop(columns=["PARTY_GOV"]),
        on=["ISO3", "YEAR"],
        how="left",  # preserve the full skeleton; see note in 01_build_skeleton.py
    )
    return merged


def main() -> None:
    config.ensure_dirs()

    skeleton = pd.read_csv(
        config.INTERIM_DIR / "01_skeleton.csv", keep_default_na=False, na_values=[""]
    )
    interpolated = pd.read_csv(config.INTERIM_DIR / "02_vparty_interpolated.csv")
    overrides = load_overrides()
    print(f"Loaded {len(overrides)} governing-party override decisions")

    resolved = resolve_governing_party(interpolated, overrides)
    n_missing_before = resolved["POP_R"].isna().sum()
    print(f"{n_missing_before} override rows have no matching interpolated V-Party value")

    print("Applying known gap fixes:")
    resolved = apply_known_gap_fixes(resolved)

    merged = merge_onto_skeleton(skeleton, resolved)

    n_with_data = merged["POP_R"].notna().sum()
    print(f"Merged onto skeleton: {len(merged)} rows, {n_with_data} with a POP_R value")

    # Surface any remaining gaps for human review rather than silently
    # carrying them forward -- a curated override exists for this exact
    # (ISO3, YEAR) pair, but the resulting POP_R is still missing after
    # the known fixes.
    override_pairs = set(zip(overrides["ISO3"], overrides["YEAR"]))
    merged_pairs = list(zip(merged["ISO3"], merged["YEAR"]))
    has_override = pd.Series(
        [pair in override_pairs for pair in merged_pairs], index=merged.index
    )
    still_missing = merged[has_override & merged["POP_R"].isna()]
    if len(still_missing):
        print(
            f"NOTE: {len(still_missing)} country-years have an override decision context "
            "but still ended up with no POP_R value after known fixes -- review:"
        )
        print(still_missing[["ISO3", "YEAR"]].to_string(index=False))

    out_path = config.INTERIM_DIR / "03_vparty_merged.csv"
    merged.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()