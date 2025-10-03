#!/usr/bin/env python3
"""
Generate 500 glossary entries.
Columns: creole_canonical,english_equivalents,aliases,domain,cultural_weight,preferred_for_patients,examples_bad,examples_good,notes,created_by
Usage:
  python scripts/generate_glossary_bulk.py --count 500 --output data/seed/01_glossary_bulk_500.csv
"""
import argparse
import csv
import json
from pathlib import Path
from random import choice

TERMS = [
    ("tèt", ["head"], ["tèt la"], "anatomy"),
    ("pwatrin", ["chest"], [], "anatomy"),
    ("doulè", ["pain"], ["mal"], "medical"),
    ("lafyèv", ["fever"], ["fyèv"], "medical"),
    ("renmèd", ["medicine","medication"], [], "medical"),
    ("randevou", ["appointment"], ["rdv"], "general"),
    ("operasyon", ["surgery"], [], "medical"),
    ("tansyon", ["blood pressure"], ["tansyon wo"], "medical"),
    ("dyabèt", ["diabetes"], ["sik"], "medical"),
    ("tous", ["cough"], ["touse"], "medical"),
]

WEIGHTS = ["neutral","positive","negative","taboo"]


def synthesize(count:int):
    rows=[]
    for i in range(count):
        cre,en,aliases,domain = choice(TERMS)
        rows.append({
            'creole_canonical': cre,
            'english_equivalents': json.dumps(en, ensure_ascii=False),
            'aliases': json.dumps(aliases, ensure_ascii=False),
            'domain': domain,
            'cultural_weight': choice(WEIGHTS),
            'preferred_for_patients': 1,
            'examples_bad': '',
            'examples_good': '',
            'notes': 'auto-generated; review',
            'created_by': 'bulk_generator'
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--count', type=int, default=500)
    ap.add_argument('--output', type=Path, default=Path('data/seed/01_glossary_bulk_500.csv'))
    args = ap.parse_args()

    rows = synthesize(args.count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding="utf-8-sig", newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"✅ Wrote {len(rows)} glossary rows to {args.output}")

if __name__ == '__main__':
    main()
