#!/usr/bin/env python3
"""
Generate 10k+ monolingual Haitian Creole sentences.

Columns: id, text, domain, topic, complexity

Usage:
  python scripts/generate_monolingual_ht.py --count 12000 --output data/seed/08_monolingual_ht.csv

Notes:
- Uses templates + lexical substitution to create variety
- Covers medical, general, education, etc. domains
"""
import argparse
import csv
from pathlib import Path
from random import choice, randint


# Template-driven generation
TEMPLATES_MEDICAL = [
    "{subject} gen {symptom} {location}.",
    "{subject} {tense} pran {medication} {dosage}.",
    "Doktè a {tense} mande {subject} {action}.",
    "{condition} sa a ka {consequence}.",
    "Fòk {subject} {action} chak {frequency}.",
    "{subject} gen doulè nan {body_part} li.",
    "Renmèd la {tense} {effect} {subject}.",
    "{subject} dwe {action} anvan yo {test}.",
]

TEMPLATES_GENERAL = [
    "{subject} {tense} {verb} nan {location}.",
    "{subject} ap {verb} {object} yo.",
    "{weather} {tense} {intensity} jòdi a.",
    "{subject} bezwen {object} {purpose}.",
    "Yo te {verb} {object} nan {location}.",
    "{subject} {tense} wè {person} nan {location}.",
    "{activity} sa a {tense} {adjective}.",
    "{subject} ap {verb} pou {goal}.",
    "{time}, {subject} {tense} {verb}.",
]

TEMPLATES_EDUCATION = [
    "Elèv yo {tense} {verb} {subject_area}.",
    "Pwofesè a {tense} eksplike {topic}.",
    "{subject} ap {verb} nan {institution}.",
    "Egzamen an {tense} {difficulty}.",
    "Yo bezwen {verb} {material} yo.",
    "Klas la {tense} kòmanse a {time}.",
    "{subject} {tense} {performance} nan {test}.",
]

# Vocabulary sets for substitution
SUBJECTS = ["Mwen", "Ou", "Li", "Nou", "Yo", "Fanmi an", "Timoun nan", "Madanm nan", "Mesye a", "Granmoun yo"]
TENSES = ["", "te", "ap", "pral", "ka", "ta"]
VERBS = ["ale", "vini", "travay", "jwe", "manje", "bwè", "etidye", "pale", "tann", "gade", "koute", "li"]
LOCATIONS = ["lakay", "lopital la", "lekòl la", "mache a", "kay la", "vil la", "lakou a"]
SYMPTOMS = ["doulè", "maladi", "tenp", "tèt k ap fè mal", "vant k ap fè mal", "gòj ki gen doulè"]
MEDICATIONS = ["aspirinn", "paracetamol", "siwo", "kréyòl", "renmèd fèy"]
BODY_PARTS = ["tèt", "vant", "kè", "pye", "men", "do", "gòj", "pwatrin"]
OBJECTS = ["manje", "lajan", "rad", "kòb", "liv", "travay", "bagay"]
WEATHER = ["Solèy la", "Lapli a", "Van an", "Nwaj yo"]
ACTIVITIES = ["Jwe", "Travay", "Manje", "Etidye", "Danse", "Chante"]
ADJECTIVES = ["bèl", "lèd", "gwo", "ti", "bon", "move", "fasil", "difisil", "cho", "frè"]

# Compile template sets
TEMPLATE_SETS = [
    ("medical", TEMPLATES_MEDICAL),
    ("general", TEMPLATES_GENERAL),
    ("education", TEMPLATES_EDUCATION),
]


def substitute_template(template: str, domain: str):
    """Fill template with vocabulary appropriate to domain"""
    replacements = {
        "{subject}": choice(SUBJECTS),
        "{tense}": choice(TENSES),
        "{verb}": choice(VERBS),
        "{location}": choice(LOCATIONS),
        "{object}": choice(OBJECTS),
        "{adjective}": choice(ADJECTIVES),
        "{weather}": choice(WEATHER),
        "{activity}": choice(ACTIVITIES),
        "{intensity}": choice(["anpil", "yon ti kras", "twò", "pi bon"]),
        "{time}": choice(["nan maten", "nan aswè", "jòdi a", "yè", "demen"]),
        "{goal}": choice(["fè bagay yo", "ede moun yo", "gen lajan", "aprann"]),
        "{person}": choice(["zanmi li", "fanmi li", "vwazen an", "doktè a"]),
        "{purpose}": choice(["pou travay", "pou jwe", "pou manje", "pou etidye"]),
        "{frequency}": choice(["jou", "semèn", "mwa", "ane"]),
    }
    # Medical-specific
    if domain == "medical":
        replacements.update({
            "{symptom}": choice(SYMPTOMS),
            "{medication}": choice(MEDICATIONS),
            "{dosage}": f"{randint(1,4)} {choice(['tablèt', 'kiyè', 'kapsul'])}",
            "{body_part}": choice(BODY_PARTS),
            "{condition}": choice(["Maladi", "Doulè", "Pwoblèm", "Ensifizans"]),
            "{consequence}": choice(["danje", "pi mal", "pi bon", "koze pwoblèm"]),
            "{action}": choice(["pran renmèd", "repoze", "bwè dlo", "ale lopital"]),
            "{effect}": choice(["ede", "geri", "soulaje", "amelyore"]),
            "{test}": choice(["teste", "egzaminen", "operasyon"]),
        })
    # Education-specific
    elif domain == "education":
        replacements.update({
            "{subject_area}": choice(["matematik", "istwa", "syans", "kreyòl", "angle"]),
            "{topic}": choice(["fowmil yo", "evenman yo", "ekspèriman an"]),
            "{institution}": choice(["lekòl la", "inivèsite a", "bibliyotèk la"]),
            "{difficulty}": choice(["difisil", "fasil", "entèresan", "ennuyan"]),
            "{material}": choice(["liv", "karakil", "òdinatè", "tablo"]),
            "{performance}": choice(["reisi", "echwe", "byen fè", "pi mal"]),
            "{test}": choice(["egzamen", "devwa", "pwojè"]),
        })

    result = template
    for placeholder, replacement in replacements.items():
        result = result.replace(placeholder, replacement)
    return result.strip()


def generate_sentences(count: int):
    sentences = []
    for i in range(count):
        domain, templates = choice(TEMPLATE_SETS)
        template = choice(templates)
        text = substitute_template(template, domain)
        complexity = choice(["simple", "medium", "complex"])
        topic = {
            "medical": choice(["symptoms", "treatment", "doctor_visit", "medication"]),
            "general": choice(["daily_life", "family", "weather", "activities"]),
            "education": choice(["school", "learning", "exams", "teaching"]),
        }[domain]
        
        sentences.append({
            "id": i + 1,
            "text": text,
            "domain": domain,
            "topic": topic,
            "complexity": complexity,
        })
    return sentences


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=12000)
    ap.add_argument("--output", type=Path, default=Path("data/seed/08_monolingual_ht.csv"))
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sentences = generate_sentences(args.count)

    with args.output.open("w", encoding="utf-8-sig", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "text", "domain", "topic", "complexity"],
        )
        writer.writeheader()
        writer.writerows(sentences)

    print(f"✅ Generated {len(sentences)} Haitian Creole sentences to {args.output}")


if __name__ == "__main__":
    main()