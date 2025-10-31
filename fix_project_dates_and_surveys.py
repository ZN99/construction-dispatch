#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
案件の作成日を過去数ヶ月に分散させる & 現地調査を適切に配置
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from order_management.models import Project
from surveys.models import Survey, SurveyPhoto, Surveyor
from django.utils import timezone
from django.contrib.auth.models import User


def distribute_project_dates():
    """案件の作成日を過去7ヶ月に分散（4月〜10月）"""
    print("=== 📅 案件作成日の分散処理開始 ===\n")

    projects = Project.objects.all().order_by('id')
    total = projects.count()

    if total == 0:
        print("案件がありません。")
        return

    # 現在の分布を確認
    print("【現在の作成日分布】")
    today = timezone.now().date()
    for i in range(6, -1, -1):
        month = today.replace(day=1) - timedelta(days=30*i)
        year, m = month.year, month.month
        count = Project.objects.filter(created_at__year=year, created_at__month=m).count()
        print(f"  {year}年{m:02d}月: {count}件")

    # 過去7ヶ月に分散させる（4月1日〜10月31日）
    print("\n【分散処理中...】")

    # 4月1日から10月31日までの範囲
    start_date = datetime(2025, 4, 1).date()
    end_date = datetime(2025, 10, 31).date()
    total_days = (end_date - start_date).days

    updated_count = 0

    for project in projects:
        # ランダムな日付を生成（4月1日〜10月31日）
        random_days = random.randint(0, total_days)
        new_created_at = timezone.make_aware(
            datetime.combine(
                start_date + timedelta(days=random_days),
                datetime.now().time()
            )
        )

        # 作成日を更新
        project.created_at = new_created_at

        # 工事日・完了日も調整（作成日より後）
        if project.work_start_date:
            days_offset = random.randint(7, 60)  # 7日〜60日後に着工
            project.work_start_date = new_created_at.date() + timedelta(days=days_offset)

        if project.work_end_date:
            if project.work_start_date:
                work_duration = random.randint(5, 30)  # 5日〜30日の工期
                project.work_end_date = project.work_start_date + timedelta(days=work_duration)
            else:
                project.work_end_date = new_created_at.date() + timedelta(days=random.randint(30, 90))

        # 完工日も調整
        if project.project_status == '完工' and project.completion_date:
            if project.work_end_date:
                project.completion_date = project.work_end_date + timedelta(days=random.randint(1, 7))
            else:
                project.completion_date = new_created_at.date() + timedelta(days=random.randint(30, 90))

        project.save()
        updated_count += 1

        if updated_count % 20 == 0:
            print(f"  処理中... {updated_count}/{total}件")

    print(f"\n✅ {updated_count}件の案件を更新しました")

    # 更新後の分布を確認
    print("\n【更新後の作成日分布】")
    for i in range(6, -1, -1):
        month = today.replace(day=1) - timedelta(days=30*i)
        year, m = month.year, month.month
        count = Project.objects.filter(created_at__year=year, created_at__month=m).count()
        status = "✅" if count > 0 else "⚠️"
        print(f"  {year}年{m:02d}月: {count}件 {status}")

    # 0件の月があるかチェック
    print("\n=== 🎯 結果 ===")
    zero_months = []
    for i in range(6, -1, -1):
        month = today.replace(day=1) - timedelta(days=30*i)
        year, m = month.year, month.month
        count = Project.objects.filter(created_at__year=year, created_at__month=m).count()
        if count == 0:
            zero_months.append(f"{year}年{m:02d}月")

    if zero_months:
        print(f"⚠️ 以下の月で案件が0件です:")
        for month in zero_months:
            print(f"  • {month}")
    else:
        print("✅ すべての月に案件が分散されました")


def create_additional_surveys():
    """現地調査データを追加作成（一部の案件のみ）"""
    print("\n=== 🔍 現地調査データの作成開始 ===\n")

    # 現在の状態を確認
    total_projects = Project.objects.count()
    existing_surveys = Survey.objects.count()
    projects_with_surveys = Project.objects.filter(survey__isnull=False).distinct().count()

    print(f"【現在の状態】")
    print(f"  総案件数: {total_projects}件")
    print(f"  現地調査数: {existing_surveys}件")
    print(f"  現地調査あり案件: {projects_with_surveys}件")
    print(f"  現地調査なし案件: {total_projects - projects_with_surveys}件\n")

    # 既存の現地調査を持たない案件から、ランダムに40%程度に現地調査を作成
    projects_without_survey = Project.objects.filter(survey__isnull=True)
    target_count = int(projects_without_survey.count() * 0.4)  # 約40%
    selected_projects = random.sample(list(projects_without_survey), min(target_count, projects_without_survey.count()))

    # 現地調査員を取得
    surveyors = list(Surveyor.objects.all())
    if not surveyors:
        print("⚠️ 現地調査員が見つかりません")
        return

    admin = User.objects.filter(is_staff=True).first()
    if not admin:
        print("⚠️ 管理者ユーザーが見つかりません")
        return

    created_count = 0
    for project in selected_projects:
        # 案件の作成日から7〜30日後に現地調査を設定
        days_offset = random.randint(7, 30)
        scheduled_date = project.created_at.date() + timedelta(days=days_offset)

        # ランダムに現地調査員を選択
        surveyor = random.choice(surveyors)

        # 現地調査を作成
        survey = Survey.objects.create(
            project=project,
            scheduled_date=scheduled_date,
            scheduled_start_time=datetime.now().time(),
            surveyor=surveyor,
            status=random.choice(['scheduled', 'completed', 'completed', 'completed']),  # completedが多め
            notes=f"{project.site_name}の現地調査"
        )

        # Note: 写真は実際の画像ファイルが必要なため、ここでは作成しない

        created_count += 1

    print(f"✅ {created_count}件の現地調査を作成しました")

    # 最終結果
    final_surveys = Survey.objects.count()
    final_projects_with_surveys = Project.objects.filter(survey__isnull=False).distinct().count()

    print(f"\n【最終状態】")
    print(f"  総案件数: {total_projects}件")
    print(f"  現地調査数: {final_surveys}件")
    print(f"  現地調査あり案件: {final_projects_with_surveys}件 ({final_projects_with_surveys/total_projects*100:.1f}%)")
    print(f"  現地調査なし案件: {total_projects - final_projects_with_surveys}件 ({(total_projects-final_projects_with_surveys)/total_projects*100:.1f}%)")

    # ステータス別の分布
    print(f"\n【現地調査ステータス別】")
    status_display = {
        'scheduled': '予定',
        'in_progress': '進行中',
        'completed': '完了',
        'pending_approval': '承認待ち',
        'approved': '承認済み',
        'rejected': '差し戻し',
        'cancelled': 'キャンセル',
    }
    for status, display in status_display.items():
        count = Survey.objects.filter(status=status).count()
        if count > 0:
            print(f"  {display}: {count}件")


def main():
    print("=" * 60)
    print("案件作成日の分散処理 & 現地調査の配置")
    print("=" * 60)

    distribute_project_dates()
    create_additional_surveys()

    print("\n" + "=" * 60)
    print("✨ 完了")
    print("=" * 60)


if __name__ == '__main__':
    main()
