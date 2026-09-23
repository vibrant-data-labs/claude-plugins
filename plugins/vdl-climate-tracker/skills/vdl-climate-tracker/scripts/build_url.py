#!/usr/bin/env python3
"""Build a US Climate Finance Tracker Data Explorer URL from a compact spec.

Handles the things that are easy to get wrong by hand: repeatable ``filter.<key>``
params, the JSON encoding of an advanced ``filterQuery``, and keeping the default
baseline (Operating Status = active, CFT Organization = true) in a ``filterQuery``.

``--filter`` / ``--exclude`` emit ``filter.*`` / ``filterExclude.*``. The tracker converts
those to ``filterQuery`` on load and adds the baseline defaults, so share the address-bar
URL after the page has loaded, not this one.

Examples
--------
Simple filters::

    python3 build_url.py --x solutions --color pillars \
        --filter pillars="Energy Transition" --filter org_type="Non Profit"

Map view of a cohort::

    python3 build_url.py --view map --filter drawdown_sectors=Electricity

Advanced filter — pass the expression as JSON (the baseline leaves are added for you
unless the expression already mentions those fields, or you pass --no-baseline)::

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
}

# The sidebar's default filters. A filter.* URL gets them on load; a filterQuery URL
# does not, so they are written into the query explicitly.
BASELINE = [
    {"field": "operating_status", "op": "has_any", "values": ["active"]},
    {"field": "in_final_network", "op": "has_any", "values": ["true"]},
]

# Free-text fields take contains_any / contains_none instead of has_any / has_none.
KEYWORD_FIELDS = {"keyword"}

MAX_URL_QUERY = 8000  # the app refuses a longer filterQuery-bearing link


def kv(pairs, what):
    out = []
    for raw in pairs or []:
        if "=" not in raw:
            sys.exit(f"--{what} needs field=value, got: {raw!r}")
        key, value = raw.split("=", 1)
        out.append((key.strip(), value))
    return out


def fields_in(expr) -> set[str]:
    if isinstance(expr, dict):
        if "field" in expr:
            return {expr["field"]}
        return set().union(*(fields_in(e) for e in expr.get("all", expr.get("any", []))))
    return set()


def with_baseline(where):
    missing = [leaf for leaf in BASELINE if leaf["field"] not in fields_in(where)]
    if not missing:
        return where
    if where is None:
        parts = []
    elif isinstance(where, dict) and "all" in where:
        parts = list(where["all"])
    else:
        parts = [where]
    parts += missing
    return parts[0] if len(parts) == 1 else {"all": parts}


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
                   help="'chart' is the default and emits no param; heatmap and "
                        "scatter need an admin account")
    p.add_argument("--allocation", choices=["distributed", "full"],
                   help="default distributed")
    p.add_argument("--no-match", dest="show_no_match", action="store_true",
                   help="show the No Match group (hidden by default)")
    p.add_argument("--normalize", dest="normalize_by",
                   choices=["total", "xAttribute", "colorBy", "Growth Rate"])
    p.add_argument("--bar-mode", choices=["stacked", "grouped"])
    p.add_argument("--bar-layout", choices=["vertical", "horizontal"])
    p.add_argument("--contribution-scope", choices=["matching", "all"])
    p.add_argument("--table", dest="tables_view", choices=["side", "orgs", "funders"],
                   help="tables section mode; 'side' (Side by side) is the default")
    p.add_argument("--schema")

    p.add_argument("--filter", action="append", metavar="FIELD=VALUE",
                   help="simple filter; repeat for more values or more fields")
    p.add_argument("--exclude", action="append", metavar="FIELD=VALUE",
                   help="filterExclude.<field>, the sidebar's Exclude mode")

    p.add_argument("--query", help="advanced filter: the 'where' expression as JSON")
    p.add_argument("--any", dest="has_any", action="append",
                   metavar="FIELD=V1,V2",
                   help="shorthand has_any clause (contains_any for keyword; ANDed)")
    p.add_argument("--none", dest="has_none", action="append",
                   metavar="FIELD=V1,V2", help="shorthand has_none clause (ANDed)")
    p.add_argument("--no-baseline", action="store_true",
                   help="don't add the default Operating Status / CFT Organization "
                        "leaves to a filterQuery")

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
    add("table", args.tables_view)
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
            if isinstance(where, dict) and "where" in where:
                where = where["where"]  # a whole {"version":1,"where":…} was passed
        else:
            clauses = []
            for op, pairs in (("has_any", args.has_any), ("has_none", args.has_none)):
                for field, value in kv(pairs, op.replace("has_", "")):
                    values = sorted({v.strip() for v in value.split(",") if v.strip()})
                    if not values:
                        sys.exit(f"clause {field!r} has no values")
                    leaf_op = op.replace("has_", "contains_") if field in KEYWORD_FIELDS else op
                    clauses.append({"field": field, "op": leaf_op, "values": values})
            where = clauses[0] if len(clauses) == 1 else {"all": clauses}
        if not args.no_baseline:
            where = with_baseline(where)
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
