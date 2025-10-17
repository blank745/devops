# Инструкция по запуску проекта "Клуб любителей скачек"

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Создайте миграции:**
   ```bash
   python manage.py makemigrations
   ```

3. **Примените миграции:**
   ```bash
   python manage.py migrate
   ```

4. **Создайте суперпользователя:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Загрузите тестовые данные:**
   ```bash
   python init_data.py
   ```

6. **Запустите сервер:**
   ```bash
   python manage.py runserver
   ```
===========================================================

# Docker

1. **Установите docker и docker compose**

2. **Запуск**
   ```bash
   docker compose up --build
   ```

3. **Главные страницы**
   1. Web: localhost:8000
   2. Admin panel: localhost:8000/admin (admin / admin123)

4. **Последующий запуск**
   ```bash
   docker compose up
   ```
