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
        rows_html.append(f"""    <tr>
      <td><div class="country"><img class="flag" src="{flag_url}" alt="{r['COUNTRY']} flag">{r['COUNTRY']}</div></td>
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