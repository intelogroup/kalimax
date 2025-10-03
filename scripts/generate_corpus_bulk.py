#!/usr/bin/env python3
"""
Generate 2000 parallel EN↔HT corpus pairs via templating.
Outputs CSV with columns:
  id, src_text, src_lang, tgt_text_literal, tgt_text_localized, tgt_lang, domain, is_idiom, contains_dosage, cultural_note, provenance, curation_status

Usage:
  python scripts/generate_corpus_bulk.py --count 2000 --output data/seed/02_corpus_bulk_2000.csv
"""
import argparse
import csv
from pathlib import Path
from random import choice

SUBJECTS_EN = ["I", "You", "He", "She", "We", "They", "The patient", "The doctor"]
SUBJECTS_HT = ["Mwen", "Ou", "Li", "Li", "Nou", "Yo", "Pasyan an", "Doktè a"]

ACTIONS = [
    ("need to", "bezwen"),
    ("should", "ta dwe"),
    ("must", "dwe"),
    ("can", "ka"),
    ("will", "pral"),
]

VERBS_EN = [
    ("take medicine", "pran renmèd"),
    ("drink water", "bwè dlo"),
    ("get some rest", "repoze"),
    ("see a doctor", "wè yon doktè"),
    ("wash hands", "lave men"),
    ("cover your mouth when coughing", "kouvri bouch lè w touse"),
    ("come back tomorrow", "retounen demen"),
    ("follow the instructions", "swiv enstriksyon yo"),
]

DOMAINS = ["medical", "public_health", "general"]


def make_pair():
    i = choice(range(len(SUBJECTS_EN)))
    subj_en = SUBJECTS_EN[i]
    subj_ht = SUBJECTS_HT[i]
    aux_en, aux_ht = choice(ACTIONS)
    (verb_en, verb_ht) = choice(VERBS_EN)

    # Simple sentence mapping
    src_en = f"{subj_en} {aux_en} {verb_en}."
    tgt_ht = f"{subj_ht} {aux_ht} {verb_ht}."
    # literal same as localized for synthetic pairs
    return src_en, tgt_ht


def generate_rows(count: int):
    rows = []
    for idx in range(1, count + 1):
        src_en, tgt_ht = make_pair()
        domain = choice(DOMAINS)
        rows.append({
            'id': f'corp_bulk_{idx:05d}',
            'src_text': src_en,
            'src_lang': 'eng_Latn',
            'tgt_text_literal': tgt_ht,
            'tgt_text_localized': tgt_ht,
            'tgt_lang': 'hat_Latn',
            'domain': domain,
            'is_idiom': 0,
            'contains_dosage': 0,
            'cultural_note': 'synthetic templated pair',
            'provenance': 'bulk_generator',
            'curation_status': 'draft',
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--count', type=int, default=2000)
    ap.add_argument('--output', type=Path, default=Path('data/seed/02_corpus_bulk_2000.csv'))
    args = ap.parse_args()

    rows = generate_rows(args.count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding="utf-8-sig", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Wrote {len(rows)} corpus pairs to {args.output}")

if __name__ == '__main__':
    main()
