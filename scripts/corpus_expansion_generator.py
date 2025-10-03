#!/usr/bin/env python3
"""
Corpus Expansion Generator for Haitian Kreyol Medical Translations

This script generates synthetic parallel sentences using templates and variations
to expand the training corpus from ~5,656 to 15,000+ sentences.

Approach:
1. Template-based generation with slot filling
2. Domain-specific vocabulary substitution
3. Cultural localization variants
4. Automatic metadata generation

Usage:
    python corpus_expansion_generator.py --domain chronic_disease --count 1000
"""

import csv
import json
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import itertools


# =============================================================================
# MEDICAL DOMAIN TEMPLATES
# =============================================================================

# Template format: (English, Literal Haitian Kreyol, Localized Haitian Kreyol, cultural_note)

CHRONIC_DISEASE_TEMPLATES = [
    # Diabetes Management
    ("Check your blood sugar {frequency}",
     "Tcheke sik nan san ou {frequency}",
     "Mezire sik ou {frequency}",
     "Use familiar 'mezire' (measure) over formal 'tcheke'"),
    
    ("Your blood sugar is {level}",
     "Sik nan san ou {level}",
     "Sik ou {level}",
     "Shortened 'sik ou' more common in patient speech"),
    
    ("Take {medication} {frequency} for diabetes",
     "Pran {medication} {frequency} pou dyabèt",
     "Pran {medication} {frequency} pou pwoblèm sik",
     "'pwoblèm sik' (sugar problem) culturally familiar term"),
    
    ("Avoid eating too much {food}",
     "Evite manje twòp {food}",
     "Pa manje twòp {food}",
     "Direct negative command clearer"),
    
    ("You need to exercise {frequency}",
     "Ou bezwen fè egzèsis {frequency}",
     "Ou dwe mache {frequency}",
     "'mache' (walk) more actionable than abstract 'egzèsis'"),
    
    ("Your diabetes is under control",
     "Dyabèt ou anba kontwòl",
     "Dyabèt ou ap mache byen",
     "'ap mache byen' (going well) more reassuring"),
    
    ("Monitor your feet daily for sores",
     "Gade pye ou chak jou pou blesi",
     "Tcheke pye ou chak jou si gen blesi",
     "Add 'si gen' (if there are) for clarity"),
    
    ("Drink plenty of water",
     "Bwè anpil dlo",
     "Bwè dlo souvan",
     "'souvan' (often) more actionable than 'anpil'"),
    
    # Hypertension
    ("Your blood pressure is {level}",
     "Tansyon ou {level}",
     "Tansyon ou {level}",
     "'tansyon' commonly understood as blood pressure"),
    
    ("Take your blood pressure medication daily",
     "Pran medikaman tansyon ou chak jou",
     "Pran renmèd tansyon ou chak jou san w pa bliye",
     "Add emphasis 'san w pa bliye' (without forgetting)"),
    
    ("Reduce your salt intake",
     "Redui sèl ou manje",
     "Manje mwens sèl",
     "Simple directive clearer"),
    
    ("High blood pressure can cause {complication}",
     "Tansyon wo ka lakòz {complication}",
     "Si tansyon ou wo, ou ka fè {complication}",
     "Conditional structure 'si...ou ka' clearer"),
    
    ("Limit alcohol consumption",
     "Limite alkòl ou bwè",
     "Pa bwè twòp alkòl",
     "Direct negative command"),
    
    ("Manage your stress",
     "Jere estrès ou",
     "Pa kite bagay deranje w twòp",
     "Concrete advice vs abstract 'manage stress'"),
    
    # Asthma/Respiratory
    ("Use your inhaler when you have trouble breathing",
     "Itilize ponp ou lè w gen pwoblèm pou respire",
     "Sèvi ak ponp ou lè w ap soufle kout",
     "'soufle kout' natural description of shortness of breath"),
    
    ("Avoid {trigger} that makes your asthma worse",
     "Evite {trigger} ki fè opresyon ou vin pi mal",
     "Kenbe w lwen {trigger}, li ka fè w soufle",
     "'kenbe w lwen' (keep yourself away) more active"),
]

