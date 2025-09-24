#!/usr/bin/env python
"""
Script to update payment statuses and add variety to project types
with September as peak revenue month.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, '/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch')
django.setup()

from django.utils import timezone
from order_management.models import Project

def update_payment_statuses():
    """Update payment statuses - mark some as completed"""
    print("Updating payment statuses...")

    # Get completed projects
    today = timezone.now().date()

    # First, mark some projects as completed if not enough
    all_projects = Project.objects.all()
    for project in all_projects[:25]:  # Mark first 25 as completed
        project.work_end_completed = True
        if not project.work_end_date:
            project.work_end_date = project.payment_due_date - timedelta(days=7) if project.payment_due_date else today - timedelta(days=30)
        project.save()

    # Now get projects with past payment due dates
    past_due_projects = Project.objects.filter(
        payment_due_date__lt=today,
        work_end_completed=True
    )

    # Mark 70% of past due projects as paid
    paid_count = int(past_due_projects.count() * 0.7) if past_due_projects.count() > 0 else 10
    projects_to_mark_paid = list(past_due_projects)

    # If not enough past due, use any completed projects
    if len(projects_to_mark_paid) < paid_count:
        completed_projects = Project.objects.filter(work_end_completed=True)
        projects_to_mark_paid = list(completed_projects)[:paid_count]

    random.shuffle(projects_to_mark_paid)

    for i, project in enumerate(projects_to_mark_paid[:paid_count]):
        # Set a payment executed date
        if project.payment_due_date:
            days_after_due = random.randint(1, 15)
            project.payment_executed_date = project.payment_due_date + timedelta(days=days_after_due)
        else:
            project.payment_executed_date = today - timedelta(days=random.randint(1, 30))
        project.payment_status = 'executed'
        project.save()

    print(f"Marked {min(paid_count, len(projects_to_mark_paid))} projects as paid")

def set_september_as_peak():
    """Adjust amounts to make September the peak revenue month"""
    print("Setting September as peak revenue month...")

    # Define monthly multipliers (September = 1.5x peak)
    monthly_multipliers = {
        1: 0.7,   # January
        2: 0.75,  # February
        3: 0.8,   # March
        4: 0.85,  # April
        5: 0.9,   # May
        6: 1.0,   # June
        7: 1.1,   # July
        8: 1.3,   # August
        9: 1.5,   # September (PEAK)
        10: 1.2,  # October
        11: 0.9,  # November
        12: 0.8,  # December
    }

    # Update project amounts based on their payment due date month
    projects = Project.objects.filter(payment_due_date__isnull=False)

    for project in projects:
        month = project.payment_due_date.month
        multiplier = monthly_multipliers.get(month, 1.0)

        # Adjust estimate amount with some randomness
        base_amount = project.estimate_amount or Decimal('500000')
        random_factor = Decimal(str(random.uniform(0.8, 1.2)))
        new_amount = base_amount * Decimal(str(multiplier)) * random_factor

        # Round to nearest 10,000
        new_amount = (new_amount / 10000).quantize(Decimal('1')) * 10000

        project.estimate_amount = new_amount
        if project.billing_amount:
            project.billing_amount = new_amount * Decimal('0.95')  # Billing slightly less

        project.save()

    print("Revenue distribution updated with September as peak")

def add_project_type_variety():
    """Add more variety to project types"""
    print("Adding variety to project types...")

    work_types = [
        '原状回復',
        'リフォーム',
        '改修工事',
        '設備更新',
        '外装工事',
        '内装工事',
        '防水工事',
        '塗装工事',
        '電気工事',
        '配管工事',
        '空調設備',
        '解体工事',
        'クリーニング',
        '補修工事',
        'バリアフリー化'
    ]

    # Add detailed work descriptions
    work_descriptions = {
        'リフォーム': ['キッチン', 'バスルーム', '洋室', 'トイレ', 'リビング'],
        '改修工事': ['外壁', '屋根', 'エントランス', '共用部', '駐車場'],
        '設備更新': ['給湯器', 'エアコン', '換気扇', 'インターホン', '照明'],
        '外装工事': ['外壁塗装', 'タイル張替', '防水処理', 'シーリング', 'サイディング'],
        '内装工事': ['クロス張替', 'フローリング', '建具交換', '収納設置', '間仕切り'],
        '防水工事': ['屋上', 'ベランダ', '外壁', '浴室', '基礎'],
        '電気工事': ['配線更新', 'ブレーカー交換', 'コンセント増設', 'LED化', 'アース工事'],
        '配管工事': ['給水管', '排水管', 'ガス管', '水漏れ修理', '配管洗浄']
    }

    projects = Project.objects.all()
    total_projects = projects.count()

    # Distribute work types
    for i, project in enumerate(projects):
        # 40% keep original (原状回復)
        # 60% get varied work types
        if random.random() > 0.4:
            work_type = random.choice(work_types)
            project.work_type = work_type

            # Add detailed description for some types
            if work_type in work_descriptions:
                detail = random.choice(work_descriptions[work_type])
                project.work_content = f"{work_type} - {detail}工事"
            else:
                project.work_content = f"{work_type}工事"

            # Adjust amounts based on work type
            if work_type in ['解体工事', '改修工事', '設備更新']:
                # Higher cost projects
                project.estimate_amount = project.estimate_amount * Decimal('1.5')
            elif work_type in ['クリーニング', '補修工事']:
                # Lower cost projects
                project.estimate_amount = project.estimate_amount * Decimal('0.5')

            project.save()

    print(f"Updated work type variety for {total_projects} projects")

def update_project_statuses():
    """Update various project statuses for realism"""
    print("Updating project statuses for realism...")

    projects = Project.objects.all()

    for project in projects:
        # Set order status variety
        status_choices = ['見積もり中', '交渉中', '受注', '失注', '保留']
        weights = [0.1, 0.1, 0.6, 0.05, 0.15]  # 60% 受注

        if project.work_end_completed:
            project.order_status = '受注'
        else:
            project.order_status = random.choices(status_choices, weights=weights)[0]

        # Add payment methods (skip for now as field doesn't exist)

        project.save()

    print("Project statuses updated")

def main():
    print("=" * 50)
    print("Updating Projects Data")
    print("=" * 50)

    # Run updates
    update_payment_statuses()
    set_september_as_peak()
    add_project_type_variety()
    update_project_statuses()

    # Show summary
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)

    # September revenue
    september_projects = Project.objects.filter(
        payment_due_date__month=9,
        payment_due_date__year=2025
    )
    september_revenue = sum(p.estimate_amount or 0 for p in september_projects)
    print(f"September revenue: ¥{september_revenue:,.0f}")

    # Payment status summary
    paid_projects = Project.objects.filter(payment_status='executed').count()
    total_projects = Project.objects.count()
    print(f"Paid projects: {paid_projects}/{total_projects}")

    # Work type variety
    work_types = Project.objects.values_list('work_type', flat=True).distinct()
    print(f"Work type variety: {len(work_types)} types")

    print("\nUpdate completed successfully!")

if __name__ == "__main__":
    main()