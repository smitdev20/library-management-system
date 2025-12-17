#!/bin/bash
# Start script for Railway deployment
# Sets default PORT if not provided by Railway

export PORT=${PORT:-8000}

# Run migrations and setup
python manage.py migrate --noinput
python manage.py setup_groups

# Seed books (only creates if database is empty)
python manage.py seed_books

# Create admin user (only if not exists)
python manage.py shell -c "
from apps.accounts.models import User
from django.contrib.auth.models import Group

if not User.objects.filter(email='admin@gmail.com').exists():
    admin = User.objects.create_superuser(
        email='admin@gmail.com',
        password='Admin@10',
        username='admin',
        first_name='Admin',
        last_name='User'
    )
    admin_group, _ = Group.objects.get_or_create(name='Administrators')
    admin.groups.add(admin_group)
    print('✅ Admin user created: admin@gmail.com')
else:
    print('Admin user already exists (skipping creation)')
"

# Start Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
