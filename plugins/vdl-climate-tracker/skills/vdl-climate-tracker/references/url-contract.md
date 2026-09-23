# URL contract and UI vocabulary

Everything in the Data Explorer is URL-addressable, so navigating to a fully-built URL is
the fast, reliable way to set up a view. There is **no share button** — the address bar is
the share mechanism.

Base: `https://usclimate.vibrantdatalabs.org/` (other tenants in `tenants.md`).

## Contents

- [Chart and query parameters](#chart-and-query-parameters)
- [Simple filters](#simple-filters)
- [Advanced filters — `filterQuery`](#advanced-filters--filterquery)
- [Chart contributions — `contributionScope`](#chart-contributions--contributionscope)
- [Selections (`sel.*`)](#selections-sel)
- [What is NOT in the URL](#what-is-not-in-the-url)
- [UI labels for driving the browser](#ui-labels-for-driving-the-browser)
- [Gotchas that bite](#gotchas-that-bite)

## Chart and query parameters

| Param | Meaning | Values |
|---|---|---|
| `xAttribute` | Group by (the "Plot By" axis) | a field id — `pillars`, `solutions`, `drawdown_sectors`, `state`, `funding_year`, … |
| `colorBy` | Split by | a field id, or `none` |
| `yMetric` | measure | `distributed_funding` \| `org_count` |
| `yShow` | how the measure is read | absent = amount; `ofGroup`, `ofSubset`, `ofAll`, `growth` |
| `share` | measure restricted to a subset | `<field>:<value>`, e.g. `org_type:Non Profit` |
| `xMetric` / `xShare` / `xShow` | the same three for the scatter x-axis | as above |
| `pointColor` | scatter Color by | a parent-taxonomy field id |
| `normalizeBy` | grid normalization (plain amounts only) | `total` \| `xAttribute` \| `colorBy` \| `Growth Rate` |
| `fundingMode` | Allocation | `distributed` (default) \| `full` |
| `showNoMatch` | show the "No Match" group | `true` \| `false` (default false) |
| `chartView` | which view | absent = bar chart; `heatmap`, `scatter`, `table`, `map` |
| `barMode` | bar stacking | `stacked` (default) \| `grouped` |
| `barLayout` | bar orientation | `vertical` (default) \| `horizontal` |
| `view` | active saved view slug | slug |
| `schema` | override the serving schema | `config.schema` or a listed schema choice |

**Don't touch the schema picker.** Work with whatever is selected and say which schema a
number came from — the choices are not equivalent datasets, and silently switching one
invalidates a comparison against anything quoted earlier.

Defaults on a bare load: `xAttribute=pillars`, `colorBy=pillars`,
`yMetric=distributed_funding`, Allocation `distributed`, No Match hidden. A bare URL with
saved views present auto-applies view 0 — **pass `xAttribute` explicitly** if you want true
defaults.

`chartView=heatmap` and `chartView=scatter` are admin-gated; a non-admin link silently falls
back to the bar chart.

## Simple filters

`filter.<field id>`, repeatable. Values within one key OR; different keys AND.

```
?xAttribute=solutions&filter.pillars=Energy+Transition&filter.org_type=Non+Profit
```

`filterExclude.<field id>` is honored server-side but nothing in the simple UI writes it.

Two filters are pre-selected on every load and are easy to change by accident:
`filter.operating_status=active` and `filter.in_final_network=true`. Say which baseline a
number uses.

Event-level filters (`vdl_stage`, `investment_type`, `funding_year`) only appear in the
sidebar when `xAttribute=funding_year`, but they **keep filtering while hidden**.

## Advanced filters — `filterQuery`

Admin-only, and enabled on the `vibrant-data-labs` (usclimate) and `learning` tenants only.
Button label **`Advanced filters`** in the sidebar, above the simple filter list.

One param, `filterQuery`, holding **plain JSON** (then ordinary URL encoding — no base64):

```
{"version":1,"where": Expr | null}

Expr = {"all":[Expr, …]}                          // AND
     | {"any":[Expr, …]}                          // OR
     | {"field":"<id>","op":"<op>","values":[…]}  // leaf
```

Operators — this is the **complete** set. There is no `is` / `contains` (exact) / `is empty`
/ `between` / numeric comparison:

| Field kind | wire op | UI label |
|---|---|---|
| scalar, array, classification, event | `has_any` | Includes any |
| " | `has_none` | Excludes all |
| free-text (`keyword`) | `contains_any` | Contains any |
| " | `contains_none` | Contains none |

Negation exists only as a per-condition operator; there is no NOT group.

`field` is the **config field id** (`pillars`, `org_type`, `vdl_stage`), never a database
column. The available fields are a subset of the sidebar filters — never a superset.

### Worked example

"(Pillar is Energy Transition OR Pillar is Nature Conservation) AND Organization Type is not
Non Profit". Because `has_any` already ORs within a leaf, the natural form is:

```json
{"version":1,"where":{"all":[{"field":"pillars","op":"has_any","values":["Energy Transition","Nature Conservation"]},{"field":"org_type","op":"has_none","values":["Non Profit"]}]}}
```

Use the explicit two-leaf `any` form only when the expression identity matters (saved-view
matching, contribution evidence) — the system deliberately does not canonicalize one into
the other.

Clearing everything writes the explicit null query, not an absent param:
`filterQuery={"version":1,"where":null}`.

### Rules that bite

- **`filter.*` and `filterQuery` cannot both be present.** That combination is a hard 400
  (`AMBIGUOUS_FILTER_INPUT`). Applying advanced filters strips every `filter.*` /
  `filterExclude.*` key — and also deletes `view`, detaching the saved view.
- **A query the simple UI can't represent locks the sidebar.** It renders disabled at 40%
  opacity with the notice "Simple filters unavailable"; only Clear all still works.
  Representable = a top-level AND of leaves, at most one positive clause per field.
  So `{"any":[{pillars…},{pillars…}]}` locks it; the merged single-leaf form does not.
- Limits: nesting depth 8 (UI caps "Add group" at 6), 128 nodes, 500 values per leaf, 25
  keywords per leaf, keywords 3–100 chars, 64 KiB total, **8000 chars encoded URL**. Over
  the URL limit you get "This selection is too large for a shared URL" and nothing changes.
- A malformed `filterQuery` is a 400 with a JSON-Pointer `path` — never silently ignored.

## Chart contributions — `contributionScope`

`matching` (default) or `all`. Governs which taxonomy assignments a qualifying organization
contributes to the chart: only the assignments that *explain* the match, or all of its
assignments. Admin dialog **`Advanced chart options`**; the meaning is always visible as the
caption `Chart contributions: …`. It changes bar composition only — never table eligibility,
never Distributed vs Full.

## Selections (`sel.*`)

Written by clicking a bar, legend entry, heatmap cell, scatter point, map region, or table
row. Deliberately not part of a saved view.

`sel.chartX=<field>:<value>`, `sel.chartColor=<field>:<value>`, `sel.org` + `sel.orgLabel`,
`sel.funder` + `sel.funderLabel`.

These use `router.replace`, so **Back does not undo a bar click**. Changing Group by or
Split by drops selections whose field no longer matches.

## What is NOT in the URL

Lost on share or reload: the map's Country/State/County granularity, the tables section's
Side by side / Organizations / Funders toggle, table sort, table search, table page, and
column visibility/order/widths (those live in that browser's `localStorage`).

So a link can carry the data state but not the attention state — **say in prose where to
look**.

## UI labels for driving the browser

When you do have to click rather than navigate, these are the literal strings.

**Sidebar** (collapsed by default — the edge tab is `Show filters` / `Hide filters`):
`Filters` + a count badge · `SCHEMA` picker · `Advanced filters` (or `Edit advanced
filters`) · framework accordions `One Earth` and `Drawdown`, each with **`Include One
Earth`** / **`Exclude One Earth`** buttons in the header · pillar checkboxes named
`<Pillar> Pillar` (e.g. `Energy Transition Pillar`) with `Select all` / `None` /
`Find option…` and `Expand <sub-pillar>` buttons down to solutions · flat filter triggers
read `<Label>: All` or `<Label>: N selected` (e.g. `Organization Type: All`) · keyword input
`Add keyword, press Enter`.

**Chart toolbar** (labels are upper-case on screen): `MEASURE` · `Metric` · `Show as` ·
`ALLOCATION` (Distributed | Full) · `Chart contributions: …` · `Advanced chart options` ·
`GROUPING` · `Group by` · `Split by` · `"NO MATCH"` (Hide | Show) · view switcher
`Chart | Heatmap | Scatter | Table | Map` · `Views ⌄` · `Save view`.

**Advanced filter dialog**: title `Advanced filters` · legend `Find organizations matching` ·
`All of these conditions (AND)` / `Any of these conditions (OR)` · `Add condition` ·
`Add group` · `Remove condition` · `Remove group` · field select aria-label `Filter field` ·
operator select aria-label `Condition operator` · `Clear draft` · `Cancel` · `Apply filters`.

**Tables**: `Side by side | Organizations | Funders` · `Search table…` · `Columns` · `CSV` ·
`Rows` (25 | 50 | 100) · eye icon `View profile`.

**Omnibar**: placeholder `Search pillars, solutions, organizations…`. Choosing a facet *adds*
to that filter key; choosing an organization navigates away to `/organization/<uid>`.

## Gotchas that bite

1. The page shows **stale numbers while a new query runs**, with no spinner. Confirm the org
   count changed before reading anything.
2. Every simple filter click is a history entry and a full refetch — no debounce. Build the
   URL instead.
3. Touching any filter **deletes `view`**, silently dropping you off a saved view.
4. `County` as an axis is capped at **top 30**; the Table view and county map show all ~1,400.
5. Keywords: minimum 3 characters, maximum 25 terms — out-of-bounds terms are silently
   dropped, including from a hand-made URL.
6. `% of all …` readings are unavailable under `Allocation = Full`.
7. CSV exports **visible columns only, raw unformatted values**, and reflects table-level
   search and column filters. Side-by-side mode shows only 3–4 columns.
8. Table row click cross-filters the other table; it does **not** open the profile. The eye
   icon does.
