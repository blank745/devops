#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - continuing"

# Run database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create admin user for Django admin panel
echo "Creating admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
"

# Initialize test data
echo "Initializing test data..."
python init_data.py

python manage.py test racing.tests 

# Start the Django development server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
