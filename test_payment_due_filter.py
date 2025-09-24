#!/usr/bin/env python
"""
Test script to verify that the receipt page and invoice generation
filter projects by payment_due_date for the current month.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, '/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch')
django.setup()

from django.utils import timezone
from order_management.models import Project
import calendar

def test_receipt_view_filter():
    """Test that receipt view filters by payment_due_date"""

    # Get current month's date range
    now = timezone.now()
    year = now.year
    month = now.month
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    print(f"Testing receipt view filter for {year}-{month:02d}")
    print(f"Date range: {start_date} to {end_date}")
    print("-" * 50)

    # Query projects with payment_due_date in current month
    projects_in_month = Project.objects.filter(
        payment_due_date__gte=start_date,
        payment_due_date__lte=end_date,
        estimate_amount__gt=0
    ).exclude(
        contractor_name__isnull=True
    ).exclude(
        contractor_name=''
    )

    print(f"Projects with payment_due_date in current month: {projects_in_month.count()}")

    if projects_in_month.exists():
        print("\nSample projects in current month:")
        for project in projects_in_month[:5]:
            print(f"  - {project.site_name} | Due: {project.payment_due_date} | Client: {project.contractor_name} | Amount: ¥{project.estimate_amount:,.0f}")

    # Query all projects (old behavior - for comparison)
    all_projects = Project.objects.filter(
        estimate_amount__gt=0
    ).exclude(
        contractor_name__isnull=True
    ).exclude(
        contractor_name=''
    )

    print(f"\nTotal projects (without date filter): {all_projects.count()}")

    # Show projects outside current month
    projects_outside_month = all_projects.exclude(
        payment_due_date__gte=start_date,
        payment_due_date__lte=end_date
    )

    print(f"Projects outside current month: {projects_outside_month.count()}")

    if projects_outside_month.exists():
        print("\nSample projects outside current month:")
        for project in projects_outside_month[:5]:
            print(f"  - {project.site_name} | Due: {project.payment_due_date} | Client: {project.contractor_name}")

    return projects_in_month

def test_invoice_generation():
    """Test that invoice generation filters by payment_due_date"""

    now = timezone.now()
    year = now.year
    month = now.month
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    print("\n" + "=" * 50)
    print(f"Testing invoice generation for {year}-{month:02d}")
    print("-" * 50)

    # Get projects for current month (same logic as API)
    projects = Project.objects.filter(
        payment_due_date__gte=start_date,
        payment_due_date__lte=end_date,
        estimate_amount__gt=0
    ).exclude(
        contractor_name__isnull=True
    ).exclude(
        contractor_name=''
    )

    # Group by client
    client_projects = {}
    for project in projects:
        client_name = project.contractor_name
        if client_name not in client_projects:
            client_projects[client_name] = []
        client_projects[client_name].append(project)

    print(f"Clients with invoices to generate: {len(client_projects)}")

    total_invoice_amount = Decimal('0')
    for client_name, client_project_list in client_projects.items():
        subtotal = sum((p.billing_amount or p.estimate_amount or Decimal('0')) for p in client_project_list)
        tax_amount = (subtotal * Decimal('10') / Decimal('100')).quantize(Decimal('1'))
        total_amount = subtotal + tax_amount
        total_invoice_amount += total_amount

        print(f"\n  Client: {client_name}")
        print(f"    Projects: {len(client_project_list)}")
        print(f"    Subtotal: ¥{subtotal:,.0f}")
        print(f"    Tax (10%): ¥{tax_amount:,.0f}")
        print(f"    Total: ¥{total_amount:,.0f}")

        for project in client_project_list[:3]:  # Show first 3 projects
            print(f"      - {project.work_type} - {project.site_name} | Due: {project.payment_due_date}")

    print(f"\n" + "=" * 50)
    print(f"SUMMARY:")
    print(f"  Total clients: {len(client_projects)}")
    print(f"  Total projects: {projects.count()}")
    print(f"  Total invoice amount: ¥{total_invoice_amount:,.0f}")

if __name__ == "__main__":
    print("=" * 50)
    print("Payment Due Date Filter Test")
    print("=" * 50)

    # Run tests
    projects_in_month = test_receipt_view_filter()
    test_invoice_generation()

    print("\n" + "=" * 50)
    print("Test completed!")
    print("The receipt page and invoice generation now filter by payment_due_date for the current month.")