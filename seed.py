#!/usr/bin/env python3
"""Seed food items from data/ YAML files directly into WordPress DB.

Connects to MariaDB via env vars and bulk-inserts all items in a single transaction.
"""

import glob
import os
import re
import shutil
import sys
import time
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

MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def get_connection():
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


def wait_for_wp_filesystem():
    """Wait until WordPress has initialized wp-content directory."""
    wp_content = os.path.join(WP_UPLOADS, "..")
    for attempt in range(60):
        if os.path.isdir(wp_content):
            return
        print(f"  Waiting for wp-content... ({attempt + 1})")
        time.sleep(3)
    raise RuntimeError("wp-content not ready after 3 minutes")


def import_image(cur, image_path, post_id, now_str):
    """Copy image to wp-content/uploads and create attachment post. Returns attachment ID."""
    if not os.path.isfile(image_path):
        print(f"    [img] Not found: {image_path}")
        return None

    ext = os.path.splitext(image_path)[1].lower()
    mime = MIME_MAP.get(ext, "image/jpeg")

    now = datetime.now()
    upload_subdir = now.strftime("%Y/%m")
    upload_dir = os.path.join(WP_UPLOADS, upload_subdir)
    os.makedirs(upload_dir, exist_ok=True)

    filename = os.path.basename(image_path)
    dest = os.path.join(upload_dir, filename)
    if os.path.exists(dest):
        base, fext = os.path.splitext(filename)
        filename = f"{base}-{post_id}{fext}"
        dest = os.path.join(upload_dir, filename)

    shutil.copy2(image_path, dest)
    print(f"    [img] {os.path.basename(image_path)} -> {dest}")
    rel_path = f"{upload_subdir}/{filename}"

    cur.execute(
        "INSERT INTO wp_posts (post_author, post_date, post_date_gmt, post_content, "
        "post_title, post_excerpt, post_status, comment_status, ping_status, "
        "post_name, to_ping, pinged, post_content_filtered, "
        "post_modified, post_modified_gmt, post_parent, guid, "
        "post_type, post_mime_type) "
        "VALUES (1, %s, %s, '', %s, '', 'inherit', 'open', 'closed', "
        "%s, '', '', '', %s, %s, %s, %s, 'attachment', %s)",
        (now_str, now_str, filename, filename, now_str, now_str, post_id,
         f"/wp-content/uploads/{rel_path}", mime),
    )
    att_id = cur.lastrowid

    cur.execute(
        "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, '_wp_attached_file', %s)",
        (att_id, rel_path),
    )
    return att_id


def load_items():
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
    conn = get_connection()
    wait_for_wp_tables(conn)
    wait_for_wp_filesystem()
    cur = conn.cursor()

    term_cache = {}
    for item in items:
        cat = item["_kategorie"]
        if cat not in term_cache:
            term_cache[cat] = get_or_create_term(cur, cat)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0

    for item in items:
        nazev = item["nazev"]

        cur.execute(
            "SELECT ID FROM wp_posts WHERE post_title = %s AND post_type = 'potravina' AND post_status = 'publish'",
            (nazev,),
        )
        if cur.fetchone():
            print(f"  [skip] {nazev}")
            continue

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

        cur.execute(
            "UPDATE wp_posts SET guid = %s WHERE ID = %s",
            (f"?p={post_id}", post_id),
        )

        # Meta values
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
        if item.get("slozeni"):
            meta_rows.append((post_id, "_jidlo_slozeni", item["slozeni"]))

        # Images — support both "obrazek" (legacy string) and "obrazky" (list)
        img_list = item.get("obrazky") or []
        if not img_list and item.get("obrazek"):
            img_list = [item["obrazek"]]

        att_ids = []
        for img_rel in img_list:
            img_path = os.path.join(item["_dir"], img_rel)
            att_id = import_image(cur, img_path, post_id, now_str)
            if att_id:
                att_ids.append(att_id)

        if att_ids:
            # First image = thumbnail
            meta_rows.append((post_id, "_thumbnail_id", str(att_ids[0])))
            # All images as gallery (comma-separated IDs)
            meta_rows.append((post_id, "_jidlo_gallery", ",".join(str(a) for a in att_ids)))

        if meta_rows:
            cur.executemany(
                "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s)",
                meta_rows,
            )

        # Category
        tt_id = term_cache[item["_kategorie"]]
        cur.execute(
            "INSERT IGNORE INTO wp_term_relationships (object_id, term_taxonomy_id) VALUES (%s, %s)",
            (post_id, tt_id),
        )

        count += 1
        print(f"  [{count}] {nazev}")

    # Fix term counts
    for tt_id in term_cache.values():
        cur.execute(
            "UPDATE wp_term_taxonomy SET count = "
            "(SELECT COUNT(*) FROM wp_term_relationships WHERE term_taxonomy_id = %s) "
            "WHERE term_taxonomy_id = %s",
            (tt_id, tt_id),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nSeeding done! Created {count} food items.")


def purge():
    """Delete all potravina posts and their attachments."""
    conn = get_connection()
    wait_for_wp_tables(conn)
    cur = conn.cursor()

    cur.execute("SELECT ID FROM wp_posts WHERE post_type = 'potravina'")
    post_ids = [row[0] for row in cur.fetchall()]

    if not post_ids:
        print("Nothing to purge.")
        conn.close()
        return

    placeholders = ",".join(["%s"] * len(post_ids))

    # Delete attachments linked to these posts
    cur.execute(f"SELECT ID FROM wp_posts WHERE post_type = 'attachment' AND post_parent IN ({placeholders})", post_ids)
    att_ids = [row[0] for row in cur.fetchall()]
    all_ids = post_ids + att_ids

    ph_all = ",".join(["%s"] * len(all_ids))
    cur.execute(f"DELETE FROM wp_postmeta WHERE post_id IN ({ph_all})", all_ids)
    cur.execute(f"DELETE FROM wp_term_relationships WHERE object_id IN ({ph_all})", all_ids)
    cur.execute(f"DELETE FROM wp_posts WHERE ID IN ({ph_all})", all_ids)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Purged {len(post_ids)} food items + {len(att_ids)} attachments.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Delete all existing items before seeding")
    args = parser.parse_args()

    if args.force:
        purge()

    items = load_items()
    if not items:
        print("No YAML files found in data/")
        sys.exit(0)
    print(f"Found {len(items)} items to seed.")
    seed(items)
