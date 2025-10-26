#!/usr/bin/env python
"""
未来のプロジェクトダミーデータ生成スクリプト
売上予測機能のため
"""
import os
import django
import sys
from datetime import date, timedelta
from decimal import Decimal
import random

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth.models import User
from order_management.models import Project

def generate_future_projects():
    """未来のプロジェクトを生成"""
    print("\n" + "=" * 60)
    print("未来のプロジェクトダミーデータ生成")
    print("=" * 60)

    user = User.objects.first()
    if not user:
        print("❌ ユーザーが存在しません")
        return

    today = date.today()
    projects = []

    # 今後12ヶ月分のプロジェクトを生成
    for month_offset in range(12):
        # 各月に2-5件のプロジェクト
        num_projects = random.randint(2, 5)

        for i in range(num_projects):
            # 工事開始日を設定
            days_in_month = random.randint(1, 28)
            work_start = date(
                today.year + (today.month + month_offset - 1) // 12,
                (today.month + month_offset - 1) % 12 + 1,
                days_in_month
            )

            # 工事期間: 10-60日
            duration = random.randint(10, 60)
            work_end = work_start + timedelta(days=duration)

            # 受注金額: 300万〜3000万
            order_amount = Decimal(str(random.randint(3000000, 30000000)))

            # ステータス: 70%がネタ、30%が施工日待ち
            status = 'ネタ' if random.random() < 0.7 else '施工日待ち'

            # プロジェクト名
            site_types = ['マンション', 'オフィスビル', '商業施設', '工場', '倉庫', '住宅']
            site_type = random.choice(site_types)

            # 顧客名
            companies = ['株式会社田中建設', '鈴木不動産', '山田商事', '佐藤工業', '高橋開発']
            client = random.choice(companies)

            project = Project(
                management_no=f'P{today.year}{today.month:02d}{month_offset:02d}{i:02d}',
                site_name=f'{site_type}新築工事',
                client_name=client,
                project_status=status,
                order_amount=order_amount,
                work_start_date=work_start,
                work_end_date=work_end
            )
            projects.append(project)

    # 一括保存
    Project.objects.bulk_create(projects, ignore_conflicts=True)

    print(f"\n✅ 未来のプロジェクト生成完了: {len(projects)}件")

    # 統計
    neta_count = len([p for p in projects if p.project_status == 'ネタ'])
    waiting_count = len([p for p in projects if p.project_status == '施工日待ち'])
    total_value = sum(p.order_amount for p in projects)

    print(f"\n📊 統計:")
    print(f"   ネタ: {neta_count}件")
    print(f"   施工日待ち: {waiting_count}件")
    print(f"   総額: ¥{total_value:,.0f}")

    # 月別分布
    print(f"\n📅 月別分布:")
    for month_offset in range(6):  # 最初の6ヶ月を表示
        target_year = today.year + (today.month + month_offset - 1) // 12
        target_month = (today.month + month_offset - 1) % 12 + 1

        month_projects = [p for p in projects if
                         p.work_start_date.year == target_year and
                         p.work_start_date.month == target_month]

        if month_projects:
            month_value = sum(p.order_amount for p in month_projects)
            print(f"   {target_year}/{target_month:02d}: {len(month_projects)}件 (¥{month_value:,.0f})")


def main():
    print("\n" + "🚀 未来のプロジェクトダミーデータ生成")
    print("=" * 60)

    # 既存の未来プロジェクト確認
    today = date.today()
    existing = Project.objects.filter(
        project_status__in=['ネタ', '施工日待ち'],
        work_start_date__gte=today
    ).count()

    print(f"\n既存の未来プロジェクト: {existing}件")

    if existing > 0:
        response = input("既存データに追加しますか？ (y/n): ")
        if response.lower() != 'y':
            print("キャンセルしました")
            return

    # データ生成
    generate_future_projects()

    print("\n" + "=" * 60)
    print("🎉 完了！")
    print("=" * 60)
    print("\n次のステップ:")
    print("1. http://127.0.0.1:8000/orders/forecast/ で売上予測を確認")
    print("2. シナリオを選択して予測データを表示")

if __name__ == '__main__':
    main()
