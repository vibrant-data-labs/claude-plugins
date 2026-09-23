# Vibrant Data Labs Claude plugins

A Claude plugin marketplace from [Vibrant Data Labs](https://vibrantdatalabs.org).

| Plugin | What it does |
|---|---|
| **VDL Climate Tracker** (`plugins/vdl-climate-tracker`) | Lets Claude work through the [US Climate Finance Tracker](https://usclimate.vibrantdatalabs.org) with you: set filters, read the organizations and funders tables, and turn what you find into funder briefs, prospect lists and comparisons that link back to the views they came from. |

## Install in Claude Desktop

Needs a paid Claude plan (Pro, Max, Team or Enterprise).

1. Open **Customize → Plugins → Personal plugins**.
2. Click **+ → Add marketplace → Add from a repository**.
3. Paste `https://github.com/vibrant-data-labs/claude-plugins`.
4. Install **VDL Climate Tracker** from the list that appears.

The tracker needs a sign-in; when Claude opens it in your browser, sign in there when asked.

## Layout

```
.claude-plugin/marketplace.json          marketplace entry (no version here)
plugins/vdl-climate-tracker/
  .claude-plugin/plugin.json             plugin manifest, holds the version
  skills/vdl-climate-tracker/            the skill: SKILL.md, references/, scripts/
```

## Releasing a change

- **Bump `version` in `plugins/vdl-climate-tracker/.claude-plugin/plugin.json` on every change.**
  Users only receive an update when the version changes, so a forgotten bump means nobody
  gets the fix. Keep the version in `plugin.json` only, not in `marketplace.json`.
- Rebuild the upload zip from the same folder at the same time:
  `cd plugins/vdl-climate-tracker/skills && zip -r vdl-climate-tracker.zip vdl-climate-tracker -x '*.DS_Store'`
- Any change to the tracker's URL or filter parameters needs a matching release, since the
  skill builds those URLs.
- Changes go through PR review; merging to `main` ships to everyone who added the marketplace.
