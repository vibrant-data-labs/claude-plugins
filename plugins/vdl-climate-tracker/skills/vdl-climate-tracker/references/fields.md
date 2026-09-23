# Field registry — usclimate (Climate Finance Tracker)

What exists, what it means, and what it's called in the URL. Field ids here are what goes in
`filter.<id>`, `xAttribute`, `colorBy`, and a `filterQuery` leaf's `"field"`.

Universe: ~18,500 organizations, ~$993B tracked funding, 2010–2026, ~20,900 funders. **On a
default load you see ~13,300** — the two pre-selected baseline filters
(`operating_status=active`, `in_final_network=true`) are already cutting the universe.
Read the org count line under the title to know which number you're standing on.
One Earth: 5 pillars → 17 sub-pillars → ~119 solutions. Drawdown: 13 sectors → 35 clusters →
166 solutions. **Coverage is US-centric** — non-US totals understate reality.

## Filters

| Field id | UI label | Meaning | Kind |
|---|---|---|---|
| `keyword` | Keyword | Free text against the org description (ILIKE). Min 3 chars, max 25 terms. | org, free-text |
| `vdl_stage` | Round Stage | Stage of each funding round — seed, early/late-stage venture, grant, debt, IPO, PE… | **event** |
| `investment_type` | Round Type | Instrument — Series A–H, angel, convertible note, grant, PE, crowdfunding… | **event** |
| `funding_year` | Funding Year | Year of the round, 2010–2026. Only shown in the sidebar when Group by = Funding Year. | **event** |
| `pillars` | Pillar | One Earth L0: Energy Transition, Nature Conservation, Regenerative Agriculture, Geo-Engineering, Cross-Cutting | taxonomy `oe` L0 |
| `sub_pillars` | Sub-Pillar | One Earth L1 (17) | taxonomy `oe` L1 |
| `solutions` | Solution | One Earth L2 (~119) | taxonomy `oe` L2 |
| `drawdown_sectors` | Drawdown Sector | Drawdown L0 (13): Electricity; Buildings; Transportation; Industry, Materials & Waste; Food, Agriculture, Land & Ocean; Industrial Carbon Removal; Geoengineering; … | taxonomy `drawdown` L0 |
| `drawdown_clusters` | Drawdown Cluster | Drawdown L1 (35) | taxonomy `drawdown` L1 |
| `drawdown_solutions` | Drawdown Solution | Drawdown L2 (166) | taxonomy `drawdown` L2 |
| `org_type` | Organization Type | `Non Profit` (~11,027) / `For Profit` (~7,453). **Space, no hyphen.** | org |
| `philanthropy_vs_venture` | Philanthropic vs Venture | Philanthropy / Venture / Post-Venture / Non-Equity. Classifies the **organization, not the money**. | org |
| `predictions_adapt` | Adaptation / Mitigation | adaptation / mitigation / **both**. Excluding `both` drops a usually-large group. | org |
| `underserved_community_mention` | Underserved Community Mention | The org's own description *mentions* it. Not a verified attribute. | org |
| `equity_justice_mention` | Any Equity Justice Mention | Same — a text mention. | org |
| `gov_funder` | Received Government Funding | Any recorded funding from a government source. | org |
| `country` | Country | HQ country. | org |
| `state` | State | US HQ state. Orgs with no state drop out when set and never appear on the map. | org |
| `county` | County | `"San Francisco, California"` form. Many orgs have none. | org |
| `operating_status` | Operating Status | **Defaults to `active`.** | org |
| `in_final_network` | CFT Organization | In the published CFT network. **Defaults to `true`** — the tracked universe is broader. | org |
| `funder_names` | Funders | ~20,900 funder names. Filterable, **not** plottable. | org (array) |

Taxonomy filters are surfaced as the **One Earth** and **Drawdown** accordions in the
sidebar, not as flat dropdowns — but they write the same `filter.<id>` keys. Each accordion
header carries `Include <Framework>` / `Exclude <Framework>` buttons, and a pillar's header
checkbox writes the pillar-level key independently of the sub-pillar boxes under it.

Option lists cascade: `/api/filter-options` returns only values with ≥1 matching org under
the other active filters, so options disappear as you filter.

## Axes and measures

**Group by (`xAttribute`)** — 18 options: `funding_year`, `pillars`, `sub_pillars`,
`solutions`, `drawdown_sectors`, `drawdown_clusters`, `drawdown_solutions`, `org_type`,
`philanthropy_vs_venture`, `predictions_adapt`, `underserved_community_mention`,
`equity_justice_mention`, `gov_funder`, `country`, `state`, `county`, `operating_status`,
`in_final_network`. Default `pillars`. `county` is capped at top 30.

**Split by (`colorBy`)** — the same list minus `funding_year`, plus `none`. Default
`pillars` (so out of the box Group by == Split by).

**Not available as an axis or color**: `vdl_stage`, `investment_type`, `funder_names`,
`keyword`, `funding_stage`. Instrument and stage stories need two filtered charts, not a
color split. Never emit an `xAttribute` that isn't on the list above.

**Measure (`yMetric`)**:

| id | UI label | Unit | Distributed | Full |
|---|---|---|---|---|
| `distributed_funding` | Funding | USD | `SUM(fraction × amount)` | `SUM(amount)` over distinct (category, org, event) |
| `org_count` | Number of Organizations | count — **can be fractional** | `SUM(fraction)` | `COUNT(DISTINCT org_uid)` |

At most **two** classification dimensions per chart (x + colorBy). Since CFT has exactly two
(`oe`, `drawdown`), any One Earth × Drawdown pairing is legal.

## Organizations table

`uid` (hidden) · Organization (`name`) · Website · Data Source · Pillar · Sub-Pillar ·
Solution · Drawdown Sector · Drawdown Cluster · Drawdown Solution · Funders · **Total
Funding** · Last Funded · Organization Type · State · Country · CFT Organization.

Compact (side-by-side) default: Organization, Pillar, Total Funding — plus the chart's
plotted dimensions, which are pinned on automatically.

⚠️ **Total Funding is the org's lifetime total and is never narrowed by any filter.** Filter
to Seed rounds and the chart shows seed money while the table column still shows all-time.

## Funders table

Funder · Type · **# Matching** (portfolio orgs passing the current filters) · **# Portfolio
Orgs** (total, unfiltered — the default sort) · **Known Funding** (only where the funder is
attributed to the event; 990-derived links contribute nothing) · Last Active · Pillars ·
Solutions.

Compact default: Funder, # Matching, # Portfolio Orgs.

## Values worth knowing by heart

- One Earth pillars: **Energy Transition** · **Nature Conservation** · **Regenerative
  Agriculture** · **Geo-Engineering** · **Cross-Cutting**
- `org_type`: `Non Profit` · `For Profit` (space, no hyphen — a hyphen silently matches
  nothing)
- `philanthropy_vs_venture`: Philanthropy · Venture · Post-Venture · Non-Equity
- `predictions_adapt`: adaptation · mitigation · both
- Pinned pillar colors: Energy Transition `#008BA0`, Nature Conservation `#A7B062`,
  Regenerative Agriculture `#DC6A2C`, Geo-Engineering `#003B56`, Cross-Cutting `#5E939E`

When you need the exact vocabulary for a field, open its dropdown in the sidebar and read
the options rather than guessing — the lists cascade and change with the active filters.
