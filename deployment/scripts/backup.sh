#!/bin/bash
# ============================================================
# Backup Script — StudentAbroad
# ============================================================
# Додати в cron для щоденного бекапу:
#   crontab -e
#   0 3 * * * /home/studentabroad/app/StudentAbroadProject/deployment/scripts/backup.sh >> /var/log/studentabroad-backup.log 2>&1
# ============================================================
set -euo pipefail

# ===== Конфігурація =====
BACKUP_DIR="/backups/studentabroad"
DB_NAME="studentabroad_db"
MEDIA_DIR="/home/studentabroad/app/StudentAbroadProject/backend/media"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# ===== Кольори для виводу =====
GREEN='\033[0;32m'
NC='\033[0m'
log_info() { echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }

# ===== Створити директорії якщо не існують =====
mkdir -p "${BACKUP_DIR}/db"
mkdir -p "${BACKUP_DIR}/media"

# ===== 1. Бекап бази даних =====
log_info "🗃️  Creating database backup..."
pg_dump "$DB_NAME" | gzip > "${BACKUP_DIR}/db/db_${DATE}.sql.gz"
DB_SIZE=$(du -h "${BACKUP_DIR}/db/db_${DATE}.sql.gz" | cut -f1)
log_info "✅ Database backup created: db_${DATE}.sql.gz (${DB_SIZE})"

# ===== 2. Бекап медіа-файлів =====
if [ -d "$MEDIA_DIR" ] && [ "$(ls -A $MEDIA_DIR 2>/dev/null)" ]; then
    log_info "📁 Creating media backup..."
    tar -czf "${BACKUP_DIR}/media/media_${DATE}.tar.gz" -C "$(dirname $MEDIA_DIR)" "$(basename $MEDIA_DIR)"
    MEDIA_SIZE=$(du -h "${BACKUP_DIR}/media/media_${DATE}.tar.gz" | cut -f1)
    log_info "✅ Media backup created: media_${DATE}.tar.gz (${MEDIA_SIZE})"
else
    log_info "⏭️  No media files to backup"
fi

# ===== 3. Видалити старі бекапи =====
log_info "🧹 Cleaning backups older than ${RETENTION_DAYS} days..."
DELETED_COUNT=$(find "${BACKUP_DIR}" -type f -mtime +${RETENTION_DAYS} -print -delete | wc -l)
log_info "🗑️  Deleted ${DELETED_COUNT} old backup file(s)"

# ===== 4. Показати стан =====
log_info "📊 Backup directory usage:"
du -sh "${BACKUP_DIR}/db/" 2>/dev/null || echo "  DB backups: empty"
du -sh "${BACKUP_DIR}/media/" 2>/dev/null || echo "  Media backups: empty"

log_info "✅ Backup complete!"
