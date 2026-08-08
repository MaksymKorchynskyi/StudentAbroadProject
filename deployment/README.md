# StudentAbroad — VPS Deployment Guide

## Вимоги до VPS (OVHcloud)

- **OS:** Ubuntu 22.04 / 24.04 LTS
- **Мінімум:** 2 vCPU, 4 GB RAM, 80 GB SSD
- **Рекомендація:** OVHcloud VPS Essential або вище

## Швидкий старт

### 1. Налаштування сервера

```bash
# Оновити систему
sudo apt update && sudo apt upgrade -y

# Встановити залежності
sudo apt install -y python3 python3-venv python3-pip \
    postgresql postgresql-contrib nginx certbot python3-certbot-nginx \
    git ufw

# Налаштувати firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Створити системного користувача
sudo adduser studentabroad --disabled-password
```

### 2. PostgreSQL

```bash
sudo -u postgres psql << 'SQL'
CREATE DATABASE studentabroad_db;
CREATE USER studentabroad_user WITH PASSWORD 'STRONG_PASSWORD_HERE';
ALTER ROLE studentabroad_user SET client_encoding TO 'utf8';
ALTER ROLE studentabroad_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE studentabroad_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE studentabroad_db TO studentabroad_user;
\q
SQL
```

### 3. Деплой проєкту

```bash
sudo su - studentabroad
git clone <REPO_URL> app
cd app/StudentAbroadProject

# Створити .env з .env.example
cp .env.example .env
# ⚠️ Заповнити .env продакшн-значеннями!
nano .env

# Python venv
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt

# Django setup
mkdir -p logs cache
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### 4. Systemd + Nginx

```bash
# Systemd service
sudo cp deployment/systemd/studentabroad.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start studentabroad
sudo systemctl enable studentabroad

# Nginx
sudo cp deployment/nginx/studentabroad.conf /etc/nginx/sites-available/studentabroad
sudo ln -s /etc/nginx/sites-available/studentabroad /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Видалити дефолтний сайт
sudo nginx -t && sudo systemctl restart nginx
```

### 5. SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d studentabroad.org.ua -d www.studentabroad.org.ua
```

### 6. Автоматичні бекапи

```bash
sudo mkdir -p /backups/studentabroad
sudo chown studentabroad:studentabroad /backups/studentabroad

# Додати в cron
(crontab -l 2>/dev/null; echo "0 3 * * * /home/studentabroad/app/StudentAbroadProject/deployment/scripts/backup.sh >> /var/log/studentabroad-backup.log 2>&1") | crontab -
```

## Оновлення (деплой нової версії)

```bash
cd /home/studentabroad/app/StudentAbroadProject
bash deployment/scripts/deploy.sh
```

## Корисні команди

```bash
# Логи
sudo journalctl -u studentabroad -f
tail -f backend/logs/django.log

# Статус
sudo systemctl status studentabroad
sudo systemctl status nginx

# Перезапуск
sudo systemctl restart studentabroad
sudo systemctl restart nginx
```
