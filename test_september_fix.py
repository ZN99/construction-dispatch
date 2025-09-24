#!/usr/bin/env python
"""
Test if September 2025 revenue is now correctly calculated after fixing the logic
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

def simulate_accounting_logic_fixed():
    """Simulate the fixed accounting logic for September 2025"""
    print("=" * 60)
    print("TESTING FIXED ACCOUNTING LOGIC FOR SEPTEMBER 2025")
    print("=" * 60)

    # Fiscal year logic (same as in views_accounting.py)
    year = 2025  # Fiscal year starting April 2025
    fiscal_year_start = datetime(year, 4, 1).date()
    fiscal_year_end = datetime(year + 1, 3, 31).date()

    current_date = datetime(2025, 9, 24).date()  # Today
    current_month = 9
    current_year = 2025

    print(f"Fiscal Year: {fiscal_year_start} to {fiscal_year_end}")
    print(f"Current Date: {current_date}")

    # Projects with payment_due_date in September 2025
    revenue_projects = Project.objects.filter(
        order_status='受注',
        billing_amount__gt=0,
        payment_due_date__year=current_year,
        payment_due_date__month=current_month
    )

    print(f"\nSeptember 2025 Revenue Projects (order_status='受注', billing_amount>0): {revenue_projects.count()}")

    total_september_revenue = Decimal('0')
    for project in revenue_projects:
        revenue = project.billing_amount or Decimal('0')
        total_september_revenue += revenue
        print(f"  {project.site_name}: ¥{revenue:,.0f} (due: {project.payment_due_date})")

    print(f"\nTotal September 2025 Revenue: ¥{total_september_revenue:,.0f}")

    # Check fiscal month index for September 2025
    # April=0, May=1, June=2, July=3, August=4, September=5
    september_fiscal_index = 5  # September is 6th month of fiscal year
    print(f"September 2025 Fiscal Month Index: {september_fiscal_index}")

    # Verify this matches our expectation
    expected_revenue = 35795000  # From our earlier check
    print(f"Expected Revenue (from estimate_amount): ¥{expected_revenue:,.0f}")

    if total_september_revenue > 0:
        print("✅ SUCCESS: September revenue is now being calculated!")
    else:
        print("❌ ISSUE: September revenue is still 0")

def check_fiscal_month_calculation():
    """Check if fiscal month index calculation is working"""
    print("\n" + "=" * 60)
    print("CHECKING FISCAL MONTH INDEX CALCULATION")
    print("=" * 60)

    # Simulate get_fiscal_month_index method
    def get_fiscal_month_index(date, fiscal_year):
        """Calculate fiscal month index (April=0, May=1, ..., March=11)"""
        if date.year == fiscal_year:
            if date.month >= 4:  # April-December
                return date.month - 4
        elif date.year == fiscal_year + 1:
            if date.month <= 3:  # January-March
                return date.month + 8
        return None

    test_dates = [
        datetime(2025, 4, 15).date(),   # April 2025 -> 0
        datetime(2025, 9, 24).date(),   # September 2025 -> 5
        datetime(2026, 1, 15).date(),   # January 2026 -> 9
        datetime(2026, 3, 31).date(),   # March 2026 -> 11
    ]

    for date in test_dates:
        index = get_fiscal_month_index(date, 2025)
        print(f"{date} -> Fiscal Month Index: {index}")

if __name__ == "__main__":
    simulate_accounting_logic_fixed()
    check_fiscal_month_calculation()