#!/usr/bin/env python
"""
Fix payment status distribution to realistic ratios:
- 80% paid (executed)
- 10% pending (scheduled)
- 10% overdue
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, '/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch')
django.setup()

from django.utils import timezone
from order_management.models import Project

def fix_payment_distribution():
    """Fix payment status distribution to realistic ratios"""
    print("=" * 60)
    print("FIXING PAYMENT STATUS DISTRIBUTION")
    print("=" * 60)

    # Get all projects with billing amounts
    projects = Project.objects.filter(
        order_status='受注',
        billing_amount__gt=0
    ).exclude(contractor_name__isnull=True).exclude(contractor_name='')

    total_projects = projects.count()
    print(f"Total projects to update: {total_projects}")

    # Calculate distribution counts
    paid_count = int(total_projects * 0.8)  # 80%
    pending_count = int(total_projects * 0.1)  # 10%
    overdue_count = total_projects - paid_count - pending_count  # Remaining (should be ~10%)

    print(f"Target distribution:")
    print(f"  Paid (executed): {paid_count} ({paid_count/total_projects*100:.1f}%)")
    print(f"  Pending (scheduled): {pending_count} ({pending_count/total_projects*100:.1f}%)")
    print(f"  Overdue: {overdue_count} ({overdue_count/total_projects*100:.1f}%)")

    # Convert to list and shuffle for random distribution
    projects_list = list(projects)
    random.shuffle(projects_list)

    current_date = timezone.now().date()

    # Assign status based on distribution
    for i, project in enumerate(projects_list):
        if i < paid_count:
            # Paid status - payment completed
            project.payment_status = 'executed'
            # Set payment due date in the past for paid projects
            if project.payment_due_date and project.payment_due_date > current_date:
                days_ago = random.randint(1, 30)
                project.payment_due_date = current_date - timedelta(days=days_ago)

        elif i < paid_count + pending_count:
            # Pending status - payment scheduled but not yet due
            project.payment_status = 'scheduled'
            # Set payment due date in the future for pending projects
            if not project.payment_due_date or project.payment_due_date <= current_date:
                days_ahead = random.randint(1, 45)
                project.payment_due_date = current_date + timedelta(days=days_ahead)

        else:
            # Overdue status - payment should have been received but wasn't
            project.payment_status = 'scheduled'  # Still scheduled but overdue
            # Set payment due date in the past for overdue projects
            if not project.payment_due_date or project.payment_due_date >= current_date:
                days_overdue = random.randint(1, 60)
                project.payment_due_date = current_date - timedelta(days=days_overdue)

        project.save()

    # Verify the distribution
    print("\nActual distribution after update:")
    executed_count = projects.filter(payment_status='executed').count()
    scheduled_future = projects.filter(
        payment_status='scheduled',
        payment_due_date__gt=current_date
    ).count()
    scheduled_overdue = projects.filter(
        payment_status='scheduled',
        payment_due_date__lte=current_date
    ).count()

    print(f"  Paid (executed): {executed_count} ({executed_count/total_projects*100:.1f}%)")
    print(f"  Pending (scheduled, future due): {scheduled_future} ({scheduled_future/total_projects*100:.1f}%)")
    print(f"  Overdue (scheduled, past due): {scheduled_overdue} ({scheduled_overdue/total_projects*100:.1f}%)")

    return {
        'total': total_projects,
        'paid': executed_count,
        'pending': scheduled_future,
        'overdue': scheduled_overdue
    }

def show_sample_projects():
    """Show sample projects from each category"""
    print("\n" + "=" * 60)
    print("SAMPLE PROJECTS BY PAYMENT STATUS")
    print("=" * 60)

    current_date = timezone.now().date()

    # Paid projects
    paid_projects = Project.objects.filter(payment_status='executed')[:3]
    print(f"\nPaid Projects ({paid_projects.count()} total):")
    for project in paid_projects:
        print(f"  - {project.site_name}")
        print(f"    Status: {project.payment_status} | Due: {project.payment_due_date}")
        print(f"    Amount: ¥{project.billing_amount:,}")

    # Pending projects
    pending_projects = Project.objects.filter(
        payment_status='scheduled',
        payment_due_date__gt=current_date
    )[:3]
    print(f"\nPending Projects ({pending_projects.count()} total):")
    for project in pending_projects:
        print(f"  - {project.site_name}")
        print(f"    Status: {project.payment_status} | Due: {project.payment_due_date}")
        print(f"    Amount: ¥{project.billing_amount:,}")

    # Overdue projects
    overdue_projects = Project.objects.filter(
        payment_status='scheduled',
        payment_due_date__lte=current_date
    )[:3]
    print(f"\nOverdue Projects ({overdue_projects.count()} total):")
    for project in overdue_projects:
        print(f"  - {project.site_name}")
        print(f"    Status: {project.payment_status} | Due: {project.payment_due_date}")
        print(f"    Amount: ¥{project.billing_amount:,}")

def main():
    print("💰 Fixing Payment Status Distribution")

    distribution = fix_payment_distribution()
    show_sample_projects()

    print(f"\n✅ Payment Distribution Fixed:")
    print(f"  💸 Paid: {distribution['paid']} projects (80% target)")
    print(f"  ⏳ Pending: {distribution['pending']} projects (10% target)")
    print(f"  🚨 Overdue: {distribution['overdue']} projects (10% target)")

if __name__ == "__main__":
    main()