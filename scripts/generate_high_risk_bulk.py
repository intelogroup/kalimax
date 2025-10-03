#!/usr/bin/env python3
"""
Generate 200 high-risk items (dosage/triage/procedure) for review.
Columns (for a separate high_risk CSV, not directly corpus):
  id, src_en, tgt_ht_literal, tgt_ht_localized, contains_dosage, dosage_json, instruction_type, risk_level, safety_flags, require_human_review, provenance, notes
Usage:
  python scripts/generate_high_risk_bulk.py --count 200 --output data/seed/04_high_risk_bulk_200.csv
"""
import argparse
import csv
import json
from pathlib import Path
from random import choice, randint

DRUGS = [
    ("amoxicillin", 500, "mg"),
    ("azithromycin", 250, "mg"),
    ("ibuprofen", 400, "mg"),
    ("acetaminophen", 650, "mg"),
    ("metformin", 500, "mg"),
    ("lisinopril", 10, "mg"),
]

TRIAGE = [
    ("Call 911 immediately if chest pain worsens", "Rele 911 touswit si doulè kè a vin pi mal"),
    ("Go to the emergency room now if you cannot breathe well", "Ale nan ijans kounye a si ou pa ka respire byen"),
]

PROCEDURES = [
    ("Do not eat or drink after midnight before surgery", "Pa manje oswa bwè apre minwi avan operasyon"),
    ("Do not drive for 24 hours after anesthesia", "Pa kondwi pou 24 èdtan apre anestezi"),
]


def dosage_json(drug, qty, unit, freq_hrs=None, freq_txt=None, max_daily=None, duration=None):
    d={"drug":drug,"dose_qty":qty,"dose_unit":unit}
    if freq_hrs: d["frequency_hours"]=freq_hrs
    if freq_txt: d["frequency_text"]=freq_txt
    if max_daily: d["max_daily_dose"]=max_daily
    if duration: d["duration_days"]=duration
    return json.dumps(d)


def synthesize(count:int):
    rows=[]
    i=0
    while len(rows)<count:
        kind = choice(["dosage","triage","procedure"]) if len(rows)<count else "dosage"
        if kind=="dosage":
            drug, base_qty, unit = choice(DRUGS)
            qty = base_qty
            freq = choice([6,8,12,24])
            en = f"Take {drug} {qty}{unit} every {freq} hours"
            ht_lit = f"Pran {drug} {qty}{unit} chak {freq} èdtan"
            ht_loc = ht_lit
            rows.append({
                'id': f'hr_bulk_{len(rows)+1:04d}',
                'src_en': en,
                'tgt_ht_literal': ht_lit,
                'tgt_ht_localized': ht_loc,
                'contains_dosage': 1,
                'dosage_json': dosage_json(drug, qty, unit, freq_hrs=freq, freq_txt=f'every {freq} hours'),
                'instruction_type': 'dosage',
                'risk_level': choice(['high','medium']),
                'safety_flags': json.dumps(['requires_exact_dosage','human_review_required']),
                'require_human_review': 1,
                'provenance': 'bulk_generator',
                'notes': f'Dosage instruction for {drug}'
            })
        elif kind=="triage":
            en, ht = choice(TRIAGE)
            rows.append({
                'id': f'hr_bulk_{len(rows)+1:04d}',
                'src_en': en,
                'tgt_ht_literal': ht,
                'tgt_ht_localized': ht,
                'contains_dosage': 0,
                'dosage_json': '',
                'instruction_type': 'triage',
                'risk_level': 'high',
                'safety_flags': json.dumps(['emergency_instruction']),
                'require_human_review': 1,
                'provenance': 'bulk_generator',
                'notes': 'Emergency triage instruction'
            })
        else:
            en, ht = choice(PROCEDURES)
            rows.append({
                'id': f'hr_bulk_{len(rows)+1:04d}',
                'src_en': en,
                'tgt_ht_literal': ht,
                'tgt_ht_localized': ht,
                'contains_dosage': 0,
                'dosage_json': '',
                'instruction_type': 'procedure',
                'risk_level': choice(['medium','high']),
                'safety_flags': json.dumps(['safety_precaution']),
                'require_human_review': 1,
                'provenance': 'bulk_generator',
                'notes': 'Procedure safety guidance'
            })
        i+=1
    return rows[:count]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--count', type=int, default=200)
    ap.add_argument('--output', type=Path, default=Path('data/seed/04_high_risk_bulk_200.csv'))
    args = ap.parse_args()

    rows=synthesize(args.count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding="utf-8-sig", newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"✅ Wrote {len(rows)} high-risk rows to {args.output}")

if __name__=='__main__':
    main()
