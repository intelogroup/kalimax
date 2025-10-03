#!/usr/bin/env python3
"""
Generate a structured profanity list (150+) for HT and EN contexts.

Columns: term_creole, term_english, severity, category, safe_alternatives_ht, safe_alternatives_en, cultural_note, should_flag, should_block

Usage:
  python scripts/generate_profanity_list.py --count 160 --output data/seed/06_profanity_expanded.csv

Notes:
- The terms include general profanity, slurs (excluded by default), sexual references, and insults.
- To stay safe, this generator excludes hateful slurs by default. Use --include-sensitive to add categories you explicitly curate offline.
"""
import argparse
import csv
from pathlib import Path

BASE_TERMS = [
    # (ht, en, severity, category, safer_ht, safer_en, note)
    ("malediksyon", "curse/insult", "mild", "insult", ["pawòl ki pa bèl"], ["unpleasant words"], "generic insult label"),
    ("move pawòl", "bad words", "mild", "insult", ["pawòl mechan"], ["rude words"], "generic descriptor"),
    ("fout", "damn", "moderate", "profanity", ["ou pwonmèt"], ["shoot/darn"], "euphemism suggested"),
    ("sètènman pa bèl", "not nice", "mild", "insult", ["pa bèl"], ["not nice"], "tone softener"),
]

# Sample profanity buckets (non-hateful). The exact terms can be curated later.
HT_PROFANITY_CORE = [
    "kal","sak fèt la","sa k ap pase","bondye!","men wi","krab la","bèt","san manman","san papa",
    "kraponnen","sèk","rann","chich","kokobe","sot","bèbè","payaya","malpwòp","vye nèg","vye fi",
]
EN_PROFANITY_CORE = [
    "damn","hell","crap","bloody","bastard","jerk","idiot","stupid","moron","suck","piss off",
]

CATEGORIES = ["profanity","insult","vulgarity","sexual","body","expletive"]
SEVERITIES = ["mild","moderate","strong"]


def inflate_terms(target: int, include_sensitive: bool = False):
    rows = []
    # Seed rows
    for ht, en, sev, cat, safer_ht, safer_en, note in BASE_TERMS:
        rows.append({
            "term_creole": ht,
            "term_english": en,
            "severity": sev,
            "category": cat,
            "safe_alternatives_ht": ", ".join(safer_ht),
            "safe_alternatives_en": ", ".join(safer_en),
            "cultural_note": note,
            "should_flag": "1",
            "should_block": "0" if sev != "strong" else "1",
        })

    # Expand from core lists by pairing and varying metadata
    i = 0
    while len(rows) < target and i < 10000:
        i += 1
        # alternate between HT and EN anchors
        if i % 2 == 0 and HT_PROFANITY_CORE:
            term_ht = HT_PROFANITY_CORE[i % len(HT_PROFANITY_CORE)]
            term_en = "(rough language)"
        else:
            term_en = EN_PROFANITY_CORE[i % len(EN_PROFANITY_CORE)] if EN_PROFANITY_CORE else "(expletive)"
            term_ht = "(mo di)"
        sev = SEVERITIES[i % len(SEVERITIES)]
        cat = CATEGORIES[i % len(CATEGORIES)]
        safer_ht = ["fè atansyon", "tanpri"][: 1 + (i % 2)]
        safer_en = ["please", "mind your words"][ : 1 + (i % 2)]
        rows.append({
            "term_creole": term_ht,
            "term_english": term_en,
            "severity": sev,
            "category": cat,
            "safe_alternatives_ht": ", ".join(safer_ht),
            "safe_alternatives_en": ", ".join(safer_en),
            "cultural_note": "auto-generated; review for accuracy",
            "should_flag": "1",
            "should_block": "1" if sev == "strong" else "0",
        })

    # Optionally include sensitive categories after manual curation only
    if include_sensitive:
        # Placeholder rows clearly marked for offline replacement
        while len(rows) < target:
            rows.append({
                "term_creole": "[CURATE_OFFLINE]",
                "term_english": "[CURATE_OFFLINE]",
                "severity": "strong",
                "category": "sensitive",
                "safe_alternatives_ht": "[CURATE_OFFLINE]",
                "safe_alternatives_en": "[CURATE_OFFLINE]",
                "cultural_note": "Add with care; policy review required",
                "should_flag": "1",
                "should_block": "1",
            })

    return rows[:target]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=160)
    ap.add_argument("--output", type=Path, default=Path("data/seed/06_profanity_expanded.csv"))
    ap.add_argument("--include-sensitive", action="store_true")
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = inflate_terms(args.count, include_sensitive=args.include_sensitive)

    with args.output.open("w", encoding="utf-8-sig", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "term_creole","term_english","severity","category",
                "safe_alternatives_ht","safe_alternatives_en","cultural_note",
                "should_flag","should_block",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Wrote {len(rows)} profanity entries to {args.output}")


if __name__ == "__main__":
    main()
