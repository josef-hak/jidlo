#!/usr/bin/env python3
"""Convert data/*.yml files into Hugo content/potravina/*.md + optimized images."""

import glob
import os
from pathlib import Path

import yaml
from PIL import Image

DATA_DIR = os.environ.get("DATA_DIR", "data")
CONTENT_DIR = "content/potravina"
STATIC_IMG_DIR = "static/imgs/food"

THUMB_SIZE = 300
FULL_MAX = 800
JPEG_QUALITY = 80

CATEGORY_MAP = {
    "mlecne-vyrobky": "Mléčné výrobky",
    "maso-a-uzeniny": "Maso a uzeniny",
    "ovoce": "Ovoce",
    "zelenina": "Zelenina",
    "pecivo-a-obiloviny": "Pečivo a obiloviny",
    "lusteniny-a-orechy": "Luštěniny a ořechy",
    "napoje": "Nápoje",
    "sladkosti": "Sladkosti",
    "veganske": "Veganské",
    "ostatni": "Ostatní",
}


def resize_image(src, dest, max_size, crop_square=False):
    """Resize image. If crop_square, crop center square then resize."""
    img = Image.open(src)
    img = img.convert("RGB")

    if crop_square:
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((max_size, max_size), Image.LANCZOS)
    else:
        img.thumbnail((max_size, max_size), Image.LANCZOS)

    img.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)


def build():
    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(STATIC_IMG_DIR, exist_ok=True)

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

        # Process images
        hugo_images = []
        img_list = item.get("obrazky") or []
        if not img_list and item.get("obrazek"):
            img_list = [item["obrazek"]]

        for i, img_rel in enumerate(img_list):
            src = os.path.join(src_dir, img_rel)
            if not os.path.isfile(src):
                continue

            base = Path(src).stem
            # Full size (max 800px, readable text)
            full_name = f"{base}.jpg"
            resize_image(src, os.path.join(STATIC_IMG_DIR, full_name), FULL_MAX)
            hugo_images.append(f"/imgs/food/{full_name}")

            # Thumbnail for first image only (300x300 square crop)
            if i == 0:
                thumb_name = f"{base}-thumb.jpg"
                resize_image(src, os.path.join(STATIC_IMG_DIR, thumb_name), THUMB_SIZE, crop_square=True)

        # Build front matter
        nutrice = item.get("nutrice", {})
        fm_lines = [
            "---",
            f'title: "{item["nazev"]}"',
        ]
        if item.get("znacka"):
            fm_lines.append(f'znacka: "{item["znacka"]}"')
        for field in ["popis", "slozeni"]:
            val = item.get(field)
            if val:
                val = val.strip()
                if "\n" in val:
                    fm_lines.append(f"{field}: |")
                    for line in val.split("\n"):
                        fm_lines.append(f"  {line}")
                else:
                    escaped = val.replace('"', '\\"')
                    fm_lines.append(f'{field}: "{escaped}"')

        fm_lines.append(f'kategorie: "{cat_name}"')
        fm_lines.append(f'kategorie_slug: "{cat_dir}"')

        if hugo_images:
            # Thumbnail = first image with -thumb suffix
            thumb = hugo_images[0].replace(".jpg", "-thumb.jpg")
            fm_lines.append(f'thumbnail: "{thumb}"')
            fm_lines.append("obrazky:")
            for img in hugo_images:
                fm_lines.append(f'  - "{img}"')

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
