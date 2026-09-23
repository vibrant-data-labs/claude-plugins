# Reading the data without getting it wrong

Every rule here exists because its absence produced a wrong or misleading answer in
testing.

## The mechanics that change what a number means

### `fraction` — the fair-share split

Every org × dimension pair has classification rows whose `fraction` sums to exactly 1.0. An
org mapped to three One Earth solutions carries ≈0.333 on each. Orgs with no classification
in a dimension get an explicit `No Match` row at 1.0. Because fractions sum to 1, summing
fraction-weighted values across all categories reproduces the true ecosystem total exactly.

> **Wrong conclusion:** "This solution has 340 organizations, so 340 companies work on it."
> In Distributed mode the org count is `SUM(fraction)` — a fair-share headcount that can be
> fractional. The real number of orgs touching that solution is higher.

### `distributed_amount` and the Allocation toggle

`distributed_amount = fraction × amount`: one round's dollars apportioned across the org's
categories. Nobody granted that amount. A $30M round for an org mapped to three pillars
contributes $10M to each.

- **Distributed** (default): bars sum to the true total. Safe for "how is the ecosystem
  split".
- **Full**: the whole $30M appears under each of the three pillars. Bars intentionally
  over-count. Safe for "how much money touched this category at all".

> **Wrong conclusion:** quoting the sum across bars in Full mode as ecosystem funding — it
> can run far above the ~$993B tracked. Equally wrong: quoting a Distributed bar as "what
> these companies raised for this work", which over-precises a mechanical split.

**State the Allocation mode with every dollar figure.**

### Where a filter gets applied (the four buckets)

The query layer sorts every active filter into one of four buckets, and the bucket decides
the grain:

- **sameDimension** — a taxonomy filter's includes, when the chart is *already grouping by
  that dimension*. A direct `WHERE` on the grouped rows. Exact, no fan-out.
- **event** — a funding-event column (`vdl_stage`, `investment_type`, `funding_year`).
  Removes **rounds**, not organizations.
- **edgeScope** — a taxonomy filter when the chart is *not* grouping by its dimension, plus
  every taxonomy exclude. One `EXISTS` per dimension with all that dimension's includes
  ANDed inside, so they must hold for the *same* assignment row.
- **orgScope** — everything else: scalar org attributes, the funder array, the keyword.
  `EXISTS`: "is this org in scope?" Once it qualifies, **all** of its rows count.

**The rule that falls out:** a taxonomy filter only constrains the exact rows being grouped
when the chart groups by that same dimension. Otherwise it narrows the *population of
organizations*, after which every row of a surviving org is counted.

> **Wrong conclusion:** filter Solution = Direct Air Capture, plot by State, report "Texas
> has $2.1B of DAC funding". What it says is "$2.1B went to Texas orgs that do at least some
> DAC work" — and a diversified energy company in there can be most of it. To get DAC
> dollars, group by the dimension you filtered.

The same trap spans the two taxonomies: filtering a Drawdown Sector while plotting One Earth
Pillars is an org-level narrowing, not a dollar-level one.

### Event filters filter rounds, not organizations

Round Stage / Round Type / Funding Year keep an org visible if *any* round matches, and only
matching rounds count toward chart totals. But the org table's **Total Funding column is
read straight off the org row and is never narrowed by any filter**.

> **Wrong conclusion:** "I filtered to Seed and the table shows $410M, so it raised $410M in
> seed." That's lifetime; only its seed rounds are in the chart.

### "No Match" is context-dependent

The sentinel for an unclassified org. Hidden by default and dropped *before* normalization,
so percentages are over classified categories only.

- Unfiltered, it means globally unclassified money.
- Under a classification filter, it means the **within-branch residual** — orgs classified at
  a shallower level with no child assignment.

> **The worst recorded miss:** reading a sub-pillar's solution bars as the whole sub-pillar
> and dropping the ~$1.4B no-solution residual.

Check its size (toggle `showNoMatch=true`) before presenting any classification chart.
Reconcile: a sub-pillar total must equal its solutions plus the residual.

## Funders

- **Two linkage layers — route by question.** Event-level edges capture venture/equity
  participation; 990-derived portfolio arrays capture philanthropy. Grantee and nonprofit
  questions go to the portfolio layer; startup and investor questions to the event layer.
  The wrong layer recommends a venture investor to a nonprofit grantee.
- **DAF pass-throughs are vehicles, not doors.** Fidelity Charitable, DAFgiving360, Vanguard
  Charitable and similar top any breadth ranking. Annotate or exclude them, and read their
  presence as "individual donors give here via DAFs".
