#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
調査サンプルデータを作成するスクリプト
"""

import os
import sys
import django
from datetime import date, time, timedelta
import random

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from surveys.models import Survey, Surveyor
from order_management.models import Project

def create_sample_surveys():
    """サンプル調査データを作成"""

    print("調査サンプルデータを作成中...")

    # 調査員を取得
    surveyors = list(Surveyor.objects.all())
    if not surveyors:
        print("エラー: 調査員が見つかりません。先にcreate_surveyors.pyを実行してください。")
        return

    # プロジェクトを取得
    projects = Project.objects.filter(survey_required=True)

    # 既存の調査を削除
    Survey.objects.all().delete()

    # 調査データ作成
    created_count = 0
    today = date.today()

    for project in projects:
        # ランダムに調査の数を決定（1-3件）
        survey_count = random.randint(1, 2)

        for i in range(survey_count):
            # 調査日程を設定（今日から1週間～4週間後）
            days_offset = random.randint(7, 28)
            scheduled_date = today + timedelta(days=days_offset)

            # 開始時刻を設定（9:00-15:00の間）
            hour = random.choice([9, 10, 11, 13, 14, 15])
            minute = random.choice([0, 30])
            scheduled_start_time = time(hour, minute)

            # 所要時間（60-180分）
            estimated_duration = random.choice([60, 90, 120, 150, 180])

            # ステータス（70%がscheduled、20%がcompleted、10%がin_progress）
            status_choice = random.random()
            if status_choice < 0.7:
                status = 'scheduled'
            elif status_choice < 0.9:
                status = 'completed'
            else:
                status = 'in_progress'

            # 調査員をランダム選択
            surveyor = random.choice(surveyors)

            try:
                survey = Survey.objects.create(
                    project=project,
                    surveyor=surveyor,
                    scheduled_date=scheduled_date,
                    scheduled_start_time=scheduled_start_time,
                    estimated_duration=estimated_duration,
                    status=status,
                    notes=f"{project.site_name}の現地調査 #{i+1}"
                )

                # 完了した調査には実際の開始・終了時刻を設定
                if status == 'completed':
                    from django.utils import timezone
                    # 1-7日前に実施したことにする
                    actual_date = today - timedelta(days=random.randint(1, 7))
                    actual_start = timezone.datetime.combine(actual_date, scheduled_start_time)
                    survey.actual_start_time = actual_start
                    survey.actual_end_time = actual_start + timedelta(minutes=estimated_duration)
                    survey.save()

                created_count += 1
                print(f"✓ {project.site_name} - {surveyor.name} ({scheduled_date} {scheduled_start_time})")

            except Exception as e:
                print(f"✗ {project.site_name} の調査作成に失敗: {str(e)}")

    print(f"\n完了: {created_count}件の調査を作成しました。")

if __name__ == '__main__':
    create_sample_surveys()