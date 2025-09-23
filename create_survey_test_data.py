#!/usr/bin/env python
import os
import sys
import django
from datetime import date, time, datetime, timedelta

# Add the project directory to the Python path
sys.path.append('/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from order_management.models import Project
from surveys.models import Survey, SurveyRoom, SurveyWall, SurveyDamage, Surveyor

def create_test_data():
    # Get existing surveyors instead of creating users
    surveyor1 = Surveyor.objects.filter(is_active=True).first()
    surveyor2 = Surveyor.objects.filter(is_active=True).last()

    if not surveyor1:
        print("調査員が見つかりません。先に調査員を作成してください。")
        return

    if not surveyor2:
        surveyor2 = surveyor1  # Use same surveyor if only one exists

    # Get first project or create one
    project = Project.objects.first()
    if not project:
        project = Project.objects.create(
            management_no='DEMO-001',
            site_name='デモ案件 - 住宅内装リフォーム',
            site_address='○○県○○市サンプル町1-1-1',
            work_type='内装リフォーム',
            notes='デモ用の調査案件です（架空の物件）'
        )

    # Create test surveys
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Survey 1: In progress
    survey1, created = Survey.objects.get_or_create(
        project=project,
        surveyor=surveyor1,
        scheduled_date=today,
        scheduled_start_time=time(10, 0),
        defaults={
            'estimated_duration': 120,
            'status': 'in_progress',
            'actual_start_time': datetime.combine(today, time(10, 5)),
            'notes': 'テスト調査です。進行中の状態をテストしています。'
        }
    )

    if created:
        # Add room data for survey1
        room1 = SurveyRoom.objects.create(
            survey=survey1,
            room_name='リビング'
        )

        SurveyWall.objects.create(
            room=room1,
            direction='north',
            length=3.5,
            height=2.4,
            opening_area=1.5,
            foundation_type='gypsum_board',
            foundation_condition='good'
        )

        SurveyWall.objects.create(
            room=room1,
            direction='south',
            length=3.5,
            height=2.4,
            opening_area=0.0,
            foundation_type='gypsum_board',
            foundation_condition='good'
        )

        # Add damage data
        SurveyDamage.objects.create(
            survey=survey1,
            damage_type='nail_holes',
            has_dents=False,
            dent_count=0,
            description='壁面に小さな釘穴が複数箇所あり'
        )

    # Survey 2: Scheduled for tomorrow
    survey2, created = Survey.objects.get_or_create(
        project=project,
        surveyor=surveyor2,
        scheduled_date=tomorrow,
        scheduled_start_time=time(14, 30),
        defaults={
            'estimated_duration': 90,
            'status': 'scheduled',
            'notes': '明日予定の調査です。'
        }
    )

    # Survey 3: Completed yesterday
    yesterday = today - timedelta(days=1)
    survey3, created = Survey.objects.get_or_create(
        project=project,
        surveyor=surveyor1,
        scheduled_date=yesterday,
        scheduled_start_time=time(9, 0),
        defaults={
            'estimated_duration': 150,
            'status': 'completed',
            'actual_start_time': datetime.combine(yesterday, time(9, 0)),
            'actual_end_time': datetime.combine(yesterday, time(11, 15)),
            'notes': '調査完了済み。問題なく終了しました。'
        }
    )

    if created:
        # Add room data for completed survey
        room2 = SurveyRoom.objects.create(
            survey=survey3,
            room_name='キッチン'
        )

        SurveyWall.objects.create(
            room=room2,
            direction='east',
            length=2.8,
            height=2.4,
            opening_area=0.5,
            foundation_type='concrete',
            foundation_condition='needs_repair'
        )

        # Add damage data
        SurveyDamage.objects.create(
            survey=survey3,
            damage_type='oil_stain',
            has_dents=True,
            dent_count=2,
            description='キッチン周辺に油汚れと小さな凹みが確認された'
        )

    print("✅ テストデータの作成が完了しました！")
    print(f"- 調査員: {surveyor1.name}, {surveyor2.name}")
    print(f"- 案件: {project.site_name}")
    print(f"- 調査数: {Survey.objects.count()}件")
    print("\n🌐 調査管理画面を確認:")
    print("   http://localhost:8001/surveys/")

if __name__ == '__main__':
    create_test_data()