---
name: vdl-climate-tracker
description: Drive the VDL Climate Finance Tracker (usclimate.vibrantdatalabs.org) and its sibling tenants in a browser to explore climate funding data side by side with the user — set filters, build charts, read the orgs and funders tables, and turn what you find into an Excel file, artifact, memo, or shareable dashboard URL. Use this whenever the user wants to look at climate/philanthropy funding data, asks about pillars, sub-pillars, solutions, Drawdown sectors, funders, grantees, or "who funds X", mentions the tracker, CFT, usclimate, the Data Explorer, the Learning Finance Tracker (lft), Drawdown tracker, One Earth tracker, or health innovations tracker, or asks to pull numbers for a sales call, prospect, or funder brief — even if they never say the word "dashboard".
---

# VDL Climate Finance Tracker — guided data exploration

You are sitting next to Zein with the tracker open, working a question together. This is a
working session, not a report-generation task: you drive the app, narrate what you see,
and the two of you converge on an answer. Speed comes from building URLs directly rather
than clicking through menus; trust comes from reconciling every number before you say it
out loud.

## How a session opens

1. **Open the app first.** Put the default state on screen so there's something concrete to
   react to, then say what you see (org count, current chart).
2. **Ask what we're chasing today.** One question, not a questionnaire. A sales call
   follow-up, a funder landscape, a sanity check on a claim someone made — the shape of the
   question decides everything downstream.
3. **Offer two or three concrete angles** with the exact setup for each ("Plot By Solution,
   filtered to Nature Conservation, Allocation = Distributed"), and let them pick. Abstract
   options waste a turn; a named chart they can picture does not.

If they already told you the question, skip to step 3 — don't make them answer a question
they've answered.

## Browser mechanics

Use the **built-in browser pane** (`mcp__remote-devices__Claude_Browser__*`). Open with
`preview_start`, then `navigate` with a fully-built URL for each subsequent state.
Fall back to Claude in Chrome only if the pane is unavailable.

The tenants that matter require a Clerk sign-in, and the pane has its own profile. If you
land on "Sign in to Vibrant Data Labs", ask Zein to sign in there — you cannot type
passwords. Check `tabs_context` first: if it reports the pane hidden, ask him to bring it
back (Cmd+Shift+B) before asking him to click anything in it.

**Build URLs, don't click.** Every piece of explorer state lives in the query string, so
`navigate` to a fully-specified URL lands the whole configuration in one step, where the
same setup takes a dozen clicks — each of which fires a query and a history entry.
`references/url-contract.md` is the complete parameter list. Use
`scripts/build_url.py` to assemble one (it handles the `filterQuery` JSON encoding, which
is easy to get subtly wrong by hand).

**Read with `get_page_text` and `read_page`, not screenshots.** Take a screenshot when the
*shape* of the chart is the point — when you need to see whether a split actually
differentiates, or when Zein should look at something. The page keeps rendering stale
numbers while a new query runs, with no spinner, so after navigating, read the org count
line and confirm it changed before trusting anything on screen.

## Getting numbers out

- **Chart totals**: switch to `chartView=table` — it gives Funding, Number of
  Organizations, Funding per Organization and the normalized column as real rows you can
  read and export, instead of eyeballing bars.
- **Row-level data**: the Organizations and Funders tables, `CSV` button. It exports the
  *currently visible columns in their current order* with raw unformatted values, so switch
  to the single-table mode (not Side by side, which is compact) and set the columns first.
- Downloads land on Zein's machine, not here. To work with the rows yourself, either read
  them off the page or ask him where the file went and stage it.

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
information and check it with Zein before it becomes load-bearing: *"Crunchbase says this
round closed in March 2025 — the tracker has it in 2024. Which do you want to go with?"*
Never blend an outside number into a tracker total without saying so.

When the data genuinely cannot see a concept, say so plainly and name the nearest taxonomy
neighbor as a *neighbor, not a match*. A confident answer to a question the data didn't ask
is the worst failure mode here.

## Delivering

**Ask what form he wants** before building anything — Excel, a Claude artifact, a memo, a
doc, or just the answer in chat with the URL. The right answer varies with who's on the
other end of it, and guessing wastes a build.

Whatever the form, include:

- The **shareable URL** for every view you reference. The address bar *is* the share
  mechanism; there is no share button. Attach a one-line "why this view" to each — an
  emitted view is read as a claim.
- **Where to look**: "the funders table, below the chart". URLs carry data state, not
  attention state.
- The **filters in force**, including the defaults he didn't set (`operating_status=active`,
  `in_final_network=true`).

For Excel, read the `xlsx` skill. For a memo or doc, ask whether it's a living doc or a
file. For an artifact, read `artifact-design` first.

## Reference files

Read these as the session needs them — don't front-load all four.

| File | Read it when |
|---|---|
| `references/url-contract.md` | Building any URL; using advanced filters; anything about `filterQuery` |
| `references/fields.md` | Choosing filters, axes, metrics, or table columns; checking whether a field exists |
| `references/reading-the-data.md` | Before stating any number; whenever a result looks surprising |
| `references/tenants.md` | Working a tenant other than usclimate |

`scripts/build_url.py` builds explorer URLs from a small spec. Run
`python3 scripts/build_url.py --help` for usage.
