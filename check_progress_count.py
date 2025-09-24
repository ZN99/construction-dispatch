#!/usr/bin/env python
"""
Check in-progress project count calculation
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, '/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch')
django.setup()

from order_management.models import Project

def check_progress_counts():
    """Check project progress counts"""
    print("=" * 60)
    print("PROJECT PROGRESS COUNT CHECK")
    print("=" * 60)

    total_projects = Project.objects.count()
    received_projects = Project.objects.filter(order_status='受注')
    in_progress_projects = Project.objects.filter(work_start_completed=True, work_end_completed=False)
    completed_projects = Project.objects.filter(work_end_completed=True)

    print(f"Total projects: {total_projects}")
    print(f"Received (受注): {received_projects.count()}")
    print(f"In progress (作業開始済み・未完了): {in_progress_projects.count()}")
    print(f"Completed (作業完了): {completed_projects.count()}")

    # Detailed breakdown
    print("\nDetailed Status Breakdown:")

    # Work start status
    work_start_completed = Project.objects.filter(work_start_completed=True).count()
    work_start_not_completed = Project.objects.filter(work_start_completed=False).count()

    print(f"Work started: {work_start_completed}")
    print(f"Work not started: {work_start_not_completed}")

    # Work end status
    work_end_completed = Project.objects.filter(work_end_completed=True).count()
    work_end_not_completed = Project.objects.filter(work_end_completed=False).count()

    print(f"Work completed: {work_end_completed}")
    print(f"Work not completed: {work_end_not_completed}")

    # Show some sample in-progress projects
    print(f"\nSample In-Progress Projects:")
    for project in in_progress_projects[:5]:
        print(f"  - {project.site_name}")
        print(f"    Order Status: {project.order_status}")
        print(f"    Work Start: {project.work_start_completed} (Date: {project.work_start_date})")
        print(f"    Work End: {project.work_end_completed} (Date: {project.work_end_date})")

    # Alternative progress calculation
    print(f"\nAlternative Progress Calculations:")

    # Method 1: Based on order status and work status
    alt_in_progress_1 = Project.objects.filter(
        order_status='受注',
        work_start_completed=True,
        work_end_completed=False
    ).count()
    print(f"Alt 1 (受注 + 開始済み + 未完了): {alt_in_progress_1}")

    # Method 2: Based on work dates
    from django.utils import timezone
    now = timezone.now().date()

    alt_in_progress_2 = Project.objects.filter(
        work_start_date__lte=now,
        work_end_date__gte=now
    ).count()
    print(f"Alt 2 (作業期間中): {alt_in_progress_2}")

    # Method 3: Based on work start but not completed
    alt_in_progress_3 = Project.objects.filter(
        work_start_date__isnull=False,
        work_end_completed=False
    ).count()
    print(f"Alt 3 (開始日あり + 未完了): {alt_in_progress_3}")

if __name__ == "__main__":
    check_progress_counts()