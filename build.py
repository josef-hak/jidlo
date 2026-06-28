#!/usr/bin/env python3
"""Convert data/*.yml files into Hugo content/potravina/*.md + copy images."""

import glob
import os
import shutil
from pathlib import Path

import yaml

DATA_DIR = os.environ.get("DATA_DIR", "data")
CONTENT_DIR = "content/potravina"
STATIC_IMG_DIR = "static/imgs/food"

CATEGORY_MAP = {
    "mlecne-vyrobky": "Mléčné výrobky",
    "maso-a-uzeniny": "Maso a uzeniny",
    "ovoce": "Ovoce",
    "zelenina": "Zelenina",
    "pecivo-a-obiloviny": "Pečivo a obiloviny",
    "lusteniny-a-orechy": "Luštěniny a ořechy",
    "napoje": "Nápoje",
    "sladkosti": "Sladkosti",
    "rostlinne-alternativy": "Veganské",
    "ostatni": "Ostatní",
}


def build():
    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(STATIC_IMG_DIR, exist_ok=True)

    # Clean old generated content
    for f in glob.glob(os.path.join(CONTENT_DIR, "*.md")):
        os.remove(f)

    count = 0
    for yml_path in sorted(glob.glob(os.path.join(DATA_DIR, "*/*.yml"))):
        with open(yml_path, "r", encoding="utf-8") as f:
            item = yaml.safe_load(f)

        slug = Path(yml_path).stem
        cat_dir = Path(yml_path).parent.name
        cat_name = CATEGORY_MAP.get(cat_dir, cat_dir)
        src_dir = str(Path(yml_path).parent)

        # Copy images
        hugo_images = []
        img_list = item.get("obrazky") or []
        if not img_list and item.get("obrazek"):
            img_list = [item["obrazek"]]

        for img_rel in img_list:
            src = os.path.join(src_dir, img_rel)
            if os.path.isfile(src):
                dest_name = os.path.basename(src)
                shutil.copy2(src, os.path.join(STATIC_IMG_DIR, dest_name))
                hugo_images.append(f"/imgs/food/{dest_name}")

        # Build front matter
        nutrice = item.get("nutrice", {})
        fm_lines = [
            "---",
            f'title: "{item["nazev"]}"',
        ]
        if item.get("znacka"):
            fm_lines.append(f'znacka: "{item["znacka"]}"')
        if item.get("popis"):
            fm_lines.append(f'popis: "{item["popis"]}"')
        if item.get("slozeni"):
            # Escape quotes in slozeni
            slozeni = item["slozeni"].replace('"', '\\"')
            fm_lines.append(f'slozeni: "{slozeni}"')

        fm_lines.append(f'kategorie: "{cat_name}"')
        fm_lines.append(f'kategorie_slug: "{cat_dir}"')

        if hugo_images:
            fm_lines.append("obrazky:")
            for img in hugo_images:
                fm_lines.append(f'  - "{img}"')

        # Nutrition fields
        for key in ["energie_kj", "energie_kcal", "bilkoviny", "sacharidy", "cukry",
                     "vlaknina", "tuky", "nasycene_mk", "sul"]:
            val = nutrice.get(key)
            if val is not None:
                fm_lines.append(f"{key}: {val}")

        fm_lines.append("---")

        md_path = os.path.join(CONTENT_DIR, f"{slug}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(fm_lines) + "\n")

        count += 1
        print(f"  [{count}] {item['nazev']}")

    print(f"\nBuild done! {count} items generated.")


if __name__ == "__main__":
    build()
