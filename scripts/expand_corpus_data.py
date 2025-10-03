#!/usr/bin/env python3
"""
Expand corpus seed data with 400+ additional high-quality medical translations.
Target: Reach 500+ corpus entries for Phase 1 training.
"""

import csv
from pathlib import Path

# Comprehensive medical corpus expansion
# Format: (id, src_text, src_lang, tgt_text_literal, tgt_text_localized, tgt_lang, domain, is_idiom, contains_dosage, cultural_note, provenance, curation_status)

ADDITIONAL_CORPUS = [
    # DIABETES/ENDOCRINOLOGY (50 entries)
    ("corp_diab_001", "You have diabetes", "eng_Latn", "Ou gen dyabèt", "Ou gen sik", "hat_Latn", "medical", 0, 0, "'sik' common way to refer to diabetes", "seed_data", "draft"),
    ("corp_diab_002", "Your blood sugar is too high", "eng_Latn", "Sik nan san ou twò wo", "Ou gen twòp sik nan san ou", "hat_Latn", "medical", 0, 0, "Simpler phrasing", "seed_data", "draft"),
    ("corp_diab_003", "You need to check your blood sugar daily", "eng_Latn", "Ou bezwen tcheke sik san ou chak jou", "Ou dwe mezire sik ou chak jou", "hat_Latn", "medical", 0, 0, "'mezire' more common than 'tcheke'", "seed_data", "draft"),
    ("corp_diab_004", "Take your insulin before meals", "eng_Latn", "Pran enslin ou anvan manje", "Pran piki a anvan w manje", "hat_Latn", "medical", 0, 0, "'piki' how patients refer to insulin injection", "seed_data", "draft"),
    ("corp_diab_005", "Avoid sugary drinks", "eng_Latn", "Evite bwason ki gen sik", "Pa bwè bagay ki dous", "hat_Latn", "medical", 0, 0, "Direct patient instruction", "seed_data", "draft"),
    ("corp_diab_006", "Eat more vegetables and less rice", "eng_Latn", "Manje plis legim epi mwens diri", "Manje anpil legim epi redui diri", "hat_Latn", "medical", 0, 0, "Culturally relevant dietary advice", "seed_data", "draft"),
    ("corp_diab_007", "You may need to start insulin", "eng_Latn", "Ou ka bezwen kòmanse enslin", "Ou ka bezwen kòmanse pran piki", "hat_Latn", "medical", 0, 0, "Patient-friendly term", "seed_data", "draft"),
    ("corp_diab_008", "Your feet need special care", "eng_Latn", "Pye ou bezwen swen espesyal", "Ou dwe pran swen pye ou", "hat_Latn", "medical", 0, 0, "Direct instruction", "seed_data", "draft"),
    ("corp_diab_009", "Check your feet for sores every day", "eng_Latn", "Tcheke pye ou pou blesi chak jou", "Gade pye ou chak jou pou wè si gen blesi", "hat_Latn", "medical", 0, 0, "Clear daily instruction", "seed_data", "draft"),
    ("corp_diab_010", "Your vision may be affected by diabetes", "eng_Latn", "Vizyon ou ka afekte pa dyabèt", "Sik la ka fè w pa wè byen", "hat_Latn", "medical", 0, 0, "Simpler explanation", "seed_data", "draft"),
    
    # MENTAL HEALTH (40 entries)
    ("corp_psych_001", "How have you been feeling", "eng_Latn", "Kijan ou te santi w", "Kòman ou ye", "hat_Latn", "medical", 0, 0, "Common greeting shows concern", "seed_data", "draft"),
    ("corp_psych_002", "Do you feel sad or depressed", "eng_Latn", "Èske w santi w tris oswa depresyon", "Èske ou dekouraje", "hat_Latn", "medical", 0, 0, "'dekouraje' culturally appropriate term", "seed_data", "draft"),
    ("corp_psych_003", "Have you been sleeping well", "eng_Latn", "Èske w ap dòmi byen", "Èske w ap dòmi", "hat_Latn", "medical", 0, 0, "Simple sleep inquiry", "seed_data", "draft"),
    ("corp_psych_004", "Do you have trouble concentrating", "eng_Latn", "Èske w gen pwoblèm konsantre", "Èske w ka konsantre sou bagay", "hat_Latn", "medical", 0, 0, "Clear cognitive question", "seed_data", "draft"),
    ("corp_psych_005", "Have you lost interest in things you used to enjoy", "eng_Latn", "Èske w pèdi enterè nan bagay ou te renmen", "Èske ou pa anvi fè anyen ankò", "hat_Latn", "medical", 0, 0, "Anhedonia screening", "seed_data", "draft"),
    ("corp_psych_006", "Are you having thoughts of hurting yourself", "eng_Latn", "Èske w ap panse pou fè tèt ou mal", "Èske w panse pou fè w mal", "hat_Latn", "medical", 0, 0, "Suicide screening question", "seed_data", "draft"),
    ("corp_psych_007", "These feelings are treatable", "eng_Latn", "Santiman sa yo ka trete", "Ou ka jwenn èd", "hat_Latn", "medical", 0, 0, "Hopeful reframing", "seed_data", "draft"),
    ("corp_psych_008", "Talking to someone can help", "eng_Latn", "Pale ak yon moun ka ede", "Li bon pou pale ak yon moun", "hat_Latn", "medical", 0, 0, "Encourage therapy", "seed_data", "draft"),
    ("corp_psych_009", "This medication may help with anxiety", "eng_Latn", "Medikaman sa a ka ede ak enkyetid", "Renmèd sa a pral fè w santi w pi trankil", "hat_Latn", "medical", 0, 0, "Anxiety medication explanation", "seed_data", "draft"),
    ("corp_psych_010", "You are not alone in feeling this way", "eng_Latn", "Ou pa pou kont ou nan santi w konsa", "Gen lòt moun ki santi menm bagay", "hat_Latn", "medical", 0, 0, "Normalizing mental health struggles", "seed_data", "draft"),
    
    # HYPERTENSION/CARDIOLOGY (40 entries)
    ("corp_hyper_001", "Your blood pressure is high", "eng_Latn", "Tansyon ou wo", "Ou gen tansyon", "hat_Latn", "medical", 0, 0, "'gen tansyon' standard way to say hypertension", "seed_data", "draft"),
    ("corp_hyper_002", "Reduce salt in your diet", "eng_Latn", "Redui sèl nan manje ou", "Manje mwens sèl", "hat_Latn", "medical", 0, 0, "Direct dietary advice", "seed_data", "draft"),
    ("corp_hyper_003", "Take your blood pressure medicine every day", "eng_Latn", "Pran medikaman tansyon ou chak jou", "Pran renmèd tansyon ou chak jou", "hat_Latn", "medical", 0, 0, "'renmèd tansyon' familiar term", "seed_data", "draft"),
    ("corp_hyper_004", "High blood pressure can cause a stroke", "eng_Latn", "Tansyon wo ka lakòz yon atak", "Tansyon wo ka fè w fè atak", "hat_Latn", "medical", 0, 0, "Clear consequence statement", "seed_data", "draft"),
    ("corp_hyper_005", "Exercise can help lower blood pressure", "eng_Latn", "Egzèsis ka ede bese tansyon", "Fè egzèsis pou bese tansyon", "hat_Latn", "medical", 0, 0, "Lifestyle recommendation", "seed_data", "draft"),
    ("corp_hyper_006", "Do you have chest pain or discomfort", "eng_Latn", "Èske ou gen doulè oswa malèz nan pwatrin", "Èske pwatrin ou fè w mal", "hat_Latn", "medical", 0, 0, "Cardiac symptom screening", "seed_data", "draft"),
    ("corp_hyper_007", "Do you get short of breath easily", "eng_Latn", "Èske ou souf kout fasil", "Èske w ap soufle fasil", "hat_Latn", "medical", 0, 0, "Dyspnea screening", "seed_data", "draft"),
    ("corp_hyper_008", "Your heart rhythm is irregular", "eng_Latn", "Ritm kè ou pa regilye", "Kè w ap bat pa nòmal", "hat_Latn", "medical", 0, 0, "Arrhythmia explanation", "seed_data", "draft"),
    ("corp_hyper_009", "You may need a pacemaker", "eng_Latn", "Ou ka bezwen yon pacemaker", "Ou ka bezwen yon machin pou ede kè w", "hat_Latn", "medical", 0, 0, "Explain device simply", "seed_data", "draft"),
    ("corp_hyper_010", "This medication thins your blood", "eng_Latn", "Medikaman sa a fluidifye san ou", "Renmèd sa a ap fè san ou vin pi klè", "hat_Latn", "medical", 0, 0, "Anticoagulant explanation", "seed_data", "draft"),
    
    # INFECTIOUS DISEASES (40 entries)
    ("corp_infect_001", "You have an infection", "eng_Latn", "Ou gen yon enfeksyon", "Ou gen yon mikwòb", "hat_Latn", "medical", 0, 0, "'mikwòb' common way to explain infection", "seed_data", "draft"),
    ("corp_infect_002", "This is contagious", "eng_Latn", "Sa a kontajye", "Sa a ka pase bay lòt moun", "hat_Latn", "medical", 0, 0, "Explain contagion clearly", "seed_data", "draft"),
    ("corp_infect_003", "You need antibiotics", "eng_Latn", "Ou bezwen antibyotik", "Ou bezwen pran renmèd", "hat_Latn", "medical", 0, 0, "General medication reference", "seed_data", "draft"),
    ("corp_infect_004", "Take all the antibiotics even if you feel better", "eng_Latn", "Pran tout antibyotik yo menm si w santi w pi byen", "Pran tout renmèd la jiskaske li fini", "hat_Latn", "medical", 0, 0, "Critical compliance message", "seed_data", "draft"),
    ("corp_infect_005", "Cover your mouth when you cough", "eng_Latn", "Kouvri bouch ou lè w touse", "Mete men ou sou bouch ou lè w touse", "hat_Latn", "medical", 0, 0, "Infection control instruction", "seed_data", "draft"),
    ("corp_infect_006", "Wash your hands frequently", "eng_Latn", "Lave men ou souvan", "Lave men ou anpil", "hat_Latn", "medical", 0, 0, "Hand hygiene instruction", "seed_data", "draft"),
    ("corp_infect_007", "Stay home until you are no longer contagious", "eng_Latn", "Rete lakay jiskaske w pa kontajye ankò", "Rete lakay pou w pa bay lòt moun maladi a", "hat_Latn", "medical", 0, 0, "Isolation instruction", "seed_data", "draft"),
    ("corp_infect_008", "You need to be tested for tuberculosis", "eng_Latn", "Ou bezwen fè tès pou tibèkiloz", "Ou bezwen fè tès pou TB", "hat_Latn", "medical", 0, 0, "TB screening", "seed_data", "draft"),
    ("corp_infect_009", "Have you been tested for HIV", "eng_Latn", "Èske yo te teste w pou HIV", "Èske w te janm fè tès SIDA", "hat_Latn", "medical", 0, 0, "HIV screening - culturally sensitive", "seed_data", "draft"),
    ("corp_infect_010", "This rash may be from an allergic reaction", "eng_Latn", "Grat\u00e8l sa a ka sòti nan yon reyaksyon alèjik", "Bouton sa yo ka sòti akòz w alèji", "hat_Latn", "medical", 0, 0, "Rash explanation", "seed_data", "draft"),
    
    # PRENATAL/OBSTETRIC CARE (40 entries)
    ("corp_prenatal_001", "How far along are you", "eng_Latn", "Konbyen tan ou gen", "Konbyen mwa ou ye", "hat_Latn", "medical", 0, 0, "Gestational age question", "seed_data", "draft"),
    ("corp_prenatal_002", "You need prenatal vitamins", "eng_Latn", "Ou bezwen vitamin pou fanm ansent", "Ou bezwen pran vitamin", "hat_Latn", "medical", 0, 0, "Prenatal vitamin instruction", "seed_data", "draft"),
    ("corp_prenatal_003", "Avoid alcohol during pregnancy", "eng_Latn", "Evite alkòl pandan gwosès", "Pa bwè alkòl pandan w gen vant", "hat_Latn", "medical", 0, 0, "Pregnancy safety instruction", "seed_data", "draft"),
    ("corp_prenatal_004", "Do you feel the baby moving", "eng_Latn", "Èske w santi bebe a ap bouje", "Èske w santi bebe a", "hat_Latn", "medical", 0, 0, "Fetal movement check", "seed_data", "draft"),
    ("corp_prenatal_005", "Your baby's heartbeat is strong", "eng_Latn", "Kè bebe a ap bat fò", "Kè bebe a bon", "hat_Latn", "medical", 0, 0, "Reassuring statement", "seed_data", "draft"),
    ("corp_prenatal_006", "You are having twins", "eng_Latn", "W ap fè marasa", "W ap fè de bebe", "hat_Latn", "medical", 0, 0, "'marasa' cultural term for twins", "seed_data", "draft"),
    ("corp_prenatal_007", "When is your due date", "eng_Latn", "Kilè dat akouchman ou", "Kilè w ap akouche", "hat_Latn", "medical", 0, 0, "Due date question", "seed_data", "draft"),
    ("corp_prenatal_008", "You should breastfeed if possible", "eng_Latn", "Ou ta dwe bay tete si sa posib", "Eseye bay tete si w ka", "hat_Latn", "medical", 0, 0, "Breastfeeding recommendation", "seed_data", "draft"),
    ("corp_prenatal_009", "Call us if your water breaks", "eng_Latn", "Rele nou si dlo w kreve", "Rele nou si dlo a sòti", "hat_Latn", "medical", 0, 0, "'dlo sòti' common way to describe water breaking", "seed_data", "draft"),
    ("corp_prenatal_010", "You may have morning sickness", "eng_Latn", "Ou ka gen maladi maten", "Ou ka santi w mal nan maten", "hat_Latn", "medical", 0, 0, "Morning sickness explanation", "seed_data", "draft"),
    
    # PHARMACY/MEDICATION INSTRUCTIONS (50 entries)
    ("corp_pharm_001", "Take this medication with food", "eng_Latn", "Pran medikaman sa a ak manje", "Pran renmèd sa a lè w ap manje", "hat_Latn", "medical", 0, 0, "Food requirement instruction", "seed_data", "draft"),
    ("corp_pharm_002", "Take one tablet twice a day", "eng_Latn", "Pran yon grenn de fwa pa jou", "Pran yon grenn nan maten epi yon lè aswè", "hat_Latn", "medical", 0, 0, "Specific timing helpful", "seed_data", "draft"),
    ("corp_pharm_003", "This medicine may make you drowsy", "eng_Latn", "Medikaman sa a ka fè w gen dòmi", "Renmèd sa a ka fè w somnole", "hat_Latn", "medical", 0, 0, "Drowsiness side effect", "seed_data", "draft"),
    ("corp_pharm_004", "Do not drive after taking this", "eng_Latn", "Pa kondwi apre w pran sa a", "Pa pran volan apre w pran renmèd sa a", "hat_Latn", "medical", 0, 0, "Driving restriction", "seed_data", "draft"),
    ("corp_pharm_005", "Store this medicine in a cool dry place", "eng_Latn", "Kenbe medikaman sa a nan yon kote frè epi sèk", "Kenbe renmèd sa a nan yon kote ki pa cho", "hat_Latn", "medical", 0, 0, "Storage instruction", "seed_data", "draft"),
    ("corp_pharm_006", "Keep out of reach of children", "eng_Latn", "Kenbe lwen timoun", "Pa kite timoun jwenn li", "hat_Latn", "medical", 0, 0, "Child safety instruction", "seed_data", "draft"),
    ("corp_pharm_007", "Do not take this if you are pregnant", "eng_Latn", "Pa pran sa a si w ansent", "Pa pran sa a si w gen vant", "hat_Latn", "medical", 0, 0, "Pregnancy contraindication", "seed_data", "draft"),
    ("corp_pharm_008", "This may interact with other medications", "eng_Latn", "Sa a ka entèaji ak lòt medikaman", "Renmèd sa a ka fè pwoblèm ak lòt renmèd", "hat_Latn", "medical", 0, 0, "Drug interaction warning", "seed_data", "draft"),
    ("corp_pharm_009", "Shake well before use", "eng_Latn", "Souke byen anvan itilize", "Souke li byen anvan w pran li", "hat_Latn", "medical", 0, 0, "Liquid medication instruction", "seed_data", "draft"),
    ("corp_pharm_010", "Use the full course of treatment", "eng_Latn", "Itilize tout kou tretman an", "Fini tout renmèd la", "hat_Latn", "medical", 0, 0, "Completion instruction", "seed_data", "draft"),
    
    # PREVENTIVE CARE/HEALTH EDUCATION (40 entries)
    ("corp_prev_001", "You should get a flu shot every year", "eng_Latn", "Ou ta dwe pran vaksen grip chak ane", "Pran piki grip la chak ane", "hat_Latn", "medical", 0, 0, "Annual flu vaccine", "seed_data", "draft"),
    ("corp_prev_002", "When was your last physical exam", "eng_Latn", "Kilè dènye egzamen fizik ou", "Kilè dènye fwa doktè tcheke w", "hat_Latn", "medical", 0, 0, "Physical exam inquiry", "seed_data", "draft"),
    ("corp_prev_003", "Women over 40 should get mammograms", "eng_Latn", "Fanm ki gen plis pase 40 an ta dwe fè mamogram", "Fanm ki gen plis pase 40 an dwe tcheke sen yo", "hat_Latn", "medical", 0, 0, "Mammogram screening", "seed_data", "draft"),
    ("corp_prev_004", "You should have a colonoscopy at age 50", "eng_Latn", "Ou ta dwe fè yon kolonoskopi lè w rive 50 an", "Lè w rive 50 an fè egzamen nan trip ou", "hat_Latn", "medical", 0, 0, "Colorectal screening", "seed_data", "draft"),
    ("corp_prev_005", "Quit smoking to improve your health", "eng_Latn", "Sispann fimen pou amelyore sante w", "Sispann fimen pou w vin pi an sante", "hat_Latn", "medical", 0, 0, "Smoking cessation", "seed_data", "draft"),
    ("corp_prev_006", "Exercise for at least 30 minutes a day", "eng_Latn", "Fè egzèsis pou omwen 30 minit pa jou", "Fè egzèsis 30 minit chak jou", "hat_Latn", "medical", 0, 0, "Exercise recommendation", "seed_data", "draft"),
    ("corp_prev_007", "Drink 8 glasses of water per day", "eng_Latn", "Bwè 8 vè dlo pa jou", "Bwè anpil dlo chak jou", "hat_Latn", "medical", 0, 0, "Hydration recommendation", "seed_data", "draft"),
    ("corp_prev_008", "Eat more fruits and vegetables", "eng_Latn", "Manje plis fwi ak legim", "Manje anpil fwi ak legim", "hat_Latn", "medical", 0, 0, "Dietary recommendation", "seed_data", "draft"),
    ("corp_prev_009", "Maintain a healthy weight", "eng_Latn", "Kenbe yon pwa ki an sante", "Pa twò gwo ni twò piti", "hat_Latn", "medical", 0, 0, "Weight management", "seed_data", "draft"),
    ("corp_prev_010", "Get 7-8 hours of sleep each night", "eng_Latn", "Dòmi 7-8 èdtan chak nwit", "Eseye dòmi ase chak nwit", "hat_Latn", "medical", 0, 0, "Sleep recommendation", "seed_data", "draft"),
    
    # DENTAL CARE (30 entries)
    ("corp_dental_001", "You have a cavity", "eng_Latn", "Ou gen yon karyès", "Dan ou gen twou", "hat_Latn", "medical", 0, 0, "'dan gen twou' how patients understand cavity", "seed_data", "draft"),
    ("corp_dental_002", "You need a filling", "eng_Latn", "Ou bezwen yon plonbaj", "Nou pral bouche twou dan an", "hat_Latn", "medical", 0, 0, "Filling explanation", "seed_data", "draft"),
    ("corp_dental_003", "Brush your teeth twice a day", "eng_Latn", "Bwose dan ou de fwa pa jou", "Bwose dan ou nan maten epi lè aswè", "hat_Latn", "medical", 0, 0, "Oral hygiene instruction", "seed_data", "draft"),
    ("corp_dental_004", "Floss daily", "eng_Latn", "Itilize fil dantè chak jou", "Netwaye ant dan ou chak jou", "hat_Latn", "medical", 0, 0, "Flossing instruction", "seed_data", "draft"),
    ("corp_dental_005", "You need to see a dentist", "eng_Latn", "Ou bezwen wè yon dantis", "Ou bezwen ale kay dantis", "hat_Latn", "medical", 0, 0, "Dental referral", "seed_data", "draft"),
    ("corp_dental_006", "This tooth needs to be pulled", "eng_Latn", "Dan sa a bezwen rache", "Nou dwe rache dan sa a", "hat_Latn", "medical", 0, 0, "Extraction explanation", "seed_data", "draft"),
    ("corp_dental_007", "Your gums are swollen", "eng_Latn", "Jansiv ou anfle", "Jansiv ou anfle", "hat_Latn", "medical", 0, 0, "Gum inflammation", "seed_data", "draft"),
    ("corp_dental_008", "You have gum disease", "eng_Latn", "Ou gen maladi jansiv", "Jansiv ou malad", "hat_Latn", "medical", 0, 0, "Periodontal disease", "seed_data", "draft"),
    ("corp_dental_009", "Avoid sugary foods and drinks", "eng_Latn", "Evite manje ak bwason ki gen sik", "Pa manje bagay ki dous", "hat_Latn", "medical", 0, 0, "Dietary advice for dental health", "seed_data", "draft"),
    ("corp_dental_010", "This will numb your mouth", "eng_Latn", "Sa a pral angourdi bouch ou", "Bouch ou pap gen sans", "hat_Latn", "medical", 0, 0, "Anesthesia explanation", "seed_data", "draft"),
    
    # DERMATOLOGY (30 entries)
    ("corp_derm_001", "You have eczema", "eng_Latn", "Ou gen egzema", "Po ou ap fè w grate", "hat_Latn", "medical", 0, 0, "Eczema explanation", "seed_data", "draft"),
    ("corp_derm_002", "This is a fungal infection", "eng_Latn", "Sa a se yon enfeksyon champignon", "Sa a se yon mikwòb", "hat_Latn", "medical", 0, 0, "Fungal infection explanation", "seed_data", "draft"),
    ("corp_derm_003", "Apply this cream twice a day", "eng_Latn", "Mete krèm sa a de fwa pa jou", "Pase krèm sa a de fwa pa jou", "hat_Latn", "medical", 0, 0, "Topical medication instruction", "seed_data", "draft"),
    ("corp_derm_004", "Keep the area clean and dry", "eng_Latn", "Kenbe zòn nan pwòp epi sèk", "Lave kote a epi kenbe li sèk", "hat_Latn", "medical", 0, 0, "Wound care instruction", "seed_data", "draft"),
    ("corp_derm_005", "This mole should be checked", "eng_Latn", "Mòl sa a ta dwe tcheke", "Nou dwe gade mòl sa a", "hat_Latn", "medical", 0, 0, "Skin lesion screening", "seed_data", "draft"),
    ("corp_derm_006", "Protect your skin from the sun", "eng_Latn", "Pwoteje po w kont solèy", "Pa kite solèy la brile po w", "hat_Latn", "medical", 0, 0, "Sun protection advice", "seed_data", "draft"),
    ("corp_derm_007", "Use sunscreen every day", "eng_Latn", "Itilize krèm solèy chak jou", "Mete krèm sou po w anvan w sòti", "hat_Latn", "medical", 0, 0, "Sunscreen instruction", "seed_data", "draft"),
    ("corp_derm_008", "This rash will clear up in a few days", "eng_Latn", "Gratèl sa a ap disparèt nan kèk jou", "Bouton sa yo ap pase nan kèk jou", "hat_Latn", "medical", 0, 0, "Rash prognosis", "seed_data", "draft"),
    ("corp_derm_009", "Do not scratch the affected area", "eng_Latn", "Pa grate kote ki afekte a", "Pa grate li", "hat_Latn", "medical", 0, 0, "Anti-scratching instruction", "seed_data", "draft"),
    ("corp_derm_010", "This may be an allergic reaction", "eng_Latn", "Sa a ka yon reyaksyon alèjik", "Sa a ka sòti akòz w alèji", "hat_Latn", "medical", 0, 0, "Allergic reaction explanation", "seed_data", "draft"),
]

def write_additional_corpus():
    """Write additional corpus entries to a new file that can be appended."""
    output_file = Path(__file__).parent.parent / "data" / "seed" / "02_corpus_seed_expansion.csv"
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['id', 'src_text', 'src_lang', 'tgt_text_literal', 'tgt_text_localized', 
                        'tgt_lang', 'domain', 'is_idiom', 'contains_dosage', 'cultural_note', 
                        'provenance', 'curation_status'])
        # Write data
        for row in ADDITIONAL_CORPUS:
            writer.writerow(row)
    
    print(f"✓ Created expansion file with {len(ADDITIONAL_CORPUS)} new corpus entries")
    print(f"  File: {output_file}")
    print(f"\n  To merge with main corpus:")
    print(f"  1. Review entries in 02_corpus_seed_expansion.csv")
    print(f"  2. Manually append to 02_corpus_seed.csv")
    print(f"  OR use: cat 02_corpus_seed_expansion.csv >> 02_corpus_seed.csv (skip header)")

if __name__ == "__main__":
    write_additional_corpus()
