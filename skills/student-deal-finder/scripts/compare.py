#!/usr/bin/env python3
"""Student Deal Finder: rank offers by the real total (price - discount + shipping + tax).

Exit codes: 0 ok, 2 offers file missing or malformed.
Standard library only.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "..", "assets", "sample_offers.json")


def money(x):
    return f"${x:,.2f}"


def total(o, tax_rate):
    price = float(o["price"])
    disc = float(o.get("discount", 0) or 0)
    if o.get("discount_percent"):
        disc += price * float(o["discount_percent"]) / 100.0
    ship = float(o.get("shipping", 0) or 0)
    taxed = o.get("taxed", True)
    base = max(price - disc, 0.0)
    tax = round(base * tax_rate / 100.0, 2) if taxed else 0.0
    return round(base + ship + tax, 2), round(disc, 2), tax


def main(argv=None):
    p = argparse.ArgumentParser(description="Rank offers by total cost.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--offers", help="JSON file with the offers")
    g.add_argument("--sample", action="store_true")
    p.add_argument("--tax-rate", type=float, default=0.0, help="Combined local sales tax in percent, e.g. 8.1")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)

    path = SAMPLE if a.sample else a.offers
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        offers = data["offers"] if isinstance(data, dict) else data
        rows = []
        for o in offers:
            t, d, tax = total(o, a.tax_rate)
            rows.append({**o, "total": t, "discount_applied": d, "tax": tax})
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"error: couldn't read the offers file ({e}). Each offer needs at least 'seller' and 'price'.")
        return 2
    if not rows:
        print("error: the offers file has no offers.")
        return 2

    rows.sort(key=lambda r: r["total"])
    new = [r for r in rows if str(r.get("condition", "new")).lower() == "new"]
    if a.json:
        print(json.dumps({"ranked": rows, "cheapest_overall": rows[0],
                          "cheapest_new": new[0] if new else None}, indent=2))
        return 0

    item = data.get("item", "Item") if isinstance(data, dict) else "Item"
    print(f"{item}: {len(rows)} offers, totals include shipping and {a.tax_rate:g}% tax")
    for r in rows:
        cond = str(r.get("condition", "new"))
        notes = [cond] if cond.lower() != "new" else []
        if r["discount_applied"]:
            notes.append(f"{money(r['discount_applied'])} off" + (f" ({r['discount_note']})" if r.get("discount_note") else ""))
        if r.get("shipping"):
            notes.append(f"{money(float(r['shipping']))} shipping")
        if r.get("pickup"):
            notes.append("pickup")
        tag = ""
        if r is rows[0]:
            tag = " <- cheapest"
        elif new and r is new[0]:
            tag = " <- cheapest new"
        extra = f" ({', '.join(notes)})" if notes else ""
        print(f"- {r['seller']}: {money(r['total'])}{extra}{tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
