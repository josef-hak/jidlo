#!/usr/bin/env python3
"""Seed food items from data/ YAML files directly into WordPress DB.

Usage inside wp-setup or standalone:
    python3 /tmp/seed.py

Connects to MariaDB via env vars (WORDPRESS_DB_HOST, WORDPRESS_DB_USER, etc.)
and bulk-inserts all items in a single transaction for speed.
"""

import glob
import os
import shutil
import sys
import time
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import mysql.connector
import yaml


def slugify(text):
    """Convert text to URL-safe slug (like WordPress sanitize_title)."""
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:200]

DATA_DIR = os.environ.get("DATA_DIR", "/tmp/data")
WP_UPLOADS = "/var/www/html/wp-content/uploads"

NUTRI_KEYS = [
    "energie_kj", "energie_kcal", "tuky", "nasycene_mk",
    "sacharidy", "cukry", "vlaknina", "bilkoviny", "sul",
]

# Map directory name -> category name
CATEGORY_MAP = {
    "mlecne-vyrobky": "Mléčné výrobky",
    "maso-a-uzeniny": "Maso a uzeniny",
    "ovoce": "Ovoce",
    "zelenina": "Zelenina",
    "pecivo-a-obiloviny": "Pečivo a obiloviny",
    "lusteniny-a-orechy": "Luštěniny a ořechy",
    "napoje": "Nápoje",
    "sladkosti": "Sladkosti",
    "ostatni": "Ostatní",
}


def get_connection():
    """Connect to WordPress MariaDB with retry."""
    for attempt in range(30):
        try:
            return mysql.connector.connect(
                host=os.environ.get("WORDPRESS_DB_HOST", "db"),
                user=os.environ.get("WORDPRESS_DB_USER", "wordpress"),
                password=os.environ.get("WORDPRESS_DB_PASSWORD", "wordpress"),
                database=os.environ.get("WORDPRESS_DB_NAME", "wordpress"),
                charset="utf8mb4",
            )
        except mysql.connector.Error:
            if attempt < 29:
                time.sleep(2)
            else:
                raise


def wait_for_wp_tables(conn):
    """Wait until WordPress core tables exist (wp-setup has finished)."""
    cur = conn.cursor()
    for attempt in range(60):
        try:
            cur.execute("SELECT option_value FROM wp_options WHERE option_name = 'siteurl'")
            if cur.fetchone():
                cur.close()
                return
        except mysql.connector.Error:
            pass
        print(f"  Waiting for WordPress tables... ({attempt + 1})")
        time.sleep(3)
    cur.close()
    raise RuntimeError("WordPress tables not ready after 3 minutes")


def get_or_create_term(cur, name, taxonomy="kategorie_potravin"):
    """Get or create a taxonomy term, return term_taxonomy_id."""
    cur.execute(
        "SELECT t.term_id, tt.term_taxonomy_id FROM wp_terms t "
        "JOIN wp_term_taxonomy tt ON t.term_id = tt.term_id "
        "WHERE t.name = %s AND tt.taxonomy = %s",
        (name, taxonomy),
    )
    row = cur.fetchone()
    if row:
        return row[1]

    slug = slugify(name)

    cur.execute("INSERT INTO wp_terms (name, slug) VALUES (%s, %s)", (name, slug))
    term_id = cur.lastrowid
    cur.execute(
        "INSERT INTO wp_term_taxonomy (term_id, taxonomy, description, parent, count) "
        "VALUES (%s, %s, '', 0, 0)",
        (term_id, taxonomy),
    )
    return cur.lastrowid