MENTAL_HEALTH_TEMPLATES = [
    # Depression Screening
    ("Have you been feeling sad or depressed",
     "Èske w santi w tris oswa dekouraje",
     "Èske w santi kè w lou anpil",
     "'kè lou' (heavy heart) culturally resonant metaphor"),
    
    ("Do you have trouble sleeping",
     "Èske w gen pwoblèm pou dòmi",
     "Èske w ka dòmi byen",
     "Positive framing may be easier to answer"),
    
    ("Have you lost interest in things you used to enjoy",
     "Èske w pèdi enterè nan bagay ki te konn fè w plezi",
     "Èske gen bagay ki konn fè w kontan men kounye a yo pa fè w anyen",
     "Concrete description vs abstract 'lost interest'"),
    
    ("Do you feel hopeless about the future",
     "Èske w santi w pa gen espwa pou lavni",
     "Èske w wè lavni w nwa",
     "'wè lavni nwa' (see future black) cultural idiom"),
    
    ("Have you had thoughts of hurting yourself",
     "Èske w gen lide pou fè tèt ou mal",
     "Èske w janm panse pou fè tèt ou kichòy",
     "Indirect phrasing 'kichòy' (something) culturally sensitive"),
    
    # Anxiety
    ("Do you worry excessively",
     "Èske w enkyete w anpil",
     "Èske w ap kalkile anpil",
     "'kalkile' (calculate/overthink) colloquial expression"),
    
    ("Do you feel nervous or on edge",
     "Èske w santi w nève oswa tansyone",
     "Èske w santi w pa poze",
     "'pa poze' (not calm) natural expression"),
    
    ("Do you have panic attacks",
     "Èske w fè kriz panik",
     "Èske w janm santi kè w pral soti",
     "'kè pral soti' (heart will come out) visceral description"),
    
    # PTSD/Trauma
    ("Have you experienced a traumatic event",
     "Èske w te viv yon evènman trawmatik",
     "Èske w te viv yon bagay ki te choke w anpil",
     "'choke' (shock) more accessible term"),
    
    ("Do you have nightmares or flashbacks",
     "Èske w fè move rèv oswa w wè bagay sa a ankò",
     "Èske w fè move rèv sou bagay la",
     "Simpler phrasing for flashbacks"),
]

PREVENTIVE_CARE_TEMPLATES = [
    # General Check-ups
    ("You should get a check-up {frequency}",
     "Ou dwe fè yon egzamen {frequency}",
     "Ou dwe vin wè doktè {frequency}",
     "'vin wè doktè' (come see doctor) more concrete"),
    
    ("Have you had your {screening} test",
     "Èske w te fè tès {screening} ou",
     "Èske yo te tcheke {screening} ou",
     "'tcheke' familiar term"),
    
    ("Prevention is better than cure",
     "Prevansyon pi bon pase tretman",
     "Pi bon ou pa malad pase w chache geri",
     "Proverb-style phrasing culturally resonant"),
    
    # Vaccinations
    ("You need your {vaccine} vaccine",
     "Ou bezwen pran vaksen {vaccine}",
     "Ou dwe pran piki {vaccine}",
     "'piki' how patients refer to shots"),
    
    ("The vaccine will protect you from {disease}",
     "Vaksen an ap pwoteje w kont {disease}",
     "Piki a ap anpeche w fè {disease}",
     "'anpeche' (prevent) more concrete than 'protect'"),
    
    ("Vaccines are safe and effective",
     "Vaksen yo an sekirite epi efikas",
     "Piki yo pa fè anyen, yo ede w",
     "Addresses safety concerns directly"),
    
    # Nutrition
    ("Eat more {food_group}",
     "Manje plis {food_group}",
     "Eseye manje plis {food_group}",
     "'eseye' (try) softer recommendation"),
    
    ("A balanced diet is important for your health",
     "Yon alijman balanse enpòtan pou sante ou",
     "Manje tout kalite manje bon pou ou",
     "Concrete advice vs abstract 'balanced diet'"),
]

