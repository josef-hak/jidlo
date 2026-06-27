#!/bin/sh
# Seed script — creates sample food items via WP-CLI
# Run inside wp-setup container after theme activation

echo "Seeding food items..."

# --- Jogurt Hollandia Bio selský bílý ---
POST_ID=$(wp post create --post_type=potravina --post_title="Jogurt Hollandia Bio selský bílý" --post_status=publish --porcelain --allow-root)
wp post meta update $POST_ID _jidlo_energie_kj 265 --allow-root
wp post meta update $POST_ID _jidlo_energie_kcal 63 --allow-root
wp post meta update $POST_ID _jidlo_tuky 4 --allow-root
wp post meta update $POST_ID _jidlo_nasycene_mk 2 --allow-root
wp post meta update $POST_ID _jidlo_sacharidy 4 --allow-root
wp post meta update $POST_ID _jidlo_cukry 4 --allow-root
wp post meta update $POST_ID _jidlo_vlaknina 0 --allow-root
wp post meta update $POST_ID _jidlo_bilkoviny 4 --allow-root
wp post meta update $POST_ID _jidlo_sul 0.1 --allow-root
wp post meta update $POST_ID _jidlo_znacka "Hollandia" --allow-root
wp post term set $POST_ID kategorie_potravin "Mléčné výrobky" --allow-root

# --- Šunka nejvyšší jakosti 95% Pikok Pure ---
POST_ID=$(wp post create --post_type=potravina --post_title="Šunka nejvyšší jakosti 95% Pikok Pure" --post_status=publish --porcelain --allow-root)
wp post meta update $POST_ID _jidlo_energie_kj 456 --allow-root
wp post meta update $POST_ID _jidlo_energie_kcal 109 --allow-root
wp post meta update $POST_ID _jidlo_tuky 3.2 --allow-root
wp post meta update $POST_ID _jidlo_nasycene_mk 0.8 --allow-root
wp post meta update $POST_ID _jidlo_sacharidy 0.1 --allow-root
wp post meta update $POST_ID _jidlo_cukry 0.1 --allow-root
wp post meta update $POST_ID _jidlo_vlaknina 0 --allow-root
wp post meta update $POST_ID _jidlo_bilkoviny 18.9 --allow-root
wp post meta update $POST_ID _jidlo_sul 1.9 --allow-root
wp post meta update $POST_ID _jidlo_znacka "Pikok Pure (Lidl)" --allow-root
wp post term set $POST_ID kategorie_potravin "Maso a uzeniny" --allow-root

echo "Seeding done! Created 2 food items."
