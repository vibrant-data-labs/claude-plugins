#!/usr/bin/env python3
"""Build a VDL tracker Data Explorer URL from a compact spec.

Handles the two things that are easy to get wrong by hand: repeatable ``filter.<key>``
params, and the JSON encoding of an advanced ``filterQuery``.

Examples
--------
Simple filters::

    python3 build_url.py --x solutions --color pillars \
        --filter pillars="Energy Transition" --filter org_type="Non Profit"

Map view of a cohort::

    python3 build_url.py --view map --filter drawdown_sectors=Electricity

Advanced filter (admin only) — pass the expression as JSON::

    python3 build_url.py --x pillars --query '{"all":[
        {"field":"pillars","op":"has_any","values":["Energy Transition","Nature Conservation"]},
        {"field":"org_type","op":"has_none","values":["Non Profit"]}]}'

Or build the same thing from shorthand clauses (all ANDed together)::

    python3 build_url.py --x pillars \
        --any pillars="Energy Transition,Nature Conservation" \
        --none org_type="Non Profit"

``--query`` and the shorthand cannot be combined with ``--filter``: the app rejects a URL
carrying both ``filter.*`` and ``filterQuery``.
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlencode

TENANTS = {
    "usclimate": "https://usclimate.vibrantdatalabs.org/",
    "demo": "https://demo.vibrantdatalabs.org/",
    "lft": "https://lft.vibrantdatalabs.org/",
    "drawdown": "https://drawdown.vibrantdatalabs.org/",
    "natureloc": "https://natureloc.climatefinancetracker.com/",
    "oneearth": "https://oneearth.climatefinancetracker.com/",
    "healthinnovations": "https://healthinnovations.vibrantdatalabs.org/",
}

MAX_URL_QUERY = 8000  # the app refuses a longer filterQuery-bearing link


def kv(pairs, what):
    out = []
    for raw in pairs or []:
        if "=" not in raw:
            sys.exit(f"--{what} needs field=value, got: {raw!r}")
        key, value = raw.split("=", 1)
        out.append((key.strip(), value))
    return out


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build a Data Explorer URL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--tenant", default="usclimate", choices=sorted(TENANTS),
                   help="default: usclimate")
    p.add_argument("--x", dest="x_attribute", help="Group by field id, e.g. pillars")
    p.add_argument("--color", dest="color_by", help="Split by field id, or 'none'")
    p.add_argument("--metric", dest="y_metric",
                   choices=["distributed_funding", "org_count"])
    p.add_argument("--show", dest="y_show",
                   choices=["ofGroup", "ofSubset", "ofAll", "growth"],
                   help="how the measure is read; omit for a plain amount")
    p.add_argument("--view", dest="chart_view",
                   choices=["chart", "heatmap", "scatter", "table", "map"],
                   help="'chart' is the default and emits no param")
    p.add_argument("--allocation", choices=["distributed", "full"],
                   help="default distributed")
    p.add_argument("--no-match", dest="show_no_match", action="store_true",
                   help="show the No Match group (hidden by default)")
    p.add_argument("--normalize", dest="normalize_by",
                   choices=["total", "xAttribute", "colorBy", "Growth Rate"])
    p.add_argument("--bar-mode", choices=["stacked", "grouped"])
    p.add_argument("--bar-layout", choices=["vertical", "horizontal"])
    p.add_argument("--contribution-scope", choices=["matching", "all"])
    p.add_argument("--schema")

    p.add_argument("--filter", action="append", metavar="FIELD=VALUE",
                   help="simple filter; repeat for more values or more fields")
    p.add_argument("--exclude", action="append", metavar="FIELD=VALUE",
                   help="filterExclude.<field>; honored server-side, no UI writes it")

    p.add_argument("--query", help="advanced filter: the 'where' expression as JSON")
    p.add_argument("--any", dest="has_any", action="append",
                   metavar="FIELD=V1,V2", help="shorthand has_any clause (ANDed)")
    p.add_argument("--none", dest="has_none", action="append",
                   metavar="FIELD=V1,V2", help="shorthand has_none clause (ANDed)")

    args = p.parse_args()

    simple = kv(args.filter, "filter") + kv(args.exclude, "exclude")
    advanced = args.query or args.has_any or args.has_none
    if simple and advanced:
        sys.exit("A URL cannot carry both filter.* and filterQuery — the app returns 400 "
                 "(AMBIGUOUS_FILTER_INPUT). Express everything in one or the other.")

    params: list[tuple[str, str]] = []

    def add(key, value):
        if value is not None:
            params.append((key, value))

    add("xAttribute", args.x_attribute)
    add("colorBy", args.color_by)
    add("yMetric", args.y_metric)
    add("yShow", args.y_show)
    if args.chart_view and args.chart_view != "chart":
        add("chartView", args.chart_view)
    add("normalizeBy", args.normalize_by)
    add("fundingMode", args.allocation)
    if args.show_no_match:
        add("showNoMatch", "true")
    add("barMode", args.bar_mode)
    add("barLayout", args.bar_layout)
    add("contributionScope", args.contribution_scope)
    add("schema", args.schema)

    for field, value in kv(args.filter, "filter"):
        params.append((f"filter.{field}", value))
    for field, value in kv(args.exclude, "exclude"):
        params.append((f"filterExclude.{field}", value))

    if advanced:
        if args.query:
            try:
                where = json.loads(args.query)
            except json.JSONDecodeError as exc:
                sys.exit(f"--query is not valid JSON: {exc}")
        else:
            clauses = []
            for op, pairs in (("has_any", args.has_any), ("has_none", args.has_none)):
                for field, value in kv(pairs, op.replace("has_", "")):
                    values = sorted({v.strip() for v in value.split(",") if v.strip()})
                    if not values:
                        sys.exit(f"clause {field!r} has no values")
                    clauses.append({"field": field, "op": op, "values": values})
            where = clauses[0] if len(clauses) == 1 else {"all": clauses}
        params.append(("filterQuery",
                       json.dumps({"version": 1, "where": where},
                                  separators=(",", ":"))))

    query = urlencode(params)
    if len(query) > MAX_URL_QUERY:
        sys.exit(f"Encoded query is {len(query)} chars, over the app's {MAX_URL_QUERY} "
                 "limit — it will be refused. Reduce the selected values.")

    print(TENANTS[args.tenant] + ("?" + query if query else ""))


if __name__ == "__main__":
    main()