PATIENT_QUESTIONS_TEMPLATES = [
    # Understanding Condition
    ("What is wrong with me",
     "Kisa ki pa bon avèk mwen",
     "Ki pwoblèm mwen genyen",
     "Direct question format"),
    
    ("Why do I need this test",
     "Poukisa m bezwen fè tès sa a",
     "Poukisa m dwe fè egzamen sa a",
     "'egzamen' slightly more formal"),
    
    ("What are the side effects of {medication}",
     "Ki efè segondè {medication} genyen",
     "Èske {medication} ka fè m kichòy",
     "'fè m kichòy' (do something to me) natural phrasing"),
    
    ("How long until I feel better",
     "Konben tan anvan m santi m pi byen",
     "Kilè m ap santi m miyò",
     "'kilè' (when) more direct"),
    
    ("Can I {activity} while taking this medication",
     "Èske m ka {activity} pandan m ap pran medikaman sa a",
     "Èske m kapab {activity} avèk renmèd sa a",
     "'kapab' stronger possibility"),
    
    # Cost/Access
    ("How much will this cost",
     "Konben sa ap koute",
     "Konben lajan mwen pral peye",
     "More direct about payment"),
    
    ("Do you accept my insurance",
     "Èske w aksepte asirans mwen",
     "Èske asirans mwen bon isit la",
     "'bon isit la' (good here) colloquial"),
    
    ("Where can I get this medication",
     "Kote m ka jwenn medikaman sa a",
     "Nan ki famasi m ka achte sa a",
     "Specific about pharmacy"),
]

WOMENS_HEALTH_TEMPLATES = [
    # Pregnancy/Prenatal
    ("When is your due date",
     "Kilè dat akouchman ou",
     "Kilè w ap akouche",
     "Direct question more natural"),
    
    ("Are you experiencing morning sickness",
     "Èske w ap fè vomisman nan maten",
     "Èske vant ou ap vire nan maten",
     "'vant vire' natural nausea description"),
    
    ("You need to take prenatal vitamins",
     "Ou bezwen pran vitamin prenatal",
     "Ou dwe pran vitamin pou gwosès",
     "Explain purpose of vitamins"),
    
    ("Your baby is developing normally",
     "Bebe ou ap devlope nòmalman",
     "Tibebe a ap grandi byen",
     "'grandi byen' reassuring phrasing"),
    
    ("Avoid alcohol during pregnancy",
     "Evite alkòl pandan gwosès",
     "Pa bwè alkòl pandan w ansent",
     "Direct negative command + 'ansent' colloquial"),
    
    # Family Planning
    ("What contraceptive method do you prefer",
     "Ki metòd kontrasepsyon ou prefere",
     "Ki jan ou vle pwoteje w",
     "Softer phrasing for sensitive topic"),
    
    ("This method is effective for preventing pregnancy",
     "Metòd sa a efikas pou anpeche gwosès",
     "Sa a ka anpeche w tonbe ansent",
     "Natural patient-level explanation"),
    
    # Menstrual Health
    ("When was your last period",
     "Kilè dènye peryòd ou",
     "Kilè dènye règ ou",
     "'règ' more commonly used"),
    
    ("Are your periods regular",
     "Èske peryòd ou regilye",
     "Èske w wè règ ou chak mwa",
     "Concrete phrasing about regularity"),
    
    ("Heavy bleeding is not normal",
     "Pèt san anpil pa nòmal",
     "Si w ap pèdi twòp san, sa pa bon",
     "Conditional structure adds concern"),
]

