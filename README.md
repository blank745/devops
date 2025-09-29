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
