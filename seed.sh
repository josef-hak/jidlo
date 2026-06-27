#!/bin/sh
# Seed script — reads data/potraviny.yml and creates food items via WP-CLI
# Run inside wp-setup container after theme activation

DATA_DIR="/tmp/data"
COUNT=0

echo "Seeding food items..."

# Simple YAML parser — reads one item at a time
NAZEV="" ZNACKA="" POPIS="" KATEGORIE="" OBRAZEK=""
E_KJ="" E_KCAL="" TUKY="" NMK="" SACH="" CUKRY="" VLAK="" BILK="" SUL=""
IN_NUTRICE=0

save_item() {
    [ -z "$NAZEV" ] && return

    POST_ID=$(wp post create --post_type=potravina --post_title="$NAZEV" --post_status=publish --porcelain --allow-root)

    [ -n "$E_KJ" ]   && wp post meta update $POST_ID _jidlo_energie_kj "$E_KJ" --allow-root
    [ -n "$E_KCAL" ]  && wp post meta update $POST_ID _jidlo_energie_kcal "$E_KCAL" --allow-root
    [ -n "$TUKY" ]    && wp post meta update $POST_ID _jidlo_tuky "$TUKY" --allow-root
    [ -n "$NMK" ]     && wp post meta update $POST_ID _jidlo_nasycene_mk "$NMK" --allow-root
    [ -n "$SACH" ]    && wp post meta update $POST_ID _jidlo_sacharidy "$SACH" --allow-root
    [ -n "$CUKRY" ]   && wp post meta update $POST_ID _jidlo_cukry "$CUKRY" --allow-root
    [ -n "$VLAK" ]    && wp post meta update $POST_ID _jidlo_vlaknina "$VLAK" --allow-root
    [ -n "$BILK" ]    && wp post meta update $POST_ID _jidlo_bilkoviny "$BILK" --allow-root
    [ -n "$SUL" ]     && wp post meta update $POST_ID _jidlo_sul "$SUL" --allow-root
    [ -n "$ZNACKA" ]  && wp post meta update $POST_ID _jidlo_znacka "$ZNACKA" --allow-root
    [ -n "$POPIS" ]   && wp post meta update $POST_ID _jidlo_popis "$POPIS" --allow-root
    [ -n "$KATEGORIE" ] && wp post term set $POST_ID kategorie_potravin "$KATEGORIE" --allow-root

    if [ -n "$OBRAZEK" ] && [ -f "$DATA_DIR/$OBRAZEK" ]; then
        ATT_ID=$(wp media import "$DATA_DIR/$OBRAZEK" --porcelain --allow-root 2>/dev/null)
        [ -n "$ATT_ID" ] && wp post meta update $POST_ID _thumbnail_id "$ATT_ID" --allow-root
    fi

    COUNT=$((COUNT + 1))
    echo "  [$COUNT] $NAZEV"

    NAZEV="" ZNACKA="" POPIS="" KATEGORIE="" OBRAZEK=""
    E_KJ="" E_KCAL="" TUKY="" NMK="" SACH="" CUKRY="" VLAK="" BILK="" SUL=""
    IN_NUTRICE=0
}

# Strip quotes helper
strip_q() { echo "$1" | sed 's/^"//;s/"$//'; }

while IFS= read -r line; do
    case "$line" in
        "- nazev:"*)
            save_item
            NAZEV=$(strip_q "${line#*: }")
            IN_NUTRICE=0
            ;;
        "  znacka:"*)   ZNACKA=$(strip_q "${line#*: }") ;;
        "  popis:"*)    POPIS=$(strip_q "${line#*: }") ;;
        "  kategorie:"*) KATEGORIE=$(strip_q "${line#*: }") ;;
        "  obrazek:"*)  OBRAZEK=$(strip_q "${line#*: }") ;;
        "  nutrice:")    IN_NUTRICE=1 ;;
        *)
            if [ "$IN_NUTRICE" = "1" ]; then
                key=$(echo "$line" | sed 's/^ *//;s/:.*//')
                val=$(echo "$line" | sed 's/^[^:]*: *//')
                case "$key" in
                    energie_kj)   E_KJ="$val" ;;
                    energie_kcal) E_KCAL="$val" ;;
                    tuky)         TUKY="$val" ;;
                    nasycene_mk)  NMK="$val" ;;
                    sacharidy)    SACH="$val" ;;
                    cukry)        CUKRY="$val" ;;
                    vlaknina)     VLAK="$val" ;;
                    bilkoviny)    BILK="$val" ;;
                    sul)          SUL="$val" ;;
                esac
            fi
            ;;
    esac
done < "$DATA_DIR/potraviny.yml"

# Save last item
save_item

echo "Seeding done! Created $COUNT food items."