PEDIATRIC_TEMPLATES = [
    # Well-Child Visit
    ("Your child is growing well",
     "Pitit ou a ap grandi byen",
     "Tibebe a ap pouse byen",
     "'pouse' (sprouting) colloquial for growth"),
    
    ("Your child is at a healthy weight",
     "Pitit ou a gen yon pwa an sante",
     "Tibebe a gen bon pwa",
     "Simplified phrasing"),
    
    ("We need to check your child's development",
     "Nou bezwen tcheke devlopman pitit ou a",
     "Nou pral gade si tibebe a ap grandi byen",
     "Explain what 'development' means"),
    
    # Vaccinations
    ("Your child needs vaccinations today",
     "Pitit ou a bezwen vaksen jodi a",
     "Tibebe a pral resevwa piki jodi a",
     "'resevwa piki' how parents understand shots"),
    
    ("The shot might hurt for a moment",
     "Piki a ka fè mal pou yon ti moman",
     "Li ka plenyen yon ti jan men sa pral vit pase",
     "Prepare parent for crying, reassure it passes"),
    
    # Common Illnesses
    ("Your child has an ear infection",
     "Pitit ou a gen enfeksyon nan zòrèy",
     "Zòrèy tibebe a enfekte",
     "Simplified structure"),
    
    ("Give your child plenty of fluids",
     "Bay pitit ou anpil likid",
     "Fè li bwè anpil dlo",
     "Direct actionable instruction"),
    
    ("Keep your child home from school",
     "Kenbe pitit ou lakay li pa ale lekòl",
     "Pa voye li lekòl jodi a",
     "Direct command clearer"),
    
    ("This rash will go away in a few days",
     "Bouton sa a pral disparèt nan kèk jou",
     "Manchs sa yo ap pase nan kèk jou",
     "'manchs' (marks/spots) familiar term"),
    
    # Feeding/Nutrition
    ("Continue breastfeeding if possible",
     "Kontinye bay tete si posib",
     "Eseye ba li tete toujou",
     "'eseye' softer recommendation"),
]

LAB_RESULTS_TEMPLATES = [
    ("Your test results are normal",
     "Rezilta tès ou yo nòmal",
     "Rezilta ou yo bon",
     "'bon' simpler than 'nòmal'"),
    
    ("We found {finding} in your blood test",
     "Nou jwenn {finding} nan tès san ou",
     "Lè nou tcheke san ou, nou wè {finding}",
     "Explain what was found more concretely"),
    
    ("We need to run more tests",
     "Nou bezwen fè plis tès",
     "Nou dwe fè lòt egzamen",
     "'lòt egzamen' (other tests) clear"),
    
    ("Your cholesterol level is elevated",
     "Nivo kolestewòl ou elve",
     "Kolestewòl ou wo",
     "Simplified phrasing"),
    
    ("You need to fast before this test",
     "Ou bezwen fè jèn anvan tès sa a",
     "Pa manje anyen anvan ou vin fè tès la",
     "Direct instruction clearer"),
]

MEDICATION_INSTRUCTIONS_TEMPLATES = [
    ("Take this with food",
     "Pran sa a avèk manje",
     "Pran sa a lè w fini manje",
     "Specify timing more clearly"),
    
    ("Do not take this on an empty stomach",
     "Pa pran sa a sou vant vid",
     "Manje yon ti bagay anvan w pran sa a",
     "Positive instruction easier to follow"),
    
    ("This may make you drowsy",
     "Sa a ka fè w somnolan",
     "Sa a ka fè w anvi dòmi",
     "'anvi dòmi' (want to sleep) concrete"),
    
    ("Finish the entire course of antibiotics",
     "Fini tout kou antibyotik la",
     "Pran tout grenn yo jiskaske yo fini",
     "Count pills metaphorically, emphasize completion"),
    
    ("Store this medication in the refrigerator",
     "Mete medikaman sa a nan frijidè",
     "Kenbe renmèd sa a nan frizè",
     "'frizè' colloquial for refrigerator"),
    
    ("Take this at the same time every day",
     "Pran sa a nan menm lè chak jou",
     "Chwazi yon lè epi pran li chak jou nan lè sa a",
     "Help patient plan consistent timing"),
    
    ("Do not stop taking this suddenly",
     "Pa sispann pran sa a toudenkou",
     "Pa janm sispann pran sa a san w pa pale ak doktè",
     "Add consequence and proper action"),
]

