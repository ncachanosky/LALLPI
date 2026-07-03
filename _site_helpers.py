"""
_site_helpers.py

Shared helpers for building live, data-driven HTML snippets used across
multiple .qmd pages (currently: index.qmd and pages/documentation.qmd
both embed the same country ranking table). Factored out to one place
so the two pages can't silently drift out of sync with each other --
the same risk this whole approach exists to avoid in the first place.

Requires execute-dir: project in _quarto.yml (already set) so that a
plain `import _site_helpers` works from a .qmd in any subfolder.
"""

import pandas as pd

# Single source of truth for which countries have a generated page at
# pages/countries/<slug>.qmd, and what URL slug each uses. Shared by
# build_ranking_table_html() (to link country names) and
# generate_country_pages.py (to know what to generate) so the two
# can't drift out of sync with each other. CUB, GUY, and SUR are
# deliberately absent -- each has some data but never a complete POP
# value for any year (see project notes), so there's no "latest year"
# to build a page around; country_summary() returns None for them.
COUNTRY_SLUGS = {
    "ARG": "argentina",
    "BRB": "barbados",
    "BOL": "bolivia",
    "BRA": "brazil",
    "CHL": "chile",
    "COL": "colombia",
    "CRI": "costa-rica",
    "DOM": "dominican-republic",
    "ECU": "ecuador",
    "SLV": "el-salvador",
    "GTM": "guatemala",
    "HTI": "haiti",
    "HND": "honduras",
    "JAM": "jamaica",
    "MEX": "mexico",
    "NIC": "nicaragua",
    "PAN": "panama",
    "PRY": "paraguay",
    "PER": "peru",
    "TTO": "trinidad-y-tobago",
    "URY": "uruguay",
    "VEN": "venezuela",
}


def build_ranking_table_html(index_csv_path: str, year: int) -> str:
    """Build the HTML for the country ranking table for a given year.

    Pulls directly from the published index CSV -- see index.qmd's
    comments for why this matters (the old site's hand-copied table
    had gone stale relative to the actual data).
    """
    df = pd.read_csv(index_csv_path)
    year_data = df[(df["YEAR"] == year) & (df["POP"].notna())].copy()
    year_data = year_data.sort_values("POP", ascending=False).reset_index(drop=True)

    rows_html = []
    for i, r in year_data.iterrows():
        rank = i + 1
        flag_url = f"https://flagcdn.com/w40/{r['ISO2'].lower()}.png"
        slug = COUNTRY_SLUGS.get(r["ISO3"])
        if slug:
            country_label = f'<a href="/pages/countries/{slug}.html">{r["COUNTRY"]}</a>'
        else:
            # Shouldn't happen in practice -- every country with a POP
            # value (required to appear in this table at all) is in
            # COUNTRY_SLUGS -- but fall back to plain text rather than
            # a broken link if the two ever do drift apart.
            country_label = r["COUNTRY"]
        rows_html.append(f"""    <tr>
      <td><div class="country"><img class="flag" src="{flag_url}" alt="{r['COUNTRY']} flag">{country_label}</div></td>
      <td>{r['POP']:.1f} ({rank})</td>
      <td>{r['EP']:.1f}</td>
      <td>{r['IP']:.1f}</td>
      <td>{r['POP_R']:.2f}</td>
    </tr>""")

    return f"""<table class="lallpi-ranking">
  <thead>
    <tr>
      <th>Country</th>
      <th>Overall populism</th>
      <th>Economic populism</th>
      <th>Institutional populism</th>
      <th>Populist rhetoric</th>
    </tr>
  </thead>
  <tbody>
{chr(10).join(rows_html)}
  </tbody>
</table>"""


