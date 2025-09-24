#!/usr/bin/env python
"""
Check the actual accounting balance calculation in the view
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

def check_accounting_balance():
    """Check the accounting balance calculation exactly like the view does it"""
    print("=" * 60)
    print("CHECKING ACCOUNTING BALANCE CALCULATION")
    print("=" * 60)

    # Use current month like the view
    now = timezone.now()
    year = now.year
    month = now.month

    # Month range
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    print(f"Checking for {year}-{month:02d} ({start_date} to {end_date})")

    # Same query as the accounting view
    receipt_projects = Project.objects.filter(
        payment_due_date__range=[start_date, end_date],
        order_status='受注',
        billing_amount__gt=0
    ).exclude(contractor_name__isnull=True).exclude(contractor_name='')

    print(f"Found {receipt_projects.count()} receipt projects")

    # Create transactions exactly like the view
    transactions = []

    # Receipt transactions
    for project in receipt_projects:
        amount = project.billing_amount or project.estimate_amount or 0
        if amount > 0:
            transactions.append({
                'date': project.payment_due_date or project.contract_date or start_date,
                'description': f'入金: {project.site_name}',
                'client': project.contractor_name,
                'type': 'receipt',
                'amount': amount,
                'status': 'completed' if project.payment_status == 'executed' else 'pending',
                'project': project,
                'payment_status': project.payment_status  # Add for debugging
            })

    print(f"\nCreated {len(transactions)} transactions")

    # Show payment status distribution
    executed_count = sum(1 for t in transactions if t['status'] == 'completed')
    pending_count = sum(1 for t in transactions if t['status'] == 'pending')
    print(f"Executed (completed): {executed_count}")
    print(f"Pending: {pending_count}")

    # Balance calculation (oldest to newest)
    transactions_for_calc = sorted(transactions, key=lambda x: x['date'])

    print(f"\nBalance calculation (oldest to newest):")
    print("Date       | Description                    | Amount      | Status    | Payment Status | Balance")
    print("-" * 110)

    balance = 0
    for transaction in transactions_for_calc:
        if transaction['type'] == 'receipt':
            if transaction['status'] == 'completed':
                balance += transaction['amount']
        transaction['balance'] = balance

        print(f"{transaction['date']} | {transaction['description'][:28]:28s} | ¥{transaction['amount']:>9,.0f} | {transaction['status']:9s} | {transaction['payment_status']:14s} | ¥{balance:>9,.0f}")

    # Display order (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)

    print(f"\nDisplay order (newest to oldest):")
    print("Date       | Description                    | Amount      | Status    | Balance")
    print("-" * 80)

    for transaction in transactions[:10]:  # Show first 10
        print(f"{transaction['date']} | {transaction['description'][:28]:28s} | ¥{transaction['amount']:>9,.0f} | {transaction['status']:9s} | ¥{transaction['balance']:>9,.0f}")

    print(f"\nFinal balance: ¥{balance:,.0f}")

    if balance == 0:
        print("⚠️  WARNING: Balance is 0 - this indicates no 'executed' payment status projects!")
        print("⚠️  Let's check payment statuses...")

        all_projects = Project.objects.filter(
            order_status='受注',
            billing_amount__gt=0
        ).exclude(contractor_name__isnull=True).exclude(contractor_name='')

        status_counts = {}
        for project in all_projects:
            status = project.payment_status or 'None'
            status_counts[status] = status_counts.get(status, 0) + 1

        print(f"\nPayment status distribution across all projects:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")

    return balance

if __name__ == "__main__":
    check_accounting_balance()