POST_OPERATIVE_TEMPLATES = [
    ("Change the bandage daily",
     "Chanje panseman an chak jou",
     "Wete bandaj la epi mete yon lòt chak jou",
     "Spell out what 'change' means"),
    
    ("Keep the wound clean and dry",
     "Kenbe blesi a pwòp epi sèk",
     "Pa kite dlo touche kote operasyon an",
     "Concrete instruction about water"),
    
    ("Call us if you notice signs of infection",
     "Rele nou si w wè siy enfeksyon",
     "Rele nou si kote a vin wouj, anfle, oswa fè plis mal",
     "List specific signs patient should watch for"),
    
    ("You can resume normal activities in {timeframe}",
     "Ou ka reprann aktivite nòmal yo nan {timeframe}",
     "Nan {timeframe} w ap ka fè bagay ou konn fè yo",
     "More conversational phrasing"),
    
    ("Avoid heavy lifting for now",
     "Evite leve lou pou kounye a",
     "Pa leve bagay lou pou kèk tan",
     "Direct command + time frame"),
]

EMERGENCY_SYMPTOMS_TEMPLATES = [
    ("Call 911 if you have chest pain",
     "Rele 911 si w gen doulè nan pwatrin",
     "Si kè w ap fè w mal, rele 911 touswit",
     "More urgent phrasing"),
    
    ("Seek immediate care if you have difficulty breathing",
     "Chache swen imedya si w gen difikilte pou respire",
     "Si w pa ka respire byen, ale lopital touswit",
     "Direct action instruction"),
    
    ("This is a medical emergency",
     "Sa a se yon ijans medikal",
     "Ou bezwen wè doktè touswit",
     "Action-oriented rather than label"),
    
    ("Go to the emergency room now",
     "Ale nan sal ijans kounye a",
     "Ale lopital touswit",
     "Simplified instruction"),
    
    ("Do not drive yourself",
     "Pa kondui tèt ou",
     "Mande yon moun mennen w",
     "Positive action clearer"),
]

DIET_NUTRITION_TEMPLATES = [
    ("Eat {food_group} regularly",
     "Manje {food_group} regilyèman",
     "Eseye manje {food_group} souvan",
     "'eseye' softer than command"),
    
    ("Limit your intake of {food}",
     "Limite {food} ou manje",
     "Pa manje twòp {food}",
     "Direct negative clearer"),
    
    ("Choose whole grains over white rice",
     "Chwazi sereyal konplè olye diri blan",
     "Eseye manje diri kowonpe pito pase diri blan",
     "Local grain example"),
    
    ("Include protein in every meal",
     "Mete pwotein nan chak repa",
     "Manje vyann, pwason, oswa pwa chak fwa w manje",
     "List concrete protein sources"),
    
    ("Drink at least 8 glasses of water daily",
     "Bwè omwen 8 vè dlo chak jou",
     "Eseye bwè anpil dlo chak jou, omwen 8 vè",
     "'eseye' softer recommendation"),
]

FOLLOW_UP_APPOINTMENT_TEMPLATES = [
    ("We need to see you again in {timeframe}",
     "Nou bezwen wè w ankò nan {timeframe}",
     "Ou dwe tounen wè nou nan {timeframe}",
     "'tounen' (come back) natural"),
    
    ("Schedule a follow-up appointment",
     "Pran yon randevou suivi",
     "Pran yon lòt randevou",
     "Simplified phrasing"),
    
    ("Come back if symptoms worsen",
     "Tounen si sentòm yo vin pi mal",
     "Si w santi w pi mal, vin wè nou",
     "Condition clearer"),
    
    ("Bring your medication list to the appointment",
     "Pote lis medikaman ou nan randevou a",
     "Sonje pote tout renmèd w ap pran yo",
     "'sonje' (remember) reminder form"),
]

