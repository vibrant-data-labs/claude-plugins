# Tenants

One codebase, several dashboards, routed by hostname. Everything in `fields.md` describes
**usclimate**; the others differ in taxonomy, field list, and which features are enabled.
When working a non-default tenant, open its sidebar and chart menus and read the actual
options rather than assuming the CFT list.

| Tenant | URL | What it is | Auth |
|---|---|---|---|
| `vibrant-data-labs` | usclimate.vibrantdatalabs.org | **US Climate Finance Tracker** — the default. One Earth + Drawdown taxonomies, ~18.5k orgs, ~$993B. | Clerk |
| `demo` | demo.vibrantdatalabs.org | Trimmed CFT for prospects — same data, fewer selectors (9 sidebar filters, 10 axes, 7 color-by). Solutions filterable but not plottable; no country (US-only); baseline filters moved server-side so they're not visible or changeable. No advanced filters, no schema picker, no copilot suggestions. | Clerk (own key) |
| `learning` | lft.vibrantdatalabs.org | **Learning Finance Tracker** — education funding. Taxonomies: education (Pillar→Sub-Pillar→Solution), Learning Focus Areas, Learning Journey Stages. ~20.6k nonprofit / 1.5k for-profit; no org-level funding stage. | Clerk |
| `drawdown` | drawdown.vibrantdatalabs.org | **Drawdown Tracker** — one Drawdown taxonomy plus mode of operation and solution properties (category, speed of action, climate pollutants) carried on the edge. ~4.7k orgs. | public |
| `nature-loc` | natureloc.climatefinancetracker.com | **Nature Levers of Change** — One Earth LoC frame (Pillar→Solution→Sub-Term), nature-only funding. ~4.7k orgs. | public |
| `one-earth` | oneearth.climatefinancetracker.com | **One Earth Solutions** — the original gen-1 tracker, US-only baseline, curated views ("Landscape Overview", "Energy Transition Overview"). | public |
| `healthinnovations` | healthinnovations.vibrantdatalabs.org | Health innovations (ARPA-H): Treatment vs Prevention, Innovation Category/Subcategory, Health Outcomes and Drivers. Gen-1 schema. | public |
| `admin` | admin.vibrantdatalabs.org | Admin app, not a data tracker. | Clerk |

## Feature availability

| Feature | Where |
|---|---|
| Advanced filters (`filterQuery`) | **usclimate and lft only**, and **admin role only** |
| Advanced chart options (`contributionScope`) | same |
| Heatmap and Scatter views | usclimate, admin role only |
| Map view | usclimate (country / state / county, default state) |
| Schema picker | usclimate |
| Saved views and stories | usclimate, lft, one-earth |

A `chartView=heatmap` or `chartView=scatter` link handed to a non-admin silently renders the
bar chart instead. If a feature you expect isn't on screen, check the role gate before
assuming the app is broken.

## Switching tenants mid-session

The URL parameters are the same across tenants, but **field ids are not** — `pillars` on
usclimate is not the same vocabulary as `pillars` on lft, and Drawdown-only fields don't
exist on the education tracker. Re-read the sidebar after switching, and never carry a
`filterQuery` across tenants: an unknown field is a 400 (`This field is not available in
this tenant query`).
