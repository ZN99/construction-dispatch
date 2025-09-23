#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
現場調査データ作成スクリプト
"""

import os
import sys
import django
from datetime import datetime, date, timedelta, time
from decimal import Decimal
import random

# Djangoの設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.utils import timezone
from order_management.models import Project
from surveys.models import Survey, Surveyor, SurveyRoom, SurveyWall, SurveyDamage

def create_survey_data():
    """現場調査データを作成"""

    print("=" * 50)
    print("現場調査データを作成します...")

    # 既存のプロジェクトを取得
    projects = Project.objects.filter(
        contractor_name__isnull=False
    ).exclude(
        contractor_name=''
    )[:20]  # 最初の20件に調査データを作成

    if not projects.exists():
        print("❌ プロジェクトが見つかりません")
        return

    # 調査員を取得
    surveyors = list(Surveyor.objects.filter(is_active=True))
    if not surveyors:
        print("❌ 調査員が見つかりません")
        return

    print(f"📊 {projects.count()}件のプロジェクトに調査データを作成")
    print(f"👷 調査員: {len(surveyors)}名")

    survey_count = 0
    today = date.today()

    # 調査ステータスのパターン
    status_patterns = [
        'scheduled',  # 予定
        'in_progress',  # 進行中
        'completed',  # 完了
        'approved',  # 承認済み
    ]

    for project in projects:
        # ランダムに調査員を選択
        surveyor = random.choice(surveyors)

        # ステータスをランダムに選択
        status = random.choice(status_patterns)

        # 調査日を設定（過去30日から未来7日の間でランダム）
        days_offset = random.randint(-30, 7)
        survey_date = today + timedelta(days=days_offset)

        # 調査時間を設定（9時から16時の間でランダム）
        start_hour = random.randint(9, 15)
        scheduled_start_time = time(start_hour, 0)

        # 調査時間（60分から180分）
        duration = random.randint(60, 180)

        # 調査データを作成
        survey = Survey.objects.create(
            project=project,
            surveyor=surveyor,
            scheduled_date=survey_date,
            scheduled_start_time=scheduled_start_time,
            estimated_duration=duration,
            status=status,
            notes=f"プロジェクト「{project.site_name}」の現地調査"
        )

        # ステータスに応じて追加データを設定
        if status in ['in_progress', 'completed', 'approved']:
            survey.actual_start_time = timezone.make_aware(
                datetime.combine(survey_date, time(start_hour, 5))
            )

        if status in ['completed', 'approved']:
            end_time = datetime.combine(
                survey_date,
                time(start_hour + (duration // 60), duration % 60)
            )
            survey.actual_end_time = timezone.make_aware(end_time)
            survey.weather = random.choice(['sunny', 'cloudy', 'rainy'])
            survey.temperature = random.randint(15, 30)

        if status == 'approved':
            survey.approved_at = timezone.now()
            survey.approved_by = 'システム管理者'
            survey.approval_notes = '問題なし'

        survey.save()

        # 完了済みの調査には部屋データを追加
        if status in ['completed', 'approved']:
            room_types = ['living', 'bedroom', 'kitchen', 'bathroom', 'entrance', 'other']
            num_rooms = random.randint(3, 6)

            for i in range(num_rooms):
                room_type = random.choice(room_types)
                room_name = {
                    'living': 'リビング',
                    'bedroom': f'寝室{i+1}',
                    'kitchen': 'キッチン',
                    'bathroom': '浴室',
                    'entrance': '玄関',
                    'other': f'その他{i+1}'
                }.get(room_type, f'部屋{i+1}')

                room = SurveyRoom.objects.create(
                    survey=survey,
                    room_name=room_name
                )

                # 各部屋に壁データを追加
                num_walls = random.randint(2, 4)
                for wall_num in range(1, num_walls + 1):
                    wall = SurveyWall.objects.create(
                        room=room,
                        direction=random.choice(['north', 'south', 'east', 'west']),
                        length=Decimal(random.randint(200, 400) / 100),
                        height=Decimal('2.4'),
                        opening_area=Decimal(random.randint(0, 20) / 10),
                        foundation_type=random.choice(['gypsum_board', 'concrete', 'plywood', 'other']),
                        foundation_condition=random.choice(['good', 'needs_repair'])
                    )

                    # ダメージ情報を追加（30%の確率）
                    if random.random() < 0.3:
                        SurveyDamage.objects.create(
                            survey=survey,
                            damage_type=random.choice([
                                'stain_discoloration',
                                'tear_peel',
                                'nail_holes',
                                'large_holes',
                                'mold_stain',
                                'tobacco_stain',
                                'oil_stain'
                            ]),
                            has_dents=random.choice([True, False]),
                            dent_count=random.randint(0, 5),
                            description=random.choice([
                                'クラックあり',
                                '汚れあり',
                                '穴あり',
                                '水漏れ跡',
                                'カビ発生'
                            ])
                        )

        survey_count += 1

        status_emoji = {
            'scheduled': '📅',
            'in_progress': '🔄',
            'completed': '✅',
            'approved': '👍'
        }.get(status, '❓')

        print(f"  {status_emoji} {project.site_name[:20]}... - {surveyor.name} ({status})")

    # 統計情報を表示
    print("\n" + "=" * 50)
    print("📊 調査データ作成結果:")
    print(f"  作成件数: {survey_count}件")

    # ステータス別の集計
    for status_choice in status_patterns:
        count = Survey.objects.filter(status=status_choice).count()
        status_label = {
            'scheduled': '予定',
            'in_progress': '進行中',
            'completed': '完了',
            'approved': '承認済み'
        }.get(status_choice, status_choice)
        print(f"  {status_label}: {count}件")

    total_rooms = SurveyRoom.objects.count()
    total_walls = SurveyWall.objects.count()
    total_damages = SurveyDamage.objects.count()

    print(f"\n📐 詳細データ:")
    print(f"  部屋数: {total_rooms}室")
    print(f"  壁面数: {total_walls}面")
    print(f"  ダメージ箇所: {total_damages}件")

    print("\n✨ 現場調査データの作成が完了しました！")
    print("🌐 確認URL: http://localhost:8000/surveys/")


if __name__ == '__main__':
    create_survey_data()