def apply_chart_style():
    """Shared matplotlib styling for all documentation-page charts.

    Academic/professional look: open axes (no top/right spines),
    light y-gridlines only, no legend frame, consistent sizing.
    Called once per chart chunk rather than duplicating these settings
    three times -- keeps the charts from drifting out of sync with
    each other as the site evolves.

    Uses a generic sans-serif font rather than forcing Roboto Condensed:
    matplotlib needs the font file actually installed on whatever
    machine renders the site, which can't be verified here, and a
    silent fallback or build error is worse than a slightly plainer
    (but reliable) font.
    """
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "axes.edgecolor": "#041E42",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": "#B1B3B3",
        "grid.alpha": 0.3,
        "grid.linewidth": 0.6,
        "legend.frameon": False,
        "xtick.color": "#041E42",
        "ytick.color": "#041E42",
        "text.color": "#041E42",
        "axes.labelcolor": "#041E42",
    })


# ---------------------------------------------------------------------------
# Country page helpers
# ---------------------------------------------------------------------------

EP_LABELS = {
    "EP_1": "Business & labor regulation",
    "EP_2": "Government interference",
    "EP_3": "Monetary & financial freedom",
    "EP_4": "Freedom to trade",
}
IP_LABELS = {
    "IP_1": "Rule of law",
    "IP_2": "Corruption",
    "IP_3": "Legislative constraints",
    "IP_4": "Corruption (duplicate)",
    "IP_5": "Neopatrimonialism",
    "IP_6": "Property rights",
}


def country_data(df, iso3):
    """All rows for one country, sorted by year."""
    return df[df["ISO3"] == iso3].sort_values("YEAR")


def country_summary(df, iso3):
    """Latest year with a real POP value for this country, as a dict."""
    d = country_data(df, iso3)
    d = d[d["POP"].notna()]
    if d.empty:
        return None
    latest = d.iloc[-1]
    n_countries_that_year = df[(df["YEAR"] == latest["YEAR"]) & df["POP"].notna()]["ISO3"].nunique()
    return {
        "country": latest["COUNTRY"],
        "iso2": latest["ISO2"],
        "region": latest["REGION"],
        "year": int(latest["YEAR"]),
        "pop": latest["POP"],
        "rank": int(latest["POP_RANK"]),
        "n_countries": n_countries_that_year,
        "percentile": latest["POP_PERCENTILE"],
        "first_year": int(d["YEAR"].min()),
        "last_year": int(d["YEAR"].max()),
        "n_years": len(d),
    }


def _reindex_full_years(d, value_cols):
    """Reindex a country's data onto its full year range (min to max),
    leaving NaN for years with no data. This makes matplotlib break the
    line across real gaps instead of drawing a straight (misleading)
    line connecting across years with no data -- e.g. Colombia has data
    for 2000-2002 and 2011-2019 but nothing in between; a naive plot of
    the non-null rows alone draws a smooth line straight across that
    9-year gap, implying a trend that isn't actually observed.
    """
    full_years = range(int(d["YEAR"].min()), int(d["YEAR"].max()) + 1)
    d = d.set_index("YEAR").reindex(full_years)[value_cols]
    d.index.name = "YEAR"
    return d.reset_index()


def build_country_trend_chart(df, iso3):
    """POP/PEP/PIP over time for one country -- same visual language as the
    regional chart on the Documentation page, filtered to a single country.
    Gaps in year coverage are shown as real gaps, not smoothed over."""
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    apply_chart_style()
    d = country_data(df, iso3)
    d = d[d["YEAR"].between(d[d["POP"].notna()]["YEAR"].min(), d[d["POP"].notna()]["YEAR"].max())]
    d = _reindex_full_years(d, ["POP", "PEP", "PIP"])

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(d["YEAR"], d["PIP"], color="#FF8200", linewidth=2, marker="o", markersize=4, label="PIP (institutional)")
    ax.plot(d["YEAR"], d["POP"], color="#041E42", linewidth=2, marker="o", markersize=4, label="POP (overall)")
    ax.plot(d["YEAR"], d["PEP"], color="#B1B3B3", linewidth=2, marker="o", markersize=4, label="PEP (economic)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Score")
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.22)
    return fig


