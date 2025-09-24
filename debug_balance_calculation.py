#!/usr/bin/env python
"""
Debug the balance calculation issue in passbook view
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
from order_management.models import Project, Subcontract

def simulate_passbook_logic():
    """Simulate current passbook logic to debug balance issue"""
    print("=" * 60)
    print("DEBUGGING PASSBOOK BALANCE CALCULATION")
    print("=" * 60)

    # Simulate the same logic as views_accounting.py
    year = 2025
    month = 9
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, 30).date()

    # Get receipt projects (same logic as view)
    receipt_projects = Project.objects.filter(
        payment_due_date__range=[start_date, end_date],
        estimate_amount__gt=0
    ).exclude(
        contractor_name__isnull=True
    ).exclude(
        contractor_name=''
    )

    # Get payment subcontracts
    payment_subcontracts = Subcontract.objects.filter(
        payment_date__range=[start_date, end_date]
    )

    transactions = []

    # Add receipt transactions
    for project in receipt_projects:
        amount = project.billing_amount or project.estimate_amount or 0
        if amount > 0:
            status = 'completed' if project.payment_status == 'executed' else 'pending'
            transactions.append({
                'date': project.payment_due_date or start_date,
                'description': f'入金: {project.site_name}',
                'client': project.contractor_name,
                'type': 'receipt',
                'amount': amount,
                'status': status,
                'project': project
            })

    # Add payment transactions
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

    print(f"Total transactions: {len(transactions)}")

    # Sort by date (newest first) - same as current logic
    transactions.sort(key=lambda x: x['date'], reverse=True)

    print("\nCURRENT BALANCE CALCULATION (PROBLEMATIC):")
    print("Date       | Type    | Amount      | Status     | Balance")
    print("-" * 65)

    # Current problematic logic
    balance = 0
    for i, transaction in enumerate(transactions[:10]):  # Show first 10
        if transaction['type'] == 'receipt':
            if transaction['status'] == 'completed':
                balance += transaction['amount']
        else:  # payment
            if transaction['status'] == 'paid':
                balance -= transaction['amount']

        transaction['balance'] = balance

        print(f"{transaction['date']} | {transaction['type']:7s} | ¥{transaction['amount']:>9,.0f} | {transaction['status']:10s} | ¥{balance:>9,.0f}")

    print("\nFIXED BALANCE CALCULATION (CORRECT):")
    print("Date       | Type    | Amount      | Status     | Balance")
    print("-" * 65)

    # Fixed logic: calculate from oldest to newest, then reverse for display
    transactions_for_calc = sorted(transactions, key=lambda x: x['date'])  # Oldest first for calculation

    balance = 0
    for transaction in transactions_for_calc:
        if transaction['type'] == 'receipt':
            if transaction['status'] == 'completed':
                balance += transaction['amount']
        else:  # payment
            if transaction['status'] == 'paid':
                balance -= transaction['amount']

        transaction['correct_balance'] = balance

    # Now show in newest first order
    for i, transaction in enumerate(transactions[:10]):  # Show first 10 (newest first)
        print(f"{transaction['date']} | {transaction['type']:7s} | ¥{transaction['amount']:>9,.0f} | {transaction['status']:10s} | ¥{transaction.get('correct_balance', 0):>9,.0f}")

    # Show some statistics
    receipt_completed = [t for t in transactions if t['type'] == 'receipt' and t['status'] == 'completed']
    receipt_pending = [t for t in transactions if t['type'] == 'receipt' and t['status'] == 'pending']

    print(f"\nStatistics:")
    print(f"Receipt completed: {len(receipt_completed)} transactions")
    print(f"Receipt pending: {len(receipt_pending)} transactions")

    if receipt_completed:
        print(f"Sample completed receipts:")
        for t in receipt_completed[:3]:
            print(f"  {t['date']} - {t['description'][:30]} - ¥{t['amount']:,.0f}")

if __name__ == "__main__":
    simulate_passbook_logic()