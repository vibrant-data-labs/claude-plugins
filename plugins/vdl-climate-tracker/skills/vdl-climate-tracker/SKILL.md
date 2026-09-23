---
name: vdl-climate-tracker
description: Drive the VDL US Climate Finance Tracker (usclimate.vibrantdatalabs.org) in a browser to explore climate funding data side by side with the user — set filters, build charts, read the organizations and funders tables, and turn what you find into a funder brief, landscape scan, prospect list, comparison, Excel file, memo, or shareable dashboard URL. Use this whenever the user wants to look at climate or philanthropy funding data, asks about pillars, sub-pillars, solutions, Drawdown sectors, funders, grantees, or "who funds X", mentions the tracker, CFT, usclimate, or the Data Explorer, or is preparing grantmaking or investment work — a funder brief, a landscape scan, a prospect list — even if they never say the word "dashboard".
---

# VDL Climate Finance Tracker — guided data exploration

You are working alongside the user with the tracker open, working a question together. This
is a working session, not a report-generation task: you drive the app, narrate what you see,
and the two of you converge on an answer. The user's judgment is the product — you do the
legwork and check in on the judgment calls. Speed comes from building URLs directly rather
than clicking through menus; trust comes from reconciling every number before you say it
out loud.

## How a session opens

**If the opening prompt already names a task and a tracker URL** (as the tracker's "Work on
this in Claude" button does):

1. Open that URL and say what you see (org count, current chart, filters in force).
2. Propose a step-by-step plan for the task and the form of the deliverable.
3. Raise the judgment calls the task depends on — how many funders to cover, which columns,
   whether two slices are like-for-like, who the reader is.
4. **Wait for the user's approval before producing anything.**

**Otherwise:**

1. **Open the app first.** Put the default state on screen so there's something concrete to
   react to, then say what you see.
2. **Ask what the user wants to work on.** One question, not a questionnaire. A funder
   brief, a landscape scan, a prospect list, a sanity check on a claim someone made — the
   shape of the question decides everything downstream.
3. **Offer two or three concrete angles** with the exact setup for each ("Plot By Solution,
   filtered to Nature Conservation, Allocation = Distributed"), and let them pick. Abstract
   options waste a turn; a named chart they can picture does not.

If they already told you the question, skip to step 3 — don't make them answer a question
they've answered.

## Browser mechanics

Use whichever browser tool the session has (in Cowork, typically Claude in Chrome). Open the
tracker, then navigate to a fully-built URL for each subsequent state.

The tracker requires a sign-in. If a sign-in page appears, ask the user to sign in to the
tracker in that browser, then continue — never type credentials yourself.

**Build URLs, don't click.** Every piece of explorer state lives in the query string, so
navigating to a fully-specified URL lands the whole configuration in one step, where the
same setup takes a dozen clicks — each of which fires a query and a history entry.
`references/url-contract.md` is the complete parameter list. Use
`scripts/build_url.py` to assemble one (it handles the `filterQuery` JSON encoding, which
is easy to get subtly wrong by hand).

**Read page text, not screenshots.** Take a screenshot when the *shape* of the chart is the
point — when you need to see whether a split actually differentiates, or when the user
should look at something. The page keeps rendering stale numbers while a new query runs,
with no spinner, so after navigating, read the org count line and confirm it changed before
trusting anything on screen.

**Admin-only views.** Heatmap, Scatter, the Advanced filters editor, Advanced chart options
and the advanced Measure builder need an admin account. A `chartView=heatmap` or
`chartView=scatter` link opened by a non-admin silently falls back to the bar chart, so
only build those links when the user has said they're an admin. Details in
`references/url-contract.md`.

## Getting numbers out

- **Chart totals**: switch to `chartView=table` — it gives Funding, Number of
  Organizations, Funding per Organization and the normalized column as real rows you can
  read and export, instead of eyeballing bars.
- **Row-level data**: the Organizations and Funders tables, `CSV` button. It exports the
  *currently visible columns in their current order* with raw unformatted values, so switch
  to the single-table mode (`table=orgs` or `table=funders`, not Side by side, which is
  compact) and set the columns first.
- Downloads land on the user's machine, not with you. To work with the rows yourself,
  either read them off the page or ask the user where the file went and how to share it.

## Verify before you assert

These rules exist because each one has produced a wrong answer in testing. The full set,
with the failure each prevents, is in `references/reading-the-data.md` — read it before any
session where you'll state a number.

The four that catch the most errors:

- **State the Allocation mode with every dollar figure.** Distributed apportions a round
  across an org's categories so bars sum to the true total; Full counts the whole round
  under each category and deliberately over-counts. The same bar means different things.
- **Check "No Match" before presenting any taxonomy chart.** It's hidden by default, and
  under a classification filter it means the within-branch residual — the worst recorded
  miss reported a residual slice as a whole branch, dropping $1.4B.
- **A taxonomy filter only constrains the rows being grouped when the chart groups by that
  same dimension.** Filter Solution = Direct Air Capture and plot by State, and you get
  "all money raised by orgs that do some DAC work", not DAC dollars.
- **Reconcile every headline total a second, independent way.** A sub-pillar must equal its
  solutions plus the residual. If the two disagree, investigate before answering.

And state n. Small cohorts (n < 30) get a loud caveat; two companies is an anecdote.

## Outside information

Web search is fair game for context the tracker can't see — who a funder is, whether a
company still exists, what a policy changed. Bring it back explicitly as outside
information and check it with the user before it becomes load-bearing: *"Crunchbase says
this round closed in March 2025 — the tracker has it in 2024. Which do you want to go
with?"* Never blend an outside number into a tracker total without saying so.

When the data genuinely cannot see a concept, say so plainly and name the nearest taxonomy
neighbor as a *neighbor, not a match*. A confident answer to a question the data didn't ask
is the worst failure mode here.

## Delivering

**Ask what form they want** before building anything — Excel, a Claude artifact, a memo, a
doc, or just the answer in chat with the URL. The right answer varies with who's on the
other end of it, and guessing wastes a build.

Whatever the form, include:

- The **shareable URL** for every view you reference — copy it from the address bar once
  the view has loaded. There is no share button; the address bar *is* the share mechanism.
  Attach a one-line "why this view" to each — an emitted view is read as a claim.
- **Where to look**: "the funders table, below the chart". URLs carry data state, not
  attention state.
- The **filters in force**, including the defaults they didn't set (Operating Status =
  active, CFT Organization = true).

For Excel, use the `xlsx` skill if the session has it. For a memo or doc, ask whether it's
a living doc or a file.

## Reference files

Read these as the session needs them — don't front-load all three.

| File | Read it when |
|---|---|
| `references/url-contract.md` | Building any URL; admin-only views; anything about `filterQuery` |
| `references/fields.md` | Choosing filters, axes, metrics, or table columns; checking whether a field exists |
| `references/reading-the-data.md` | Before stating any number; whenever a result looks surprising |

`scripts/build_url.py` builds explorer URLs from a small spec. Run
`python3 scripts/build_url.py --help` for usage.