def build_subindex_breakdown_chart(df, iso3):
    """Horizontal bar chart of the latest year's EP_1-4 and IP_1-6 components."""
    import matplotlib.pyplot as plt

    apply_chart_style()
    d = country_data(df, iso3).dropna(subset=["POP"])
    if d.empty:
        return None
    latest = d.iloc[-1]

    labels, values, colors = [], [], []
    for col, label in EP_LABELS.items():
        labels.append(f"{label} ({col})")
        values.append(latest[col])
        colors.append("#B1B3B3")
    for col, label in IP_LABELS.items():
        labels.append(f"{label} ({col})")
        values.append(latest[col])
        colors.append("#FF8200")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    y_pos = range(len(labels))
    ax.barh(y_pos, values, color=colors)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(f"Score ({int(latest['YEAR'])})")
    ax.set_xlim(0, 100)
    fig.tight_layout()
    return fig


def build_regional_comparison_chart(df, iso3):
    """Country POP vs. its region's average POP, over the country's own year range.
    Gaps in the country's year coverage are shown as real gaps."""
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    apply_chart_style()
    d_raw = country_data(df, iso3)
    valid = d_raw[d_raw["POP"].notna()]
    if valid.empty:
        return None
    region = valid["REGION"].iloc[0]
    country_name = valid["COUNTRY"].iloc[0]

    d = d_raw[d_raw["YEAR"].between(valid["YEAR"].min(), valid["YEAR"].max())]
    d = _reindex_full_years(d, ["POP"])
    years = d["YEAR"].tolist()

    region_df = df[(df["REGION"] == region) & (df["YEAR"].isin(years)) & df["POP"].notna()]
    region_avg = region_df.groupby("YEAR")["POP"].mean().reindex(years)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(d["YEAR"], d["POP"], color="#FF8200", linewidth=2.5, marker="o", markersize=4, label=country_name)
    ax.plot(region_avg.index, region_avg.values, color="#B1B3B3", linewidth=2, linestyle="--", label=f"{region} average")
    ax.set_xlabel("Year")
    ax.set_ylabel("POP")
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.2)
    return fig


def build_party_history_table_html(df, iso3):
    """HTML table of YEAR / governing party / POP_R for one country, most recent year first."""
    d = country_data(df, iso3).dropna(subset=["POP_R"])
    if d.empty:
        return "<p><em>No governing-party data available.</em></p>"
    d = d.sort_values("YEAR", ascending=False)

    rows = []
    for _, r in d.iterrows():
        party = r["PARTY_NAME"] if pd.notna(r["PARTY_NAME"]) else "--"
        rows.append(f"    <tr><td>{int(r['YEAR'])}</td><td>{party}</td><td>{r['POP_R']:.2f}</td></tr>")

    return f"""<table class="lallpi-ranking">
  <thead>
    <tr><th>Year</th><th>Governing party</th><th>Populist rhetoric (POP_R)</th></tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
</table>"""


def build_countries_directory_html(df: pd.DataFrame) -> str:
    """Alphabetical directory of every country with a generated page,
    each with flag, name (linked), and latest-year POP for context.
    Uses COUNTRY_SLUGS as the country list (not the raw data), so this
    always matches exactly what pages actually exist -- no risk of
    linking to a country page that wasn't generated.
    """
    rows = []
    for iso3, slug in sorted(COUNTRY_SLUGS.items(), key=lambda kv: kv[1]):
        summary = country_summary(df, iso3)
        if summary is None:
            continue  # shouldn't happen given COUNTRY_SLUGS's definition, but stay safe
        rows.append(f"""    <tr>
      <td><div class="country"><img class="flag" src="https://flagcdn.com/w40/{summary['iso2'].lower()}.png" alt="{summary['country']} flag"><a href="/pages/countries/{slug}.html">{summary['country']}</a></div></td>
      <td>{summary['region']}</td>
      <td>{summary['pop']:.1f} ({summary['year']})</td>
    </tr>""")

    return f"""<table class="lallpi-ranking">
  <thead>
    <tr>
      <th>Country</th>
      <th>Region</th>
      <th>Latest POP</th>
    </tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
</table>"""

