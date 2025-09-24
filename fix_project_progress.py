#!/usr/bin/env python
"""
Fix project progress status to show realistic in-progress projects
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

def fix_project_progress_status():
    """Fix project progress status based on work dates and realistic scenarios"""
    print("=" * 60)
    print("FIXING PROJECT PROGRESS STATUS")
    print("=" * 60)

    projects = Project.objects.all()
    now = timezone.now().date()

    progress_categories = {
        'not_started': 0,
        'in_progress': 0,
        'completed': 0
    }

    for project in projects:
        # Ensure work_start_date and work_end_date exist
        if not project.work_start_date:
            if project.contract_date:
                # Start work 1-7 days after contract
                days_after_contract = random.randint(1, 7)
                project.work_start_date = project.contract_date + timedelta(days=days_after_contract)
            elif project.payment_due_date:
                # Assume work starts before payment due date
                work_duration = random.randint(14, 30)
                project.work_start_date = project.payment_due_date - timedelta(days=work_duration)

        if not project.work_end_date and project.work_start_date:
            # Work duration: 5-21 days
            work_duration = random.randint(5, 21)
            project.work_end_date = project.work_start_date + timedelta(days=work_duration)

        # Determine project status based on dates
        if project.work_start_date and project.work_end_date:
            if now < project.work_start_date:
                # Not started yet
                project.work_start_completed = False
                project.work_end_completed = False
                progress_categories['not_started'] += 1

            elif project.work_start_date <= now < project.work_end_date:
                # In progress
                project.work_start_completed = True
                project.work_end_completed = False
                progress_categories['in_progress'] += 1

            else:  # now >= work_end_date
                # Completed
                project.work_start_completed = True
                project.work_end_completed = True
                progress_categories['completed'] += 1

        project.save()

    print(f"Progress Status Distribution:")
    print(f"  Not Started: {progress_categories['not_started']}")
    print(f"  In Progress: {progress_categories['in_progress']}")
    print(f"  Completed: {progress_categories['completed']}")

    return progress_categories

def show_sample_projects():
    """Show sample projects from each category"""
    print("\n" + "=" * 60)
    print("SAMPLE PROJECTS BY STATUS")
    print("=" * 60)

    # In-progress projects
    in_progress = Project.objects.filter(work_start_completed=True, work_end_completed=False)
    print(f"\nIn-Progress Projects ({in_progress.count()}):")
    for project in in_progress[:3]:
        print(f"  - {project.site_name}")
        print(f"    Start: {project.work_start_date} | End: {project.work_end_date}")
        print(f"    Order Status: {project.order_status}")

    # Not started projects
    not_started = Project.objects.filter(work_start_completed=False)
    print(f"\nNot Started Projects ({not_started.count()}):")
    for project in not_started[:3]:
        print(f"  - {project.site_name}")
        print(f"    Start: {project.work_start_date} | End: {project.work_end_date}")

    # Completed projects
    completed = Project.objects.filter(work_end_completed=True)
    print(f"\nCompleted Projects ({completed.count()}):")
    for project in completed[:3]:
        print(f"  - {project.site_name}")
        print(f"    Start: {project.work_start_date} | End: {project.work_end_date}")

def main():
    print("🔧 Fixing Project Progress Status")

    categories = fix_project_progress_status()
    show_sample_projects()

    print(f"\n✅ Progress Status Fixed:")
    print(f"  📋 Not Started: {categories['not_started']} projects")
    print(f"  🔨 In Progress: {categories['in_progress']} projects")
    print(f"  ✅ Completed: {categories['completed']} projects")

if __name__ == "__main__":
    main()