#!/usr/bin/env python
"""
Check actual project data to verify revenue for September and other months
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
import calendar

def check_monthly_revenue():
    """Check actual monthly revenue based on payment due dates"""
    print("=" * 60)
    print("MONTHLY REVENUE CHECK - Based on Payment Due Dates")
    print("=" * 60)

    monthly_revenue = {}
    total_revenue = 0

    for month in range(1, 13):
        # Get projects with payment due dates in this month
        projects = Project.objects.filter(
            payment_due_date__month=month,
            payment_due_date__year=2025,
            estimate_amount__gt=0
        )

        month_revenue = sum(p.estimate_amount or 0 for p in projects)
        monthly_revenue[month] = {
            'revenue': month_revenue,
            'projects': projects.count(),
            'month_name': calendar.month_name[month]
        }
        total_revenue += month_revenue

        print(f"{month:2d}月 ({calendar.month_name[month]:>9s}): ¥{month_revenue:>12,.0f} ({projects.count():>2d}件)")

    print("-" * 60)
    print(f"年間合計:                   ¥{total_revenue:>12,.0f}")

    # Find peak month
    peak_month = max(monthly_revenue.items(), key=lambda x: x[1]['revenue'])
    print(f"ピーク月: {peak_month[1]['month_name']} - ¥{peak_month[1]['revenue']:,.0f}")

    return monthly_revenue

def check_6_month_period():
    """Check 4-9月 period as shown in ultimate dashboard"""
    print("\n" + "=" * 60)
    print("4-9月 PERIOD CHECK (Ultimate Dashboard)")
    print("=" * 60)

    total_6month = 0
    for month in range(4, 10):  # 4月-9月
        projects = Project.objects.filter(
            payment_due_date__month=month,
            payment_due_date__year=2025,
            estimate_amount__gt=0
        )

        month_revenue = sum(p.estimate_amount or 0 for p in projects)
        total_6month += month_revenue

        print(f"{month:2d}月: ¥{month_revenue:>12,.0f} ({projects.count():>2d}件)")

    print("-" * 60)
    print(f"4-9月合計: ¥{total_6month:>12,.0f}")
    print(f"万円換算: {total_6month/10000:>10.0f}万円")

if __name__ == "__main__":
    monthly_data = check_monthly_revenue()
    check_6_month_period()

    # Show specific September data
    sept_data = monthly_data[9]
    print(f"\n🎯 9月詳細:")
    print(f"   売上: ¥{sept_data['revenue']:,.0f}")
    print(f"   案件数: {sept_data['projects']}件")
    print(f"   万円: {sept_data['revenue']/10000:.0f}万円")