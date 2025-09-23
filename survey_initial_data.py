import os
import django
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "construction_dispatch.settings")
django.setup()

from projects.models import Surveyor, Survey, Project
from django.utils import timezone

# 調査員データの初期化（架空の人物）
surveyors = [
    {
        "name": "サンプル 太郎",
        "phone": "090-1234-5678",
        "email": "sample.taro@demo-survey.example.com",
        "base_location": "東京都○○区",
        "daily_capacity": 3,
        "work_start_time": "09:00",
        "work_end_time": "17:00",
    },
    {
        "name": "テスト 花子",
        "phone": "090-2345-6789",
        "email": "test.hanako@demo-survey.example.com",
        "base_location": "東京都○○区",
        "daily_capacity": 4,
        "work_start_time": "08:30",
        "work_end_time": "17:30",
    },
    {
        "name": "ダミー 次郎",
        "phone": "090-3456-7890",
        "email": "dummy.jiro@demo-survey.example.com",
        "base_location": "神奈川県○○市",
        "daily_capacity": 2,
        "work_start_time": "09:30",
        "work_end_time": "16:30",
    },
]

for surveyor_data in surveyors:
    surveyor, created = Surveyor.objects.get_or_create(
        name=surveyor_data["name"],
        defaults={
            "phone": surveyor_data["phone"],
            "email": surveyor_data["email"],
            "base_location": surveyor_data["base_location"],
            "daily_capacity": surveyor_data["daily_capacity"],
            "work_start_time": surveyor_data["work_start_time"],
            "work_end_time": surveyor_data["work_end_time"],
        },
    )
    if created:
        print(f'調査員 "{surveyor.name}" を作成しました')
    else:
        print(f'調査員 "{surveyor.name}" は既に存在します')

# サンプル調査データの作成
projects = Project.objects.all()[:5]  # 最初の5件の案件を使用

if projects:
    for i, project in enumerate(projects):
        survey, created = Survey.objects.get_or_create(
            project=project,
            defaults={
                "surveyor": Surveyor.objects.all()[i % 3],  # 3人の調査員に順番にアサイン
                "scheduled_date": timezone.now()
                + timedelta(days=i + 1, hours=9 + i * 2),
                "estimated_duration": 120 + (i * 30),
                "priority": ["normal", "high", "urgent", "normal", "low"][i],
                "status": "scheduled",
                "access_info": f"サンプルアクセス情報 {i+1}",
                "notes": f"サンプル調査メモ {i+1}",
            },
        )
        if created:
            print(f'調査 "{survey.project.title}" を作成しました')
        else:
            print(f'調査 "{survey.project.title}" は既に存在します')

print("調査データの初期化が完了しました！")
