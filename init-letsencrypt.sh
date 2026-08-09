#!/bin/bash

# ============================================================
# StudentAbroad — SSL Certificate Initialization Script
# ============================================================
# Цей скрипт виконується ОДИН раз при першому деплої на сервер.
# Він автоматично:
#   1. Завантажує рекомендовані TLS параметри
#   2. Створює тимчасовий (dummy) сертифікат для запуску Nginx
#   3. Запускає Nginx
#   4. Отримує справжній сертифікат від Let's Encrypt
#   5. Запускає міграції БД та збирає статику
#   6. Піднімає всі контейнери
#
# ВАЖЛИВО: Перед запуском на бойовому сервері змініть staging=0
# ============================================================

set -e

# --- Визначення команди Docker Compose (V1 або V2) ---
if command -v docker-compose &> /dev/null; then
  DC="docker-compose"
elif docker compose version &> /dev/null; then
  DC="docker compose"
else
  echo "Error: Neither 'docker-compose' nor 'docker compose' is installed." >&2
  exit 1
fi

echo "Using: $DC"

# --- Конфігурація ---
domains=(studentabroad.org.ua www.studentabroad.org.ua)
rsa_key_size=4096
data_path="./certbot"
email="maksim.korcinskij@gmail.com" # Ваш email для Let's Encrypt сповіщень
staging=1 # УВАГА: Змініть на 0 для отримання справжнього сертифікату!

# --- Перевірка існуючих сертифікатів ---
if [ -d "$data_path/conf/live/${domains[0]}" ]; then
  read -p "Existing data found for ${domains[0]}. Continue and replace existing certificate? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

# --- Крок 1: Завантаження рекомендованих TLS параметрів ---
if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

# --- Крок 2: Створення тимчасового (dummy) сертифікату ---
echo "### Creating dummy certificate for ${domains[0]} ..."
path="/etc/letsencrypt/live/${domains[0]}"
mkdir -p "$data_path/conf/live/${domains[0]}"
$DC -f docker-compose.prod.yml run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=localhost'" certbot
echo

# --- Крок 3: Запуск Nginx з тимчасовим сертифікатом ---
echo "### Starting nginx ..."
$DC -f docker-compose.prod.yml up --force-recreate -d nginx
echo

# --- Крок 4: Видалення тимчасового сертифікату ---
echo "### Deleting dummy certificate for ${domains[0]} ..."
$DC -f docker-compose.prod.yml run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/${domains[0]} && \
  rm -Rf /etc/letsencrypt/archive/${domains[0]} && \
  rm -Rf /etc/letsencrypt/renewal/${domains[0]}.conf" certbot
echo

# --- Крок 5: Отримання справжнього сертифікату від Let's Encrypt ---
echo "### Requesting Let's Encrypt certificate for ${domains[*]} ..."

# Формуємо аргументи -d для кожного домену
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Визначаємо аргумент для email
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Визначаємо staging режим
staging_arg=""
if [ $staging != "0" ]; then
  staging_arg="--staging"
  echo "  (STAGING MODE — тестовий сертифікат, не для продакшну)"
fi

$DC -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot
echo

# --- Крок 6: Перезавантаження Nginx з новим сертифікатом ---
echo "### Reloading nginx with real certificate ..."
$DC -f docker-compose.prod.yml exec nginx nginx -s reload
echo

# --- Крок 7: Запуск міграцій бази даних ---
echo "### Running database migrations ..."
$DC -f docker-compose.prod.yml run --rm web python manage.py migrate
echo

# --- Крок 8: Збір статичних файлів ---
echo "### Collecting static files ..."
$DC -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput
echo

# --- Крок 9: Запуск УСІХ контейнерів ---
echo "### Starting all services ..."
$DC -f docker-compose.prod.yml up -d
echo

echo "============================================================"
echo "  ✅ Initialization complete!"
echo ""
if [ $staging != "0" ]; then
  echo "  ⚠️  УВАГА: Ви використали STAGING сертифікат (тестовий)."
  echo "  Для бойового сертифікату:"
  echo "    1. Змініть staging=0 у цьому скрипті"
  echo "    2. Запустіть скрипт ще раз: sudo ./init-letsencrypt.sh"
else
  echo "  🔒 Бойовий SSL сертифікат успішно встановлено!"
fi
echo ""
echo "  Ваш сайт: https://${domains[0]}"
echo "============================================================"
