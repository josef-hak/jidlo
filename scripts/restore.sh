#!/bin/bash
# Obnovení ze zálohy
# Použití: ./scripts/restore.sh jidlo-backup-2026-06-27_120000.tar.gz

set -e

if [ -z "$1" ]; then
    echo "Použití: $0 <backup-soubor.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
BACKUP_DIR="/tmp/jidlo-restore"

rm -rf "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"

echo "Rozbaluji archiv..."
tar -xzf "${BACKUP_FILE}" -C "${BACKUP_DIR}" --strip-components=1

echo "Importuji databázi..."
docker compose exec -T db mysql -u wordpress -pwordpress wordpress < "${BACKUP_DIR}/database.sql"

if [ -d "${BACKUP_DIR}/uploads" ]; then
    echo "Kopíruji nahrané soubory..."
    docker compose cp "${BACKUP_DIR}/uploads" wordpress:/var/www/html/wp-content/uploads
fi

rm -rf "${BACKUP_DIR}"

echo "Obnovení dokončeno."
