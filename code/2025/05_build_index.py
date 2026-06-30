"""
05_build_index.py

Computes the populism sub-indices and the overall index from the merged
panel produced by 04_load_external.py:

    EP  = Economic Populism      (4-component average, Heritage + EFW)
    IP  = Institutional Populism (6-component average, V-Dem + Heritage)
    PEP = POP_R * EP
    PIP = POP_R * IP
    POP = (PEP + PIP) / 2

Formula notes (confirmed against the published documentation -- see
project notes, not re-litigated here)
-----------------------------------------------------------------------
- POP = (PEP + PIP) / 2. The published documentation states
  POP = PEP + PIP (no division). The CODE is authoritative per
  project decision; the documentation page needs updating to match,
  not the other way around.
- IP averages 6 components, not the 5 named in the documentation.
  VDEM_3 (legislative constraints) and VDEM_4 (corruption) are each
  used twice: once inside the IP_1/IP_2 composites, and again on
  their own as IP_3/IP_4. VDEM_6 (freedom of expression) is never
  used. This is confirmed-as-intended per project decision -- the
  calculation is unchanged from the original script. Only an
  inaccurate comment has been corrected (the original mislabeled
  IP_4 as "Freedom of the Press"; it is actually corruption data,
  duplicated from IP_2). The documentation needs updating to describe
  6 components, not 5.

Input
-----
data/2025/interim/04_external_merged.csv

Output
------
data/2025/interim/05_index_built.csv
    The panel with EP, EP_1..EP_4, IP, IP_1..IP_6, PEP, PIP, POP, and
    rank/percentile columns for POP, PEP, PIP, POP_R attached.
"""

import pandas as pd

import config


def compute_ep(df: pd.DataFrame) -> pd.DataFrame:
    """Economic Populism: 4-component average (Heritage + EFW, already in populism direction)."""
    df = df.copy()
    df["EP_1"] = (df["HERITAGE_2"] + df["EFW_5"] + df["EFW_6"]) / 3   # Business & labor regulation
    df["EP_2"] = (df["EFW_1"] + df["EFW_2"]) / 2                       # Government interference
    df["EP_3"] = (df["HERITAGE_3"] + df["HERITAGE_5"] + df["EFW_3"]) / 3  # Monetary & financial freedom
    df["EP_4"] = (df["HERITAGE_4"] + df["EFW_4"]) / 2                  # Freedom to trade

    df["EP"] = (df["EP_1"] + df["EP_2"] + df["EP_3"] + df["EP_4"]) / 4
    return df


def compute_ip(df: pd.DataFrame) -> pd.DataFrame:
    """Institutional Populism: 6-component average (V-Dem + Heritage).

    See module docstring -- IP_3 duplicates legislative constraints
    (already in IP_1), IP_4 duplicates corruption (already in IP_2),
    and freedom of expression (VDEM_6) is not used. Preserved exactly
    as-is per project decision; do not "fix" without sign-off.
    """
    df = df.copy()
    df["IP_1"] = (df["VDEM_1"] + df["VDEM_2"] + df["VDEM_3"]) / 3  # Rule of law composite
    df["IP_2"] = (df["VDEM_4"] + df["HERITAGE_6"]) / 2             # Corruption composite
    df["IP_3"] = df["VDEM_3"]   # Legislative constraints (duplicate of part of IP_1)
    df["IP_4"] = df["VDEM_4"]   # Corruption (duplicate of part of IP_2) -- NOT freedom of expression
    df["IP_5"] = df["VDEM_5"]   # Neopatrimonialism
    df["IP_6"] = df["HERITAGE_1"]  # Property rights

    df["IP"] = (df["IP_1"] + df["IP_2"] + df["IP_3"] + df["IP_4"] + df["IP_5"] + df["IP_6"]) / 6
    return df


def compute_pop(df: pd.DataFrame) -> pd.DataFrame:
    """PEP, PIP, POP, and rank/percentile columns within each YEAR."""
    df = df.copy()
    df["PEP"] = df["POP_R"] * df["EP"]
    df["PIP"] = df["POP_R"] * df["IP"]
    df["POP"] = (df["PEP"] + df["PIP"]) / 2  # see module docstring: code is authoritative

    for col in ["POP", "PEP", "PIP", "POP_R"]:
        df[f"{col}_RANK"] = df.groupby("YEAR")[col].rank(ascending=False)
        df[f"{col}_PERCENTILE"] = df.groupby("YEAR")[col].rank(pct=True)

    return df


def main() -> None:
    config.ensure_dirs()

    df = pd.read_csv(
        config.INTERIM_DIR / "04_external_merged.csv", keep_default_na=False, na_values=[""]
    )
    print(f"Loaded {len(df)}-row panel from 04_load_external.py")

    df = compute_ep(df)
    df = compute_ip(df)
    df = compute_pop(df)

    n_pop = df["POP"].notna().sum()
    n_ep_only = (df["EP"].notna() & df["POP"].isna()).sum()
    n_ip_only = (df["IP"].notna() & df["POP"].isna()).sum()
    print(f"POP computed for {n_pop} / {len(df)} country-years")
    print(f"({n_ep_only} have EP but not POP, {n_ip_only} have IP but not POP -- "
          "missing POP_R or the other sub-index)")

    out_path = config.INTERIM_DIR / "05_index_built.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()