#!/usr/bin/env python3
"""
Generate 300 expressions/idioms rows.
Columns: creole,literal_gloss_en,idiomatic_en,localized_ht,register,region,cultural_note
Usage:
  python scripts/generate_expressions_bulk.py --count 300 --output data/seed/03_expressions_bulk_300.csv
"""
import argparse
import csv
from pathlib import Path
from random import choice

BASE = [
    ("Dèyè mòn gen mòn", "Behind mountains there are mountains", "Challenges keep coming", "Pwoblèm pa janm fini", "neutral", "General"),
    ("Men anpil, chay pa lou", "Many hands, load not heavy", "Many hands make light work", "Ansanm nou pi fò", "neutral", "General"),
    ("Piti piti zwazo fè nich li", "Little by little the bird builds its nest", "Progress comes gradually", "Dousman dousman n ap rive", "neutral", "General"),
    ("Kè sote pa geri maladi", "Worry does not cure illness", "Anxiety doesn’t heal", "Repoze tèt ou", "formal", "General"),
    ("Pa jije liv sou kouvèti li", "Don’t judge the book by its cover", "Appearances deceive", "Aparans ka twonpe", "neutral", "General"),
]
REGIONS = ["General","Haiti-North","Haiti-South","Diaspora-US","Diaspora-Canada","Diaspora-France"]
REGISTERS = ["formal","neutral","informal"]


def synthesize(count:int):
    rows=[]
    i=0
    while len(rows)<count:
        cre, lit, idio, ht, reg, region = choice(BASE)
        reg2 = choice(REGISTERS)
        region2 = choice(REGIONS)
        cre_var = cre if i%3 else f"{cre} ({region2})"
        rows.append({
            'creole': cre_var,
            'literal_gloss_en': lit,
            'idiomatic_en': idio,
            'localized_ht': ht,
            'register': reg2,
            'region': region2,
            'cultural_note': 'auto-generated; review'
        })
        i+=1
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--count', type=int, default=300)
    ap.add_argument('--output', type=Path, default=Path('data/seed/03_expressions_bulk_300.csv'))
    args = ap.parse_args()

    rows=synthesize(args.count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding="utf-8-sig", newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"✅ Wrote {len(rows)} expressions to {args.output}")

if __name__=='__main__':
    main()