PAIN_ASSESSMENT_TEMPLATES = [
    ("Where does it hurt",
     "Kote ki fè mal",
     "Kote doulè a ye",
     "Both acceptable"),
    
    ("Point to where the pain is",
     "Montre kote doulè a ye",
     "Mete dwèt ou kote ki fè mal la",
     "Physical instruction clearer"),
    
    ("Does the pain come and go",
     "Èske doulè a vin epi pati",
     "Èske li fè mal tout tan oswa yon fwa yon fwa",
     "'yon fwa yon fwa' (intermittent) natural"),
    
    ("Is the pain constant",
     "Èske doulè a konstan",
     "Èske li fè mal tout tan",
     "Concrete phrasing"),
    
    ("Does anything make the pain better",
     "Èske gen anyen ki fè doulè a pi byen",
     "Ki sa ki ka ede w santi w miyò",
     "Reframe as help-seeking"),
]

# =============================================================================
# SLOT FILLERS - Vocabulary variations
# =============================================================================

SLOT_FILLERS = {
    "frequency": [
        ("every day", "chak jou", "chak jou"),
        ("twice a day", "de fwa pa jou", "de fwa chak jou"),
        ("once a week", "yon fwa pa semèn", "yon fwa chak semèn"),
        ("every morning", "chak maten", "chak maten"),
        ("every evening", "chak aswè", "tout aswè"),
        ("before meals", "anvan manje", "anvan w manje"),
        ("after meals", "apre manje", "apre w fini manje"),
    ],
    
    "level": [
        ("too high", "twò wo", "wo twòp"),
        ("too low", "twò ba", "ba twòp"),
        ("normal", "nòmal", "byen"),
        ("elevated", "elve", "monte"),
        ("very high", "trè wo", "wo anpil"),
    ],
    
    "medication": [
        ("metformin", "metfòmin", "metfòmin"),
        ("insulin", "ensilin", "ensilin"),
        ("lisinopril", "lisinopril", "lisinopril"),
        ("hydrochlorothiazide", "hydrochlorothiazide", "dyuretik"),  # generic term
        ("amlodipine", "amlodipin", "amlodipin"),
    ],
    
    "food": [
        ("sugar", "sik", "sik"),
        ("salt", "sèl", "sèl"),
        ("white rice", "diri blan", "diri blan"),
        ("fried food", "manje fri", "fritay"),
        ("sweets", "sikreri", "bagay dous"),
        ("soda", "soda", "gwazye"),  # colloquial
    ],
    
    "food_group": [
        ("vegetables", "legim", "legim"),
        ("fruits", "fwi", "fwi"),
        ("whole grains", "sereyal konplè", "diri kowonpe"),  # local grain
        ("lean protein", "pwotein mèg", "vyann san gres"),
        ("fish", "pwason", "pwason"),
    ],
    
    "complication": [
        ("a stroke", "yon atak serebral", "yon atak"),
        ("a heart attack", "yon atak kè", "kè w fè w pwoblèm"),
        ("kidney problems", "pwoblèm ren", "ren ou fè w mal"),
        ("vision problems", "pwoblèm je", "je w vin fèb"),
    ],
    
    "trigger": [
        ("smoke", "lafimen", "lafimen"),
        ("dust", "pousyè", "pousyè"),
        ("pollen", "polen", "poud flè"),
        ("pet dander", "plim bèt", "cheve bèt"),
        ("cold air", "lè frèt", "lè frèt"),
    ],
    
    "screening": [
        ("blood pressure", "tansyon", "tansyon"),
        ("cholesterol", "kolestewòl", "kolestewòl"),
        ("blood sugar", "sik nan san", "sik"),
        ("mammogram", "mamogram", "tcheke sen"),
        ("colonoscopy", "kolonoskopi", "tcheke trip"),
    ],
    
    "vaccine": [
        ("flu", "grip", "grip"),
        ("COVID-19", "COVID", "COVID"),
        ("tetanus", "tetanòs", "tetanòs"),
        ("hepatitis B", "epatit B", "epatit B"),
        ("pneumonia", "nemoni", "nemoni"),
    ],
    
    "disease": [
        ("flu", "grip", "grip"),
        ("COVID-19", "COVID", "COVID"),
        ("measles", "mich", "mich"),
        ("tetanus", "tetanòs", "tetanòs"),
        ("pneumonia", "nemoni", "nemoni"),
    ],
    
    "activity": [
        ("drive", "kondui", "kondui machin"),
        ("drink alcohol", "bwè alkòl", "bwè klewon"),  # colloquial
        ("work", "travay", "al travay"),
        ("exercise", "fè egzèsis", "fè espò"),
        ("swim", "naje", "naje"),
    ],
    
    "timeframe": [
        ("one week", "yon semèn", "yon semèn"),
        ("two weeks", "de semèn", "de semèn"),
        ("one month", "yon mwa", "yon mwa"),
        ("three months", "twa mwa", "twa mwa"),
        ("six weeks", "sis semèn", "sis semèn"),
    ],
    
    "finding": [
        ("elevated levels", "nivo elve", "nivo ki wo"),
        ("abnormal results", "rezilta anòmal", "bagay ki pa nòmal"),
        ("low levels", "nivo ba", "nivo ki ba"),
        ("infection markers", "mak enfeksyon", "siy enfeksyon"),
    ],
}


