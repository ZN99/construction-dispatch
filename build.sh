#!/bin/bash

# Build script for Render deployment

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Creating initial data..."
python initial_data.py

echo "Creating production users..."
python create_production_users.py

echo "Build completed successfully!"