# ---------------------------------------------------------------------------
# Codebook
# ---------------------------------------------------------------------------
#
# Static metadata (description/source/construction/notes) can't be derived
# from the data itself -- it's hand-curated below. Type/range/missing-count
# ARE computed live from the actual published CSV each time this renders,
# so this can't silently drift out of sync with the real data the way a
# fully hand-typed codebook could.

CODEBOOK_SECTIONS = [
    ("Identifier Variables", [
        ("ISO2", "2-letter country code", "ISO 3166-1 alpha-2", None,
         "Used for flag icon lookups (flagcdn.com) throughout the site. Missing for Cuba specifically -- never added to countries.csv, likely because Cuba never has a complete POP value (see COUNTRY_SLUGS notes) and therefore never needed a flag lookup on a country page."),
        ("ISO3", "3-letter country code", "ISO 3166-1 alpha-3", None,
         "Primary country key used throughout the pipeline and site (e.g. COUNTRY_SLUGS in _site_helpers.py)."),
        ("COUNTRY", "Country name", "countries.csv", None, None),
        ("REGION", "Sub-region classification", "countries.csv", None,
         "E.g. South America, Central America, Caribbean. Used for the regional-comparison charts on country pages."),
        ("YEAR", "Calendar year", "N/A", None, "2000-2020."),
        ("LDC", "Least Developed Country flag (UN classification)", "UN-OHRLLS", None, "0 = no, 1 = yes."),
        ("LLDC", "Landlocked Developing Country flag (UN classification)", "UN-OHRLLS", None, "0 = no, 1 = yes."),
        ("SIDS", "Small Island Developing State flag (UN classification)", "UN-OHRLLS", None, "0 = no, 1 = yes."),
    ]),
    ("Overall Index", [
        ("POP", "Overall populism index",
         "Constructed", "POP = (PEP + PIP) / 2",
         "Range 0-100. Combines economic and institutional populism, each already weighted by rhetoric via PEP/PIP. See Documentation for the full derivation and the scenarios this construction is designed to distinguish."),
        ("POP_RANK", "Country's POP rank among countries with a POP value that year", "Constructed", "Computed per-year, 1 = highest POP", None),
        ("POP_PERCENTILE", "Country's POP percentile rank that year", "Constructed", None, "Range 0-1."),
    ]),
    ("Institutional Populism", [
        ("PIP", "Institutional Populism, rhetoric-weighted", "Constructed", "PIP = POP_R \u00d7 IP",
         "Range 0-100 (since POP_R is 0-1 and IP is 0-100)."),
        ("PIP_RANK", "Country's PIP rank among countries with a PIP value that year", "Constructed", None, None),
        ("PIP_PERCENTILE", "Country's PIP percentile rank that year", "Constructed", None, "Range 0-1."),
        ("IP", "Institutional Populism sub-index", "Constructed", "IP = average(IP_1, IP_2, IP_3, IP_4, IP_5, IP_6)",
         "Range 0-100. Note: IP_3 (legislative constraints) and IP_4 (corruption, duplicating IP_2) reflect a known construction quirk carried over from the original pipeline -- documented transparently on the Documentation page rather than silently corrected, since it affects published historical values."),
        ("IP_1", "Rule of law", "V-Dem", None, "Range 0-100."),
        ("IP_2", "Corruption", "V-Dem", None, "Range 0-100."),
        ("IP_3", "Legislative constraints", "V-Dem", None, "Range 0-100."),
        ("IP_4", "Corruption (duplicate of IP_2 -- see IP notes above)", "V-Dem", None, "Range 0-100."),
        ("IP_5", "Neopatrimonialism", "V-Dem", None, "Range 0-100."),
        ("IP_6", "Property rights", "Heritage IEF", None, "Range 0-100."),
    ]),
    ("Economic Populism", [
        ("PEP", "Economic Populism, rhetoric-weighted", "Constructed", "PEP = POP_R \u00d7 EP",
         "Range 0-100 (since POP_R is 0-1 and EP is 0-100)."),
        ("PEP_RANK", "Country's PEP rank among countries with a PEP value that year", "Constructed", None, None),
        ("PEP_PERCENTILE", "Country's PEP percentile rank that year", "Constructed", None, "Range 0-1."),
        ("EP", "Economic Populism sub-index", "Constructed", "EP = average(EP_1, EP_2, EP_3, EP_4)",
         "Range 0-100. Each EP_n component is itself an average of Heritage IEF and Fraser EFW variables -- see Documentation for the full variable-source table."),
        ("EP_1", "Business and labor market regulation", "Heritage IEF + Fraser EFW", None, "Range 0-100."),
        ("EP_2", "Government interference", "Heritage IEF + Fraser EFW", None, "Range 0-100."),
        ("EP_3", "Monetary and financial freedom", "Heritage IEF + Fraser EFW", None, "Range 0-100."),
        ("EP_4", "Freedom to trade (internationally)", "Heritage IEF + Fraser EFW", None, "Range 0-100."),
    ]),
    ("Rhetoric and Governing Party", [
        ("POP_R", "Populist rhetoric score of the governing party that year", "V-Party", None,
         "Range 0-1. Harmonic mean of \"anti-elitism\" and \"people-centrism\" -- see Documentation for the full definition."),
        ("POP_R_RANK", "Country's POP_R rank among countries with a POP_R value that year", "Constructed", None, None),
        ("POP_R_PERCENTILE", "Country's POP_R percentile rank that year", "Constructed", None, "Range 0-1."),
        ("PARTY_CODE", "V-Party's identifier code for the governing party", "V-Party", None, None),
        ("PARTY_NAME", "Name of the governing party that year", "V-Party", None,
         "Party attribution for change-of-government years follows the documented override file -- see the Data page."),
    ]),
]


