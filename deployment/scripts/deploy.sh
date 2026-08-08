#!/bin/bash
# ============================================================
# Deploy Script — StudentAbroad
# ============================================================
# Запускати на VPS для оновлення проєкту:
#   bash deployment/scripts/deploy.sh
# ============================================================
set -euo pipefail

# ===== Конфігурація =====
PROJECT_ROOT="/home/studentabroad/app/StudentAbroadProject"
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${BACKEND_DIR}/venv"
BRANCH="main"

# ===== Кольори для виводу =====
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ===== Перевірки =====
if [ ! -d "$PROJECT_ROOT" ]; then
    log_error "Project directory not found: $PROJECT_ROOT"
    exit 1
fi

cd "$PROJECT_ROOT"

# ===== 1. Pull latest code =====
log_info "📥 Pulling latest code from ${BRANCH}..."
git pull origin "$BRANCH"

# ===== 2. Activate venv & install dependencies =====
log_info "📦 Installing dependencies..."
source "${VENV_DIR}/bin/activate"
pip install -r requirements.txt --quiet

# ===== 3. Collect static files =====
log_info "📂 Collecting static files..."
cd "$BACKEND_DIR"
python manage.py collectstatic --noinput --clear

# ===== 4. Run migrations =====
log_info "🗃️  Running database migrations..."
python manage.py migrate --noinput

# ===== 5. Restart services =====
log_info "🔄 Restarting Gunicorn..."
sudo systemctl restart studentabroad

log_info "🔄 Restarting Nginx..."
sudo systemctl restart nginx

# ===== 6. Health check =====
log_info "🏥 Running health check..."
sleep 3

if sudo systemctl is-active --quiet studentabroad; then
    log_info "✅ Gunicorn is running"
else
    log_error "❌ Gunicorn failed to start!"
    sudo journalctl -u studentabroad --no-pager -n 20
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    log_info "✅ Nginx is running"
else
    log_error "❌ Nginx failed to start!"
    sudo nginx -t
    exit 1
fi

log_info "✅ Deployment complete! 🚀"
echo ""
echo "Check logs:"
echo "  sudo journalctl -u studentabroad -f"
echo "  tail -f ${BACKEND_DIR}/logs/django.log"
