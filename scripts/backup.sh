#!/bin/bash
# Záloha databáze + nahraných fotek
# Použití: ./scripts/backup.sh
# Výstup: jidlo-backup-YYYY-MM-DD_HHMMSS.tar.gz

set -e

TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_NAME="jidlo-backup-${TIMESTAMP}"
BACKUP_DIR="/tmp/${BACKUP_NAME}"

mkdir -p "${BACKUP_DIR}"

echo "Exportuji databázi..."
docker compose exec -T db mysqldump -u wordpress -pwordpress wordpress > "${BACKUP_DIR}/database.sql"

echo "Kopíruji nahrané soubory..."
docker compose cp wordpress:/var/www/html/wp-content/uploads "${BACKUP_DIR}/uploads" 2>/dev/null || echo "Žádné uploads."

echo "Balím archiv..."
tar -czf "${BACKUP_NAME}.tar.gz" -C /tmp "${BACKUP_NAME}"
rm -rf "${BACKUP_DIR}"

echo "Záloha uložena: ${BACKUP_NAME}.tar.gz"
