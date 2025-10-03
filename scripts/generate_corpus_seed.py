#!/usr/bin/env python3
"""
Generate comprehensive corpus seed data for Kalimax medical translation training.
This provides a solid foundation for the team to review, correct, and expand.
"""

import csv
import sys
from pathlib import Path

# Medical corpus data organized by specialty
CORPUS_DATA = [
    # Emergency Medicine
    ("corp_emerg_001", "This is a medical emergency", "eng_Latn", "Sa a se yon ijans medikal", "Sa a se ijans", "hat_Latn", "medical", 0, 0, "Urgent context clear", "seed_data", "draft"),
    ("corp_emerg_002", "Call 911 immediately", "eng_Latn", "Rele 911 imedyatman", "Rele 911 kounye a", "hat_Latn", "medical", 0, 0, "Immediate action required", "seed_data", "draft"),
    ("corp_emerg_003", "Are you having chest pain", "eng_Latn", "Èske ou gen doulè nan pwatrin", "Èske pwatrin ou fè w mal", "hat_Latn", "medical", 0, 0, "Common symptom question", "seed_data", "draft"),
    ("corp_emerg_004", "Can you breathe", "eng_Latn", "Èske ou ka respire", "Èske w ap respire", "hat_Latn", "medical", 0, 0, "Critical assessment", "seed_data", "draft"),
    ("corp_emerg_005", "Are you allergic to any medications", "eng_Latn", "Èske ou alèjik a nenpòt medikaman", "Èske gen renmèd ki fè w alèji", "hat_Latn", "medical", 0, 0, "Critical safety question", "seed_data", "draft"),
    ("corp_emerg_006", "When did the symptoms start", "eng_Latn", "Kilè sentòm yo te kòmanse", "Depi kilè sa kòmanse", "hat_Latn", "medical", 0, 0, "Timeline assessment", "seed_data", "draft"),
    ("corp_emerg_007", "Have you lost consciousness", "eng_Latn", "Èske ou te pèdi konesans", "Èske w te endòmi san ou pa konnen", "hat_Latn", "medical", 0, 0, "Explain loss of consciousness in simpler terms", "seed_data", "draft"),
    ("corp_emerg_008", "Do you have any medical conditions", "eng_Latn", "Èske ou gen nenpòt kondisyon medikal", "Èske w malad ak kèk bagay", "hat_Latn", "medical", 0, 0, "Medical history question", "seed_data", "draft"),
    ("corp_emerg_009", "We need to take you to the hospital", "eng_Latn", "Nou bezwen mennen w lopital", "Nou pral mennen w lopital", "hat_Latn", "medical", 0, 0, "Direct action statement", "seed_data", "draft"),
    ("corp_emerg_010", "Stay calm and breathe slowly", "eng_Latn", "Rete kalm epi respire dousman", "Pa pè epi respire dousman", "hat_Latn", "medical", 0, 0, "'Pa pè' (don't be afraid) more calming", "seed_data", "draft"),
    
    # Obstetrics/Gynecology
    ("corp_ob_001", "When was your last menstrual period", "eng_Latn", "Kilè dènye peryòd regl ou", "Kilè ou te wè regl ou dènye fwa", "hat_Latn", "medical", 0, 0, "Common OB question", "seed_data", "draft"),
    ("corp_ob_002", "Are you pregnant", "eng_Latn", "Èske ou ansent", "Èske w gen vant", "hat_Latn", "medical", 0, 0, "'gen vant' common way to say pregnant", "seed_data", "draft"),
    ("corp_ob_003", "How many weeks pregnant are you", "eng_Latn", "Konbyen semèn ou ansent", "Konbyen mwa ou gen", "hat_Latn", "medical", 0, 0, "Patients often count in months", "seed_data", "draft"),
    ("corp_ob_004", "Have you felt the baby move", "eng_Latn", "Èske ou te santi tibebe a ap bouje", "Èske w santi bebe a ap  regle", "hat_Latn", "medical", 0, 0, "'regle' common term for fetal movement", "seed_data", "draft"),
    ("corp_ob_005", "Do you have any cramping", "eng_Latn", "Èske ou gen nenpòt kranp", "Èske vant ou ap fè w mal", "hat_Latn", "medical", 0, 0, "Simpler symptom description", "seed_data", "draft"),
    ("corp_ob_006", "Are you having contractions", "eng_Latn", "Èske w ap gen kontraksyon", "Èske vant ou ap sere", "hat_Latn", "medical", 0, 0, "'vant ap sere' how contractions described", "seed_data", "draft"),
    ("corp_ob_007", "Your baby is healthy", "eng_Latn", "Tibebe ou a an sante", "Bebe a byen", "hat_Latn", "medical", 0, 0, "Reassuring statement", "seed_data", "draft"),
    ("corp_ob_008", "We need to do an ultrasound", "eng_Latn", "Nou bezwen fè yon iltrason", "Nou pral gade bebe a ak machin", "hat_Latn", "medical", 0, 0, "Explain procedure simply", "seed_data", "draft"),
    ("corp_ob_009", "It is time to push", "eng_Latn", "Se lè a pou pouse", "Kounye a pouse", "hat_Latn", "medical", 0, 0, "Direct delivery instruction", "seed_data", "draft"),
    ("corp_ob_010", "The baby is crowning", "eng_Latn", "Tèt tibebe a parèt", "Tèt bebe a ap sòti", "hat_Latn", "medical", 0, 0, "Delivery stage description", "seed_data", "draft"),
    
    # Neurology
    ("corp_neuro_001", "Are you having headaches", "eng_Latn", "Èske w ap gen tèt fè mal", "Èske tèt ou ap fè w mal", "hat_Latn", "medical", 0, 0, "Common neurological symptom", "seed_data", "draft"),
    ("corp_neuro_002", "Do you have any numbness or tingling", "eng_Latn", "Èske ou gen nenpòt angoudisman oswa pikotman", "Èske gen pati ki pa gen sans oswa ki ap pike", "hat_Latn", "medical", 0, 0, "Describe sensations clearly", "seed_data", "draft"),
    ("corp_neuro_003", "Have you had a seizure", "eng_Latn", "Èske ou te fè yon kriz", "Èske ou te fè kadik", "hat_Latn", "medical", 0, 0, "'kadik' common term for seizure", "seed_data", "draft"),
    ("corp_neuro_004", "Do you have problems with your memory", "eng_Latn", "Èske ou gen pwoblèm ak memwa ou", "Èske w ap bliye bagay", "hat_Latn", "medical", 0, 0, "Simpler cognitive question", "seed_data", "draft"),
    ("corp_neuro_005", "Can you raise both arms", "eng_Latn", "Èske ou ka leve tou de bra", "Leve de men ou", "hat_Latn", "medical", 0, 0, "Stroke assessment", "seed_data", "draft"),
    ("corp_neuro_006", "Can you smile for me", "eng_Latn", "Èske ou ka souri pou mwen", "Souri ban mwen", "hat_Latn", "medical", 0, 0, "Facial symmetry test", "seed_data", "draft"),
    ("corp_neuro_007", "Is your vision blurry", "eng_Latn", "Èske vizyon ou flou", "Èske w ap wè byen", "hat_Latn", "medical", 0, 0, "Vision assessment", "seed_data", "draft"),
    ("corp_neuro_008", "Do you have any weakness", "eng_Latn", "Èske ou gen nenpòt feblès", "Èske w santi w feb", "hat_Latn", "medical", 0, 0, "General weakness question", "seed_data", "draft"),
    ("corp_neuro_009", "You may have had a stroke", "eng_Latn", "Ou ka te fè yon atak serebral", "Ou ka te fè yon atak", "hat_Latn", "medical", 0, 0, "Serious diagnosis communication", "seed_data", "draft"),
    ("corp_neuro_010", "We need to do a CT scan", "eng_Latn", "Nou bezwen fè yon CT scan", "Nou pral pran foto sèvo ou", "hat_Latn", "medical", 0, 0, "Explain CT scan simply", "seed_data", "draft"),
    
    # Gastroenterology
    ("corp_gastro_001", "Do you have stomach pain", "eng_Latn", "Èske ou gen doulè nan vant", "Èske vant ou fè w mal", "hat_Latn", "medical", 0, 0, "Common GI complaint", "seed_data", "draft"),
    ("corp_gastro_002", "Have you been vomiting", "eng_Latn", "Èske w ap vomi", "Èske w ap voye jete", "hat_Latn", "medical", 0, 0, "'voye jete' also common for vomiting", "seed_data", "draft"),
    ("corp_gastro_003", "Do you have diarrhea", "eng_Latn", "Èske ou gen dyare", "Èske ou gen kouri vant", "hat_Latn", "medical", 0, 0, "'kouri vant' common term", "seed_data", "draft"),
    ("corp_gastro_004", "When was your last bowel movement", "eng_Latn", "Kilè dènye fwa ou te ale nan twalèt", "Kilè ou te fè poupou dènye fwa", "hat_Latn", "medical", 0, 0, "Simple direct question", "seed_data", "draft"),
    ("corp_gastro_005", "Is there blood in your stool", "eng_Latn", "Èske gen san nan poupou ou", "Èske w ap wè san lè w fè poupou", "hat_Latn", "medical", 0, 0, "Important symptom question", "seed_data", "draft"),
    ("corp_gastro_006", "Do you have heartburn", "eng_Latn", "Èske ou gen brile lestomak", "Èske lestomak ou ap boule", "hat_Latn", "medical", 0, 0, "'ap boule' describes burning sensation", "seed_data", "draft"),
    ("corp_gastro_007", "Avoid spicy foods", "eng_Latn", "Evite manje pike", "Pa manje bagay ki pike", "hat_Latn", "medical", 0, 0, "Dietary advice", "seed_data", "draft"),
    ("corp_gastro_008", "Drink plenty of water", "eng_Latn", "Bwè anpil dlo", "Bwè dlo anpil", "hat_Latn", "medical", 0, 0, "Hydration instruction", "seed_data", "draft"),
    ("corp_gastro_009", "You may need a colonoscopy", "eng_Latn", "Ou ka bezwen yon kolonoskopi", "Ou ka bezwen fè yon egzamen nan gwo trip", "hat_Latn", "medical", 0, 0, "Explain procedure", "seed_data", "draft"),
    ("corp_gastro_010", "This will help with digestion", "eng_Latn", "Sa a pral ede ak dijestyon", "Sa a pral ede vant ou travay byen", "hat_Latn", "medical", 0, 0, "Medication purpose", "seed_data", "draft"),
    
    # Orthopedics
    ("corp_ortho_001", "Where does it hurt", "eng_Latn", "Ki kote ki fè w mal", "Ki kote doulè a ye", "hat_Latn", "medical", 0, 0, "Pain location question", "seed_data", "draft"),
    ("corp_ortho_002", "Can you walk", "eng_Latn", "Èske ou ka mache", "Èske w ka mache", "hat_Latn", "medical", 0, 0, "Mobility assessment", "seed_data", "draft"),
    ("corp_ortho_003", "Is anything broken", "eng_Latn", "Èske gen bagay ki kase", "Èske gen zo ki kase", "hat_Latn", "medical", 0, 0, "Fracture assessment", "seed_data", "draft"),
    ("corp_ortho_004", "We need to take an X-ray", "eng_Latn", "Nou bezwen pran yon radyografi", "Nou pral pran yon foto nan zo a", "hat_Latn", "medical", 0, 0, "Explain X-ray simply", "seed_data", "draft"),
    ("corp_ortho_005", "You have a fracture", "eng_Latn", "Ou gen yon frakti", "Ou gen yon zo kase", "hat_Latn", "medical", 0, 0, "'zo kase' clearer than medical term", "seed_data", "draft"),
    ("corp_ortho_006", "We need to put a cast on it", "eng_Latn", "Nou bezwen mete yon plat sou li", "Nou pral mete plat", "hat_Latn", "medical", 0, 0, "Treatment explanation", "seed_data", "draft"),
    ("corp_ortho_007", "Use crutches to walk", "eng_Latn", "Itilize beki pou mache", "Sèvi ak beki pou mache", "hat_Latn", "medical", 0, 0, "Mobility aid instruction", "seed_data", "draft"),
    ("corp_ortho_008", "Do not put weight on it", "eng_Latn", "Pa mete pwa sou li", "Pa apiye sou li", "hat_Latn", "medical", 0, 0, "Weight-bearing restriction", "seed_data", "draft"),
    ("corp_ortho_009", "Your joint is swollen", "eng_Latn", "Jwenti ou anfle", "Jwenti ou anfle", "hat_Latn", "medical", 0, 0, "Joint assessment", "seed_data", "draft"),
    ("corp_ortho_010", "You may need physical therapy", "eng_Latn", "Ou ka bezwen terapi fizik", "Ou ka bezwen fè egzèsis pou kò ou reprann fòs", "hat_Latn", "medical", 0, 0, "Explain PT purpose", "seed_data", "draft"),
]

def append_to_corpus_file():
    """Append new corpus entries to the existing seed file."""
    corpus_file = Path(__file__).parent.parent / "data" / "seed" / "02_corpus_seed.csv"
    
    with open(corpus_file, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in CORPUS_DATA:
            writer.writerow(row)
    
    print(f"✓ Added {len(CORPUS_DATA)} new corpus entries to {corpus_file}")
    print(f"  Total entries now in file (including header): {len(CORPUS_DATA) + 66}")

if __name__ == "__main__":
    append_to_corpus_file()