- **Dollar rankings credit each co-investor with the full round** (participation credit).
  Prefer breadth rankings (# Portfolio Orgs / # Matching); if showing dollars, say what they
  mean.
- A funder can appear **twice** — identity is never merged on name alone, so the same
  organization can carry both an `ein:` uid and a `name:` uid with different counts.
- `Known Funding` is null or low whenever a funder's links are org-level (990) rather than
  event-level. Coverage ≠ absence.

## Coverage and caveats

- **Current year is always partial.** A drop at the right edge is reporting lag, not decline.
- **990 philanthropy lags ~2 filing years** — "recently active" means the last filing cycle.
- **Default baseline**: `operating_status=active`, `in_final_network=true`. These are
  ordinary sidebar rows here, easy to change by accident. State which baseline a number uses.
- **Text-mention fields** (`underserved_community_mention`, `equity_justice_mention`) record
  what the org's own description says. Silence means the description doesn't say it, not
  that the work isn't happening.
- **Nulls**: orgs with no state drop out when the State filter is set. Deeper taxonomy levels
  collapse to `No Match`, folding "matched the parent, no child assigned" together with
  "unclassified".
- **County axis** is truncated to top 30; Table view and the county map show all.

## Analytic discipline

- **Disambiguate polysemous terms before answering.** "Gap" has at least four senses —
  temporal, distributional (scale gap / missing middle), relative to peers, absolute (not
  funded at all). "Biggest" splits into breadth vs dollars. Ask, or answer one sense and say
  which.
- **No gap or anomaly claim without a comparison set.** A pattern that confirms a hypothesis
  in isolation may be the population norm. Benchmark first.
- **State n.** Cohorts under 30 get a loud caveat; two companies is a story, not a
  distribution.
- **Reconcile every headline total a second, independent way** before stating it. If the two
  disagree, investigate before answering. Verify taxonomy rollups with the app — never
  assert hierarchy from memory.
- **Spot-check cohort membership**: read the descriptions of the largest / most-funded
  members. An outlier that doesn't belong (a battery-materials company in a cement cohort)
  can dominate the dollars. Do this even when the cohort looks clean, and flag it as a
  taxonomy QA signal.
- **When your interpretation of the question changes, explicitly retract the views and
  claims built on the old one.** Stale charts keep misleading after the words move on.

## Vocabulary and out-of-vocabulary

- Bridge the user's words to data vocabulary explicitly: regions → state lists; themes →
  taxonomy unions. A theme like "ocean" can span several pillars — check the hierarchy and
  disclose the boundary choices.
- **False-friend probe**: scan the taxonomy broadly, then test each candidate individually.
  "Fisheries Processing" is an energy-efficiency solution, not ocean work. Disclose
  exclusions.
- **Out-of-vocabulary protocol**, in order: (1) taxonomy scan; (2) search over org
  descriptions; (3) named-entity check for known players; (4) if still invisible, say the
  data cannot see the concept, name the nearest taxonomy neighbor, and mark it a *neighbor,
  not a match*.

## Presentation

- **Every emitted view is read as a claim.** Attach a one-line "why this view" to each. If
  the chart parameters are incidental because the answer lives in a table, say so.
- **Render check before proposing an encoding**: run the group-by first; if the split is
  ~one color or ~one bar, choose a different view or drop the split. Never ship an encoding
  you haven't seen differentiate.
- **Name the answering surface** — "the funders table, below the chart". URLs carry data
  state, not attention state.
- **Never invent an axis.** No `funding_year` filler (partial current year; round filters
  change what a year means), and no org_type or status split the user didn't ask for — that's
  the same failure with a different filler. Cohort requests ("companies working in X") are
  filters, not comparisons: use `chartView=map` and let the orgs table list the cohort.
  Geographic questions open on the map too.
- Answers that fit no dashboard view (escalator shapes, graduation rates) are legitimate —
  deliver the analysis and say the dashboard has no view for it.
- **Evidence, not advice.** For "should" questions — who to talk to, where to deploy capital
  — give *who has demonstrably done X* plus *what this data cannot tell you* (receptivity,
  fit, open programs, future priorities). Never rank targets by predicted receptivity, and
  never give investment advice.
- **Verify claims about the app's own behavior.** What the search box covers, what a toggle
  does, what a column means — check it in the app (filter descriptions, captions), or hedge
  it as unverified. Inferring product behavior from placeholder text produced a wrong claim
  in testing.

## Known expressibility limits — don't pretend otherwise

- Description-matched cohorts cannot become a URL.
- Filters AND across fields, so cross-level unions (sub-pillar X OR solution Y) need either
  an advanced `filterQuery` or multiple links.
- Round stage and instrument cannot be an axis or a color.
- Focus and attention state is never URL-addressable.
