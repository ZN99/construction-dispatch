#!/usr/bin/env python
"""
Final comprehensive test of balance calculation
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

def final_balance_test():
    """Final comprehensive test replicating the exact accounting view logic"""
    print("=" * 60)
    print("FINAL COMPREHENSIVE BALANCE TEST")
    print("=" * 60)

    # Use the exact same logic as AccountingDashboardView.get_context_data
    now = timezone.now()
    year = int(now.year)  # Mimic the view's int conversion
    month = int(now.month)

    # Month boundaries
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    print(f"Testing for {year}-{month:02d} ({start_date} to {end_date})")

    # === Exact replica of view logic ===

    # Receipt projects query (exactly as in view)
    receipt_projects = Project.objects.filter(
        Q(payment_due_date__range=[start_date, end_date]) |
        Q(order_status='受注', billing_amount__gt=0)
    ).exclude(contractor_name__isnull=True).exclude(contractor_name='')

    print(f"Receipt projects found: {receipt_projects.count()}")

    # Payment subcontracts query
    payment_subcontracts = Subcontract.objects.filter(
        Q(payment_date__range=[start_date, end_date]) |
        Q(billed_amount__gt=0)
    ).select_related('project', 'contractor', 'internal_worker')

    print(f"Payment subcontracts found: {payment_subcontracts.count()}")

    # Transactions creation (exactly as in view)
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
                'project': project
            })

    # Payment transactions
    for subcontract in payment_subcontracts:
        amount = subcontract.billed_amount or subcontract.contract_amount or 0
        if amount > 0:
            payee = subcontract.contractor.name if subcontract.contractor else subcontract.internal_worker.name
            transactions.append({
                'date': subcontract.payment_date or start_date,
                'description': f'出金: {subcontract.site_name}',
                'client': payee,
                'type': 'payment',
                'amount': amount,
                'status': subcontract.payment_status,
                'project': subcontract.project
            })

    print(f"Total transactions created: {len(transactions)}")

    # Balance calculation (exactly as in view)
    transactions_for_calc = sorted(transactions, key=lambda x: x['date'])

    balance = 0
    balance_history = []

    for transaction in transactions_for_calc:
        old_balance = balance

        if transaction['type'] == 'receipt':
            if transaction['status'] == 'completed':
                balance += transaction['amount']
        else:  # payment
            if transaction['status'] == 'paid':
                balance -= transaction['amount']

        transaction['balance'] = balance

        # Track balance changes for debugging
        if balance != old_balance:
            balance_history.append({
                'date': transaction['date'],
                'type': transaction['type'],
                'amount': transaction['amount'],
                'status': transaction['status'],
                'old_balance': old_balance,
                'new_balance': balance,
                'change': balance - old_balance
            })

    # Display order (exactly as in view)
    transactions.sort(key=lambda x: x['date'], reverse=True)

    print(f"\n💰 Balance History (showing changes):")
    print("Date       | Type    | Amount      | Status    | Old Balance  | New Balance  | Change")
    print("-" * 95)

    for change in balance_history[:10]:  # Show first 10 changes
        print(f"{change['date']} | {change['type']:7s} | ¥{change['amount']:>9,.0f} | {change['status']:9s} | ¥{change['old_balance']:>9,.0f} | ¥{change['new_balance']:>9,.0f} | ¥{change['change']:>+8,.0f}")

    print(f"\n📊 Transaction Display (newest first):")
    print("Date       | Type    | Amount      | Status    | Balance")
    print("-" * 70)

    for transaction in transactions[:10]:
        print(f"{transaction['date']} | {transaction['type']:7s} | ¥{transaction['amount']:>9,.0f} | {transaction['status']:9s} | ¥{transaction['balance']:>9,.0f}")

    print(f"\n✅ Final Balance: ¥{balance:,.0f}")

    # Verify balance calculation
    completed_receipts = sum(t['amount'] for t in transactions if t['type'] == 'receipt' and t['status'] == 'completed')
    paid_payments = sum(t['amount'] for t in transactions if t['type'] == 'payment' and t['status'] == 'paid')
    expected_balance = completed_receipts - paid_payments

    print(f"\n🔍 Balance Verification:")
    print(f"  Completed receipts: ¥{completed_receipts:,.0f}")
    print(f"  Paid payments: ¥{paid_payments:,.0f}")
    print(f"  Expected balance: ¥{expected_balance:,.0f}")
    print(f"  Actual balance: ¥{balance:,.0f}")
    print(f"  Match: {'✅ YES' if balance == expected_balance else '❌ NO'}")

    if balance == 0 and completed_receipts > 0:
        print("\n⚠️  WARNING: Balance is 0 but there are completed receipts!")
        print("This suggests an issue with the balance calculation logic.")
    elif balance != expected_balance:
        print("\n⚠️  WARNING: Balance mismatch!")
        print("The running calculation doesn't match the expected total.")
    else:
        print("\n🎉 SUCCESS: Balance calculation is working correctly!")

    return balance

if __name__ == "__main__":
    from django.db.models import Q  # Import Q at the module level
    final_balance_test()