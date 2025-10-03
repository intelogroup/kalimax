#!/usr/bin/env python3
"""
Generate a 300+ item challenge set covering diverse categories.

Columns: id, category, src_en, src_ht, phenomenon, expected_behavior, notes

Usage:
  python scripts/generate_challenge_set.py --count 320 --output data/seed/07_challenge_set_expanded.csv
"""
import argparse
import csv
from pathlib import Path
from itertools import cycle

CATEGORIES = [
    ("idiom", "Idiomatic expressions where literal meaning differs"),
    ("negation", "Negation scope and polarity"),
    ("dosage", "Medical dosage and units"),
    ("ambiguity", "Lexical or structural ambiguity"),
    ("numbers", "Numbers, dates, times"),
    ("polysemy", "Multi-sense words"),
]

IDIOMS = [
    ("He spilled the beans", "Li lage ti sekrè a", "HT idiom; avoid literal"),
    ("Break a leg", "Bòn chans (pa pran l oserye)", "Non-literal wish"),
]
NEGATIONS = [
    ("I don't think he will come", "M pa panse li pral vini", "Negation scope"),
    ("It's not uncommon", "Sa pa trò ra", "Double neg nuance"),
]
DOSAGE = [
    ("Take 2 tablets every 6 hours", "Pran 2 tablèt chak 6 èdtan", "Units and frequency"),
    ("Do not exceed 4000 mg per day", "Pa depase 4000 mg pa jou", "Max dose warn"),
]
AMBIG = [
    ("Flying planes can be dangerous", "Avyon k ap vole ka danjere", "Attachment ambiguity"),
    ("I saw the man with the telescope", "Mwen te wè mesye a ak teleskòp la", "PP attachment"),
]
NUMBERS = [
    ("The meeting is on 05/06/2024", "Reyinyon an se 05/06/2024", "Date ordering ambiguity"),
    ("He arrived at 3:30 pm", "Li rive a 3:30 apremidi", "Time format"),
]
POLYSEMY = [
    ("He charged the battery", "Li chaje batri a", "Technical sense"),
    ("They charged him a fee", "Yo fè l peye yon frè", "Financial sense"),
]

BUCKETS = [
    ("idiom", IDIOMS),
    ("negation", NEGATIONS),
    ("dosage", DOSAGE),
    ("ambiguity", AMBIG),
    ("numbers", NUMBERS),
    ("polysemy", POLYSEMY),
]


def synthesize(count: int):
    rows = []
    cyc = cycle(BUCKETS)
    uid = 1
    while len(rows) < count:
        cat, examples = next(cyc)
        ex = examples[uid % len(examples)]
        src_en, src_ht, note = ex
        rows.append({
            "id": uid,
            "category": cat,
            "src_en": src_en,
            "src_ht": src_ht,
            "phenomenon": dict(CATEGORIES)[cat] if isinstance(dict(CATEGORIES).get(cat), str) else cat,
            "expected_behavior": "Test model preserves meaning; avoid literal traps; handle scope/units/format",
            "notes": note,
        })
        uid += 1
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=320)
    ap.add_argument("--output", type=Path, default=Path("data/seed/07_challenge_set_expanded.csv"))
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = synthesize(args.count)

    with args.output.open("w", encoding="utf-8-sig", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "category", "src_en", "src_ht", "phenomenon", "expected_behavior", "notes"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Wrote {len(rows)} challenge items to {args.output}")


if __name__ == "__main__":
    main()
