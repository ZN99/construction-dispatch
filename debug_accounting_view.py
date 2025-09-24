#!/usr/bin/env python
"""
Debug the accounting view with different month scenarios
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
from order_management.models import Project
from subcontract_management.models import Subcontract
import calendar

def debug_specific_month(year, month):
    """Debug a specific month's balance calculation"""
    print("=" * 60)
    print(f"DEBUGGING {year}-{month:02d}")
    print("=" * 60)

    # Month range
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    print(f"Date range: {start_date} to {end_date}")

    # Same query as the view - for receipt projects
    receipt_projects = Project.objects.filter(
        payment_due_date__range=[start_date, end_date],
        order_status='受注',
        billing_amount__gt=0
    ).exclude(contractor_name__isnull=True).exclude(contractor_name='')

    print(f"Receipt projects found: {receipt_projects.count()}")

    # Also check with different query for payment subcontracts
    payment_subcontracts = Subcontract.objects.filter(
        payment_date__range=[start_date, end_date],
        billed_amount__gt=0
    ).select_related('project', 'contractor', 'internal_worker')

    print(f"Payment subcontracts found: {payment_subcontracts.count()}")

    # Create transactions
    transactions = []

    # Receipt transactions
    for project in receipt_projects:
        amount = project.billing_amount or project.estimate_amount or 0
        if amount > 0:
            transactions.append({
                'date': project.payment_due_date or project.contract_date or start_date,
                'description': f'入金: {project.site_name[:25]}',
                'type': 'receipt',
                'amount': amount,
                'status': 'completed' if project.payment_status == 'executed' else 'pending',
            })

    # Payment transactions
    for subcontract in payment_subcontracts:
        amount = subcontract.billed_amount or subcontract.contract_amount or 0
        if amount > 0:
            payee = subcontract.contractor.name if subcontract.contractor else subcontract.internal_worker.name
            transactions.append({
                'date': subcontract.payment_date or start_date,
                'description': f'出金: {subcontract.site_name[:25]}',
                'type': 'payment',
                'amount': amount,
                'status': subcontract.payment_status,
            })

    print(f"Total transactions: {len(transactions)}")

    # Balance calculation (oldest to newest)
    transactions_for_calc = sorted(transactions, key=lambda x: x['date'])

    balance = 0
    for transaction in transactions_for_calc:
        if transaction['type'] == 'receipt':
            if transaction['status'] == 'completed':
                balance += transaction['amount']
        else:  # payment
            if transaction['status'] == 'paid':
                balance -= transaction['amount']
        transaction['balance'] = balance

    # Show recent transactions (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)

    print(f"\nRecent transactions (newest first):")
    print("Date       | Type    | Description                | Amount      | Status    | Balance")
    print("-" * 90)

    for transaction in transactions[:10]:
        print(f"{transaction['date']} | {transaction['type']:7s} | {transaction['description'][:25]:25s} | ¥{transaction['amount']:>9,.0f} | {transaction['status']:9s} | ¥{transaction['balance']:>9,.0f}")

    print(f"\nFinal balance: ¥{balance:,.0f}")

    # Summary stats
    total_receipts = sum(t['amount'] for t in transactions if t['type'] == 'receipt')
    completed_receipts = sum(t['amount'] for t in transactions if t['type'] == 'receipt' and t['status'] == 'completed')
    total_payments = sum(t['amount'] for t in transactions if t['type'] == 'payment')
    paid_payments = sum(t['amount'] for t in transactions if t['type'] == 'payment' and t['status'] == 'paid')

    print(f"\nSummary:")
    print(f"  Total receipts: ¥{total_receipts:,.0f}")
    print(f"  Completed receipts: ¥{completed_receipts:,.0f}")
    print(f"  Total payments: ¥{total_payments:,.0f}")
    print(f"  Paid payments: ¥{paid_payments:,.0f}")
    print(f"  Net balance: ¥{completed_receipts - paid_payments:,.0f}")

    return transactions

if __name__ == "__main__":
    # Check current month
    now = timezone.now()
    print("🔍 Checking current month:")
    debug_specific_month(now.year, now.month)

    # Check October (next month)
    print("\n🔍 Checking October 2025:")
    debug_specific_month(2025, 10)

    # Check previous month
    print("\n🔍 Checking August 2025:")
    debug_specific_month(2025, 8)