"""
generate_country_pages.py

Generates one .qmd page per country in pages/countries/, from a shared
template. Country pages are NOT hand-written -- if you need to change
the layout or add a section, edit TEMPLATE below and re-run this
script, rather than editing individual generated .qmd files (which
would just get overwritten next time this runs).

Each generated page reads data/2025/output/index_2025.csv live at
build time (via _site_helpers, same pattern as every other page on
this site) -- it does not bake in numbers at generation time. Re-running
this script only needs to happen when adding/removing countries from
COUNTRIES_TO_GENERATE below, not when the underlying data changes.

Usage
-----
    python3 generate_country_pages.py
"""

from pathlib import Path
import sys

sys.path.insert(0, ".")
import pandas as pd
import _site_helpers as sh

# Country list lives in _site_helpers.COUNTRY_SLUGS now -- single
# source of truth shared with build_ranking_table_html(), so the
# ranking table's links and this generator can't drift out of sync.
# See that dict's docstring for why CUB, GUY, and SUR aren't in it.
COUNTRIES_TO_GENERATE = sh.COUNTRY_SLUGS

OUTPUT_DIR = Path("pages/countries")

TEMPLATE = '''---
title: "{country_name}"
---

<a href="/pages/data.qmd">&larr; All countries</a>

```{{python}}
#| echo: false
#| output: asis

import sys
sys.path.insert(0, ".")
import pandas as pd
from IPython.display import HTML, display
import _site_helpers as sh

df = pd.read_csv("data/2025/output/index_2025.csv")
s = sh.country_summary(df, "{iso3}")

display(HTML(f"""
<div style="display:flex; align-items:center; gap:16px; margin: 1.5em 0;">
  <img src="https://flagcdn.com/w80/{{s['iso2'].lower()}}.png" alt="{{s['country']}} flag" style="border-radius:4px;">
  <div>
    <h2 style="margin:0;">{{s['country']}}</h2>
    <p style="margin:0; color:var(--utep-silver, #666);">{{s['region']}} &middot; data available {{s['first_year']}}-{{s['last_year']}} ({{s['n_years']}} years)</p>
  </div>
</div>
<div class="lallpi-stat-row">
  <div><span class="stat-value">{{s['pop']:.1f}}</span><span class="stat-label">POP ({{s['year']}})</span></div>
  <div><span class="stat-value">#{{s['rank']}}</span><span class="stat-label">of {{s['n_countries']}} countries, {{s['year']}}</span></div>
  <div><span class="stat-value">{{s['percentile']*100:.0f}}<sup>th</sup></span><span class="stat-label">percentile, {{s['year']}}</span></div>
</div>
"""))
```

## Score over time

```{{python}}
#| echo: false
#| label: fig-{slug}-trend
#| fig-cap: "{country_name}: POP, PEP, and PIP by year"

import matplotlib.pyplot as plt

fig = sh.build_country_trend_chart(df, "{iso3}")
plt.show()
```

## What's driving the score

Latest-year breakdown of the six Institutional Populism components and
four Economic Populism components -- see
[Documentation](/pages/documentation.qmd) for what each one measures.

```{{python}}
#| echo: false
#| label: fig-{slug}-breakdown
#| fig-cap: "{country_name}: sub-index components, latest year"

fig = sh.build_subindex_breakdown_chart(df, "{iso3}")
plt.show()
```

## {country_name} vs. the regional average

```{{python}}
#| echo: false
#| label: fig-{slug}-regional
#| fig-cap: "{country_name} vs. regional average POP"

fig = sh.build_regional_comparison_chart(df, "{iso3}")
plt.show()
```

## Governing party by year

The populist rhetoric score (`POP_R`) is specific to whichever party
governed that year -- see [Documentation](/pages/documentation.qmd) for
how this is determined.

```{{python}}
#| echo: false
#| output: asis

display(HTML(sh.build_party_history_table_html(df, "{iso3}")))
```
'''


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv("data/2025/output/index_2025.csv")

    for iso3, slug in COUNTRIES_TO_GENERATE.items():
        summary = sh.country_summary(df, iso3)
        if summary is None:
            print(f"WARNING: no data for {iso3}, skipping")
            continue

        content = TEMPLATE.format(
            country_name=summary["country"],
            iso3=iso3,
            slug=slug,
        )
        out_path = OUTPUT_DIR / f"{slug}.qmd"
        out_path.write_text(content)
        print(f"Wrote {out_path} ({summary['country']})")


if __name__ == "__main__":
    main()