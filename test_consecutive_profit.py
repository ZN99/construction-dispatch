#!/usr/bin/env python
"""
Test the consecutive profit months calculation
"""

import os
import sys
import django
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, '/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch')
django.setup()

from django.utils import timezone
from order_management.views_ultimate import UltimateDashboardView

def test_consecutive_profit():
    """Test the consecutive profit months calculation"""
    print("=" * 60)
    print("TESTING CONSECUTIVE PROFIT MONTHS CALCULATION")
    print("=" * 60)

    # Create a view instance and get annual performance data
    view = UltimateDashboardView()
    now = timezone.now()
    annual_performance = view.get_annual_performance(now.year)

    print(f"Fiscal year: {annual_performance['fiscal_year']}")
    print(f"Current date: {annual_performance['current_date']}")

    # Show monthly operating profit for recent months
    print("\nMonthly Operating Profit (recent months):")
    print("Year-Month | Operating Profit | Is Actual | Is Current")
    print("-" * 55)

    # Get months sorted by date (newest first)
    sorted_months = []
    for key, data in annual_performance['monthly_data'].items():
        if data['is_actual']:
            sorted_months.append(data)

    sorted_months.sort(key=lambda x: (x['year'], x['month']), reverse=True)

    for month_data in sorted_months[:8]:  # Show last 8 months
        profit = month_data['operating_profit']
        status = "黒字" if profit > 0 else "赤字" if profit < 0 else "収支0"
        print(f"{month_data['year']}-{month_data['month']:02d}   | ¥{profit:>12,.0f} | {'Yes':9s} | {'Yes' if month_data['is_current'] else 'No':10s} ({status})")

    # Show consecutive profit months
    consecutive = annual_performance.get('consecutive_profit_months', 0)
    print(f"\n✅ Consecutive profit months: {consecutive}")

    if consecutive > 0:
        print(f"🎉 {consecutive}ヶ月連続黒字")
    else:
        print("📉 連続黒字記録なし（前月は赤字または収支0）")

    return consecutive

if __name__ == "__main__":
    test_consecutive_profit()