# =============================================================================
# GENERATION FUNCTIONS
# =============================================================================

def generate_variations(template: Tuple[str, str, str, str], 
                       slot_fillers: Dict[str, List[Tuple[str, str, str]]]) -> List[Dict]:
    """Generate all variations of a template by filling slots."""
    eng, ht_literal, ht_local, cultural_note = template
    
    # Find all slots in template
    import re
    slots = re.findall(r'\{(\w+)\}', eng)
    
    if not slots:
        # No slots, return single entry
        return [{
            'src_text': eng,
            'tgt_text_literal': ht_literal,
            'tgt_text_localized': ht_local,
            'cultural_note': cultural_note,
        }]
    
    # Generate all combinations
    variations = []
    
    # Get all possible values for each slot
    slot_options = {}
    for slot in set(slots):  # unique slots
        if slot in slot_fillers:
            slot_options[slot] = slot_fillers[slot]
        else:
            # Unknown slot, skip this template
            return []
    
    # Generate cartesian product
    keys = list(slot_options.keys())
    values = [slot_options[k] for k in keys]
    
    for combination in itertools.product(*values):
        slot_values = dict(zip(keys, combination))
        
        # Fill slots in English
        eng_filled = eng
        for slot, (eng_val, _, _) in slot_values.items():
            eng_filled = eng_filled.replace(f'{{{slot}}}', eng_val)
        
        # Fill slots in Haitian Kreyol literal
        ht_lit_filled = ht_literal
        for slot, (_, ht_lit_val, _) in slot_values.items():
            ht_lit_filled = ht_lit_filled.replace(f'{{{slot}}}', ht_lit_val)
        
        # Fill slots in Haitian Kreyol localized
        ht_loc_filled = ht_local
        for slot, (_, _, ht_loc_val) in slot_values.items():
            ht_loc_filled = ht_loc_filled.replace(f'{{{slot}}}', ht_loc_val)
        
        variations.append({
            'src_text': eng_filled,
            'tgt_text_literal': ht_lit_filled,
            'tgt_text_localized': ht_loc_filled,
            'cultural_note': cultural_note,
        })
    
    return variations


