#!/usr/bin/env python3
"""Scan food product photos and generate YAML data file using local vision model.

Usage:
    python scripts/scan.py --kategorie mlecne-vyrobky foto1.jpg foto2.jpg
    python scripts/scan.py --kategorie maso-a-uzeniny --model gemma3:4b *.jpg
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

import ollama
import yaml

PROMPT = """Z fotografií potravinového produktu přečti a extrahuj následující údaje.
Vrať POUZE YAML v tomto formátu, bez dalšího textu, bez markdown značek:

nazev: "Přesný název produktu z obalu"
znacka: "Značka/výrobce"
popis: "Krátký popis produktu (max 200 znaků)"
slozeni: "Kompletní složení z etikety (český text)"
nutrice:
  energie_kj: 0
  energie_kcal: 0
  bilkoviny: 0
  sacharidy: 0
  cukry: 0
  vlaknina: 0
  tuky: 0
  nasycene_mk: 0
  sul: 0

Pravidla:
- Nutriční hodnoty na 100 g
- Čísla bez jednotek (jen holá čísla, desetinná tečka)
- Pro "<0,5" nebo stopová množství uveď 0
- Pokud hodnota chybí na etiketě, vynech celý řádek
- Složení přepiš přesně jak je na etiketě (český text)
- Název a značku přepiš přesně z obalu
- V popisu stručně charakterizuj produkt"""


def slugify(text):
    """Simple slugify for filenames."""
    import unicodedata
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:80]


def extract_yaml(text):
    """Extract YAML from model response, stripping markdown fences."""
    # Remove markdown code fences
    text = re.sub(r"^```ya?ml?\s*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)
    text = text.strip()
    return text


def validate_nutrition(nutrice):
    """Check if macro energy roughly matches declared kcal (B×4 + S×4 + T×9 ≈ kcal)."""
    kcal = nutrice.get("energie_kcal", 0)
    bilk = nutrice.get("bilkoviny", 0)
    sach = nutrice.get("sacharidy", 0)
    tuky = nutrice.get("tuky", 0)
    vlak = nutrice.get("vlaknina", 0)

    if not kcal:
        return

    computed = bilk * 4 + sach * 4 + tuky * 9 + vlak * 2
    diff = abs(computed - kcal)
    pct = diff / kcal * 100 if kcal else 0

    print(f"\n  Validation: declared {kcal} kcal, computed {computed:.0f} kcal "
          f"(B={bilk}×4 + S={sach}×4 + T={tuky}×9 + Vl={vlak}×2)")

    if pct > 15:
        print(f"  ⚠ WARNING: difference {diff:.0f} kcal ({pct:.0f}%) — check values manually!")
    else:
        print(f"  ✓ OK (difference {pct:.0f}%)")


def scan(photos, model, kategorie, validate=True, data_dir="data"):
    """Send photos to vision model and generate YAML file."""

    # Build message with images
    images = []
    for photo in photos:
        if not os.path.isfile(photo):
            print(f"  Warning: {photo} not found, skipping")
            continue
        images.append(photo)

    if not images:
        print("Error: no valid photos provided")
        sys.exit(1)

    print(f"Sending {len(images)} photo(s) to {model}...")

    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": PROMPT,
            "images": images,
        }],
    )

    raw = response["message"]["content"]
    print(f"\n--- Raw response ---\n{raw}\n---\n")

    # Parse YAML
    yaml_text = extract_yaml(raw)
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        print("Raw YAML text:")
        print(yaml_text)
        sys.exit(1)

    if not data or "nazev" not in data:
        print("Error: model did not return valid data (missing 'nazev')")
        sys.exit(1)

    # Generate slug and paths
    slug = slugify(data["nazev"])
    cat_dir = os.path.join(data_dir, kategorie)
    imgs_dir = os.path.join(cat_dir, "imgs")
    os.makedirs(imgs_dir, exist_ok=True)

    # Copy photos and build image list
    img_refs = []
    for i, photo in enumerate(images):
        ext = Path(photo).suffix.lower() or ".jpg"
        if i == 0:
            dest_name = f"{slug}-produkt{ext}"
        elif i == 1:
            dest_name = f"{slug}-nutrice{ext}"
        else:
            dest_name = f"{slug}-{i+1}{ext}"

        dest = os.path.join(imgs_dir, dest_name)
        shutil.copy2(photo, dest)
        img_refs.append(f"imgs/{dest_name}")
        print(f"  Copied: {photo} -> {dest}")

    # Build output YAML
    out = {"nazev": data["nazev"]}

    if data.get("znacka"):
        out["znacka"] = data["znacka"]
    if data.get("popis"):
        out["popis"] = data["popis"]
    if data.get("slozeni"):
        out["slozeni"] = data["slozeni"]

    out["obrazky"] = img_refs

    if data.get("nutrice"):
        out["nutrice"] = {}
        for key in ["energie_kj", "energie_kcal", "bilkoviny", "sacharidy",
                     "cukry", "vlaknina", "tuky", "nasycene_mk", "sul"]:
            val = data["nutrice"].get(key)
            if val is not None:
                # Ensure numeric
                try:
                    out["nutrice"][key] = float(val)
                except (ValueError, TypeError):
                    pass

    # Validate nutrition data
    if validate and out.get("nutrice"):
        validate_nutrition(out["nutrice"])

    # Write YAML
    yml_path = os.path.join(cat_dir, f"{slug}.yml")
    with open(yml_path, "w", encoding="utf-8") as f:
        yaml.dump(out, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\nSaved: {yml_path}")
    print(f"Review the file and adjust if needed.")


def main():
    parser = argparse.ArgumentParser(description="Scan food photos → YAML")
    parser.add_argument("photos", nargs="+", help="Photo files (JPG)")
    parser.add_argument("--kategorie", "-k", required=True, help="Category slug (e.g. mlecne-vyrobky)")
    parser.add_argument("--model", "-m", default="qwen2.5vl:7b", help="Ollama model (default: qwen2.5vl:7b)")
    parser.add_argument("--no-validate", action="store_true", help="Skip nutrition validation")
    parser.add_argument("--data-dir", default="data", help="Data directory (default: data)")
    args = parser.parse_args()

    scan(args.photos, args.model, args.kategorie, validate=not args.no_validate, data_dir=args.data_dir)


if __name__ == "__main__":
    main()