def build_codebook_html(df: pd.DataFrame) -> str:
    """Codebook: every published column, with live-computed type/range/
    missing-count from the actual data alongside hand-curated
    description/source/construction/notes (see CODEBOOK_SECTIONS).

    Rendered as compact per-variable bullet blocks rather than a wide
    table -- a table handles short categorical values fine, but forces
    awkward text-wrapping on variable-length free text (Notes
    especially), which balloons row height and makes the page feel
    unwieldy rather than scannable.
    """
    sections_html = []

    for section_title, variables in CODEBOOK_SECTIONS:
        entries = []
        for name, description, source, construction, notes in variables:
            col = df[name]
            if pd.api.types.is_numeric_dtype(col):
                non_null = col.dropna()
                if len(non_null) > 0:
                    # Format without decimals if every non-null value is a
                    # whole number (covers YEAR, LDC/LLDC/SIDS, and the
                    # *_RANK columns, all of which are conceptually
                    # integers but stored as float64 since NaN forces
                    # pandas to use a float dtype).
                    if (non_null == non_null.round()).all():
                        range_str = f"{non_null.min():.0f} to {non_null.max():.0f}"
                    else:
                        range_str = f"{non_null.min():.2f} to {non_null.max():.2f}"
                else:
                    range_str = "--"
            else:
                n_unique = col.nunique()
                range_str = f"{n_unique} distinct values"

            n_missing = int(col.isna().sum())
            pct_missing = 100 * n_missing / len(df)

            # Skip empty fields rather than showing a bare "--" bullet --
            # not every variable has a construction formula or notes.
            bullets = [f"<li><strong>{description}</strong> &middot; {source}</li>"]
            if construction:
                bullets.append(f"<li>Construction: <code>{construction}</code></li>")
            bullets.append(f"<li>Range/values: {range_str} &middot; Missing: {n_missing} ({pct_missing:.1f}%)</li>")
            if notes:
                bullets.append(f"<li>{notes}</li>")

            entries.append(f"""<div class="codebook-entry">
  <h4><code>{name}</code></h4>
  <ul>
    {chr(10).join(bullets)}
  </ul>
</div>""")

        sections_html.append(f"""
<h3>{section_title}</h3>
{chr(10).join(entries)}""")

    return "\n".join(sections_html)