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

echo "Creating progress step templates..."
python populate_progress_steps.py

echo "Creating craftsman data..."
python craftsman_initial_data.py

echo "Creating rental restoration projects..."
python create_rental_restoration_data.py

echo "Creating contractor test data..."
python create_contractor_test_data.py

echo "Creating survey test data..."
python create_survey_test_data.py

echo "Creating sample surveys..."
python create_sample_surveys.py

echo "Creating material data..."
python create_material_data.py

echo "Creating payment data..."
python create_payment_data.py

echo "Creating survey data..."
python create_survey_data.py

echo "Build completed successfully!"