def generate_corpus_expansion(domains: List[str], target_count: int = 3000) -> List[Dict]:
    """Generate expanded corpus entries."""
    
    template_sets = {
        'chronic_disease': CHRONIC_DISEASE_TEMPLATES,
        'mental_health': MENTAL_HEALTH_TEMPLATES,
        'preventive_care': PREVENTIVE_CARE_TEMPLATES,
        'patient_questions': PATIENT_QUESTIONS_TEMPLATES,
        'womens_health': WOMENS_HEALTH_TEMPLATES,
        'pediatric': PEDIATRIC_TEMPLATES,
        'lab_results': LAB_RESULTS_TEMPLATES,
        'medication_instructions': MEDICATION_INSTRUCTIONS_TEMPLATES,
        'post_operative': POST_OPERATIVE_TEMPLATES,
        'emergency_symptoms': EMERGENCY_SYMPTOMS_TEMPLATES,
        'diet_nutrition': DIET_NUTRITION_TEMPLATES,
        'follow_up': FOLLOW_UP_APPOINTMENT_TEMPLATES,
        'pain_assessment': PAIN_ASSESSMENT_TEMPLATES,
    }
    
    all_entries = []
    entry_id = 10000  # Start IDs at 10000 for new entries
    
    for domain in domains:
        if domain not in template_sets:
            print(f"Warning: Unknown domain '{domain}'")
            continue
        
        templates = template_sets[domain]
        print(f"\nGenerating variations for domain: {domain}")
        print(f"  Templates: {len(templates)}")
        
        for template in templates:
            variations = generate_variations(template, SLOT_FILLERS)
            
            for var in variations:
                entry = {
                    'id': f'exp_{domain[:4]}_{entry_id:05d}',
                    'src_text': var['src_text'],
                    'src_lang': 'eng_Latn',
                    'tgt_text_literal': var['tgt_text_literal'],
                    'tgt_text_localized': var['tgt_text_localized'],
                    'tgt_lang': 'hat_Latn',
                    'domain': domain,
                    'is_idiom': '0',
                    'contains_dosage': '1' if 'medication' in var['src_text'].lower() else '0',
                    'context': json.dumps({'generated': True, 'template_based': True}),
                    'cultural_note': var['cultural_note'],
                    'provenance': 'template_generation',
                    'curation_status': 'needs_review',
                }
                all_entries.append(entry)
                entry_id += 1
        
        print(f"  Generated: {len([e for e in all_entries if e['domain'] == domain])} entries")
    
    # Shuffle to mix domains
    random.shuffle(all_entries)
    
    # Limit to target count
    if len(all_entries) > target_count:
        all_entries = all_entries[:target_count]
    
    return all_entries


def save_expansion(entries: List[Dict], output_path: Path):
    """Save generated entries to CSV."""
    fieldnames = [
        'id', 'src_text', 'src_lang', 'tgt_text_literal', 'tgt_text_localized',
        'tgt_lang', 'domain', 'is_idiom', 'contains_dosage', 'context',
        'cultural_note', 'provenance', 'curation_status'
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    
    print(f"\n✅ Saved {len(entries)} entries to: {output_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate corpus expansion')
    parser.add_argument('--domains', nargs='+', 
                       default=['chronic_disease', 'mental_health', 'preventive_care', 'patient_questions'],
                       help='Domains to generate')
    parser.add_argument('--count', type=int, default=3000,
                       help='Target number of sentences to generate')
    parser.add_argument('--output', type=str, 
                       default='data/seed/10_expansion_batch1.csv',
                       help='Output file path')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CORPUS EXPANSION GENERATOR")
    print("="*60)
    print(f"Target domains: {', '.join(args.domains)}")
    print(f"Target count: {args.count}")
    
    # Generate
    entries = generate_corpus_expansion(args.domains, args.count)
    
    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_expansion(entries, output_path)
    
    # Statistics
    print("\n" + "="*60)
    print("GENERATION STATISTICS")
    print("="*60)
    for domain in args.domains:
        count = len([e for e in entries if e['domain'] == domain])
        print(f"  {domain}: {count} sentences")
    print(f"\nTotal generated: {len(entries)} sentences")
    print(f"\n⚠️  Status: needs_review")
    print("Next step: Review and validate generated sentences")


if __name__ == '__main__':
    main()