def import_image(cur, image_path, post_id):
    """Copy image to wp-content/uploads and create attachment post."""
    if not os.path.isfile(image_path):
        return None

    now = datetime.now()
    upload_subdir = now.strftime("%Y/%m")
    upload_dir = os.path.join(WP_UPLOADS, upload_subdir)
    os.makedirs(upload_dir, exist_ok=True)

    filename = os.path.basename(image_path)
    dest = os.path.join(upload_dir, filename)

    # Avoid overwriting — add suffix if exists
    if os.path.exists(dest):
        base, ext = os.path.splitext(filename)
        dest = os.path.join(upload_dir, f"{base}-{post_id}{ext}")
        filename = os.path.basename(dest)

    shutil.copy2(image_path, dest)

    rel_path = f"{upload_subdir}/{filename}"
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        "INSERT INTO wp_posts (post_author, post_date, post_date_gmt, post_content, "
        "post_title, post_excerpt, post_status, comment_status, ping_status, "
        "post_name, to_ping, pinged, post_content_filtered, "
        "post_modified, post_modified_gmt, post_parent, guid, "
        "post_type, post_mime_type) "
        "VALUES (1, %s, %s, '', %s, '', 'inherit', 'open', 'closed', "
        "%s, '', '', '', %s, %s, %s, %s, 'attachment', 'image/jpeg')",
        (now_str, now_str, filename, filename, now_str, now_str, post_id,
         f"/wp-content/uploads/{rel_path}"),
    )
    att_id = cur.lastrowid

    cur.execute(
        "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, '_wp_attached_file', %s)",
        (att_id, rel_path),
    )

    return att_id


def load_items():
    """Load all YAML files from data/ subdirectories."""
    items = []
    for yml_path in sorted(glob.glob(os.path.join(DATA_DIR, "*/*.yml"))):
        with open(yml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        category_dir = Path(yml_path).parent.name
        data["_kategorie"] = CATEGORY_MAP.get(category_dir, category_dir)
        data["_dir"] = str(Path(yml_path).parent)
        items.append(data)
    return items


def seed(items):
    """Bulk insert all items in a single transaction."""
    conn = get_connection()
    wait_for_wp_tables(conn)
    cur = conn.cursor()

    # Pre-create all category terms
    term_cache = {}
    for item in items:
        cat = item["_kategorie"]
        if cat not in term_cache:
            term_cache[cat] = get_or_create_term(cur, cat)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0

    for item in items:
        nazev = item["nazev"]

        # Check if already exists
        cur.execute(
            "SELECT ID FROM wp_posts WHERE post_title = %s AND post_type = 'potravina' AND post_status = 'publish'",
            (nazev,),
        )
        if cur.fetchone():
            print(f"  [skip] {nazev}")
            continue

        # Create post
        slug = slugify(nazev)
        cur.execute(
            "INSERT INTO wp_posts (post_author, post_date, post_date_gmt, post_content, "
            "post_title, post_excerpt, post_status, comment_status, ping_status, "
            "post_name, to_ping, pinged, post_content_filtered, "
            "post_modified, post_modified_gmt, guid, post_type) "
            "VALUES (1, %s, %s, '', %s, '', 'publish', 'closed', 'closed', "
            "%s, '', '', '', %s, %s, '', 'potravina')",
            (now_str, now_str, nazev, slug, now_str, now_str),
        )
        post_id = cur.lastrowid

        # Update guid
        cur.execute(
            "UPDATE wp_posts SET guid = %s WHERE ID = %s",
            (f"?p={post_id}", post_id),
        )

        # Meta values — batch insert
        meta_rows = []
        nutrice = item.get("nutrice", {})
        for key in NUTRI_KEYS:
            val = nutrice.get(key)
            if val is not None:
                meta_rows.append((post_id, f"_jidlo_{key}", str(val)))

        if item.get("znacka"):
            meta_rows.append((post_id, "_jidlo_znacka", item["znacka"]))
        if item.get("popis"):
            meta_rows.append((post_id, "_jidlo_popis", item["popis"]))

        # Image
        img_rel = item.get("obrazek")
        if img_rel:
            img_path = os.path.join(item["_dir"], img_rel)
            att_id = import_image(cur, img_path, post_id)
            if att_id:
                meta_rows.append((post_id, "_thumbnail_id", str(att_id)))

        if meta_rows:
            cur.executemany(
                "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s)",
                meta_rows,
            )

        # Category term relationship
        tt_id = term_cache[item["_kategorie"]]
        cur.execute(
            "INSERT IGNORE INTO wp_term_relationships (object_id, term_taxonomy_id) VALUES (%s, %s)",
            (post_id, tt_id),
        )
        cur.execute(
            "UPDATE wp_term_taxonomy SET count = count + 1 WHERE term_taxonomy_id = %s",
            (tt_id,),
        )

        count += 1
        print(f"  [{count}] {nazev}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nSeeding done! Created {count} food items.")


if __name__ == "__main__":
    items = load_items()
    if not items:
        print("No YAML files found in data/")
        sys.exit(0)
    print(f"Found {len(items)} items to seed.")
    seed(items)
