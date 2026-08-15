# Базовий образ Python (використовуємо slim для меншого розміру)
FROM python:3.12-slim

# Налаштування змінних оточення
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Встановлення робочої директорії
WORKDIR /app

# Встановлення системних залежностей для PostgreSQL та інших пакетів
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копіювання файлу залежностей (використовуємо контекст збірки з кореня проєкту)
COPY requirements.txt /app/

# Встановлення Python залежностей
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копіювання коду проєкту
COPY backend /app/backend

# Налаштування робочої директорії на рівень, де знаходиться manage.py
WORKDIR /app/backend

# Створити директорії для кешу та логів (потрібні на production)
RUN mkdir -p /app/backend/cache /app/backend/logs

# Команда за замовчуванням (буде перевизначена в docker-compose для продакшену)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
