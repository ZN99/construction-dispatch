#!/usr/bin/env python
"""
Debug why current month (September 2025) shows 0 revenue in accounting dashboard
"""

import os
import sys
import django
from datetime import datetime
from decimal import Decimal

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, '/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch')
django.setup()

from django.utils import timezone
from order_management.models import Project

def check_current_month_issue():
    """Debug current month revenue calculation"""
    print("=" * 60)
    print("DEBUGGING CURRENT MONTH (SEPTEMBER 2025) REVENUE")
    print("=" * 60)

    current_date = timezone.now().date()
    current_year = current_date.year  # 2025
    current_month = current_date.month  # 9

    print(f"Current Date: {current_date}")
    print(f"Current Year: {current_year}")
    print(f"Current Month: {current_month}")

    # Check all projects with September 2025 payment due dates
    september_projects = Project.objects.filter(
        payment_due_date__year=current_year,
        payment_due_date__month=current_month,
        estimate_amount__gt=0
    )

    print(f"\nSeptember 2025 Projects (payment_due_date): {september_projects.count()}")

    order_status_counts = {}
    for project in september_projects:
        status = project.order_status
        order_status_counts[status] = order_status_counts.get(status, 0) + 1

    print("Order Status Distribution:")
    for status, count in order_status_counts.items():
        print(f"  {status}: {count}件")

    # Check projects that would be counted in accounting logic
    accounting_projects = september_projects.filter(order_status='受注')
    print(f"\n'受注' status projects in September: {accounting_projects.count()}")

    # Show work completion status
    work_completed = september_projects.filter(work_end_completed=True)
    print(f"Work completed projects in September: {work_completed.count()}")

    # Check projects with billing_amount
    with_billing = september_projects.filter(billing_amount__gt=0)
    with_estimate_only = september_projects.filter(billing_amount__isnull=True, estimate_amount__gt=0)

    print(f"\nBilling Amount Status:")
    print(f"  With billing_amount: {with_billing.count()}")
    print(f"  With estimate_amount only: {with_estimate_only.count()}")

    # Simulate accounting logic
    revenue_total = Decimal('0')
    for project in september_projects:
        if project.order_status == '受注' and project.billing_amount and project.billing_amount > 0:
            # This is what accounting dashboard looks for
            revenue_date = project.work_end_date or project.payment_due_date
            if revenue_date and revenue_date.year == current_year and revenue_date.month == current_month:
                revenue_total += project.billing_amount
                print(f"  Would count: {project.site_name} - ¥{project.billing_amount}")

    print(f"\nAccounting Logic Revenue: ¥{revenue_total:,.0f}")

    if revenue_total == 0:
        print("\n🔍 ISSUE IDENTIFIED:")
        print("  - No projects have order_status='受注' AND billing_amount > 0")
        print("  - Need to either:")
        print("    1. Update project order_status to '受注'")
        print("    2. Set billing_amount for September projects")
        print("    3. Modify accounting logic to use estimate_amount")

def show_sample_september_projects():
    """Show details of some September projects"""
    print("\n" + "=" * 60)
    print("SAMPLE SEPTEMBER 2025 PROJECTS")
    print("=" * 60)

    september_projects = Project.objects.filter(
        payment_due_date__year=2025,
        payment_due_date__month=9,
        estimate_amount__gt=0
    )[:5]

    for project in september_projects:
        print(f"\nProject: {project.site_name}")
        print(f"  Order Status: {project.order_status}")
        print(f"  Estimate Amount: ¥{project.estimate_amount:,.0f}")
        print(f"  Billing Amount: {project.billing_amount or 'None'}")
        print(f"  Work End Date: {project.work_end_date or 'None'}")
        print(f"  Work End Completed: {project.work_end_completed}")
        print(f"  Payment Due Date: {project.payment_due_date}")

if __name__ == "__main__":
    check_current_month_issue()
    show_sample_september_projects()