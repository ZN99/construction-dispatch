#!/usr/bin/env python
"""業者管理ダッシュボードのテストデータ作成スクリプト"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from order_management.models import Contractor, Project

def create_test_data():
    """テスト用の受注業者とプロジェクトデータを作成"""

    # 1. 受注業者を作成
    contractors_data = [
        {
            'name': '山田建設株式会社',
            'address': 'テスト県デモ市サンプル町1-2-3',
            'phone': '03-1234-5678',
            'email': 'yamada@construction.jp',
            'contact_person': '山田太郎',
            'specialties': '建築工事全般、リフォーム',
            'is_receiving': True,
            'is_active': True
        },
        {
            'name': '鈴木電気工事',
            'address': 'ダミー県架空市テスト町2-3-4',
            'phone': '03-2345-6789',
            'email': 'suzuki@denki.jp',
            'contact_person': '鈴木一郎',
            'specialties': '電気設備工事、配線工事',
            'is_receiving': True,
            'is_active': True
        },
        {
            'name': '佐藤設備工業',
            'address': 'サンプル県デモ市架空区3-4-5',
            'phone': '03-3456-7890',
            'email': 'sato@setsubi.jp',
            'contact_person': '佐藤次郎',
            'specialties': '給排水設備、空調設備',
            'is_receiving': True,
            'is_active': True
        },
        {
            'name': '高橋塗装店',
            'address': 'テスト県サンプル市デモ町4-5-6',
            'phone': '03-4567-8901',
            'email': 'takahashi@paint.jp',
            'contact_person': '高橋三郎',
            'specialties': '外壁塗装、内装塗装',
            'is_receiving': True,
            'is_active': True
        },
        {
            'name': '中村内装工事',
            'address': 'ダミー県テスト市サンプル区5-6-7',
            'phone': '03-5678-9012',
            'email': 'nakamura@interior.jp',
            'contact_person': '中村四郎',
            'specialties': '内装工事、クロス張替',
            'is_receiving': True,
            'is_active': True
        }
    ]

    print("既存の受注業者を削除...")
    Contractor.objects.filter(is_receiving=True).delete()

    print("関連するプロジェクトを削除...")
    # 業者名でプロジェクトを削除
    for data in contractors_data:
        Project.objects.filter(contractor_name=data['name']).delete()

    print("新しい受注業者を作成...")
    contractors = []
    for data in contractors_data:
        contractor = Contractor.objects.create(**data)
        contractors.append(contractor)
        print(f"  ✓ {contractor.name} を作成しました")

    # 2. 各業者に対してプロジェクトを作成（過去12ヶ月分）
    print("\nプロジェクトデータを作成...")

    project_counter = 1000  # 管理番号用カウンター
    now = datetime.now()

    for contractor in contractors:
        # 業者ごとに異なる数のプロジェクトを作成
        num_projects = random.randint(8, 25)  # 月あたり平均1-2件

        for i in range(num_projects):
            # ランダムな日付（過去12ヶ月以内）
            days_ago = random.randint(0, 365)
            project_date = now - timedelta(days=days_ago)

            # 見積金額をランダムに設定（業者の専門性に応じて）
            if '建築' in contractor.specialties:
                min_amount = 5000000
                max_amount = 20000000
            elif '電気' in contractor.specialties:
                min_amount = 1000000
                max_amount = 8000000
            elif '設備' in contractor.specialties:
                min_amount = 2000000
                max_amount = 10000000
            elif '塗装' in contractor.specialties:
                min_amount = 800000
                max_amount = 5000000
            else:  # 内装
                min_amount = 500000
                max_amount = 4000000

            estimate_amount = Decimal(random.randint(min_amount, max_amount))

            # プロジェクトを作成
            project = Project.objects.create(
                management_no=f'P{project_counter:04d}',
                site_name=f'{contractor.name.split("株式会社")[0].split("工")[0]}案件{i+1}',
                site_address=f'テスト県{random.choice(["デモ市", "架空市", "サンプル市"])}ダミー町{i}-{j}-{k}',
                work_type=contractor.specialties.split('、')[0],
                order_status='受注',
                contractor_name=contractor.name,  # 業者名を設定
                estimate_issued_date=project_date.date(),
                estimate_amount=estimate_amount,
                created_at=project_date,
                updated_at=project_date
            )

            # created_atを強制的に設定（auto_now_addを上書き）
            Project.objects.filter(pk=project.pk).update(created_at=project_date)

            project_counter += 1

        print(f"  ✓ {contractor.name} に {num_projects} 件のプロジェクトを作成しました")

    # 3. 統計情報を表示
    print("\n=== データ作成完了 ===")
    print(f"受注業者数: {len(contractors)}")

    for contractor in contractors:
        projects = Project.objects.filter(contractor_name=contractor.name)
        total_amount = sum(p.estimate_amount for p in projects)
        print(f"\n{contractor.name}:")
        print(f"  - プロジェクト数: {projects.count()}")
        print(f"  - 総売上: ¥{total_amount:,}")

        # 月別集計
        monthly_data = {}
        for project in projects:
            month_key = project.created_at.strftime('%Y/%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += project.estimate_amount

        if monthly_data:
            sorted_months = sorted(monthly_data.items())[-3:]  # 直近3ヶ月
            print(f"  - 直近の売上:")
            for month, amount in sorted_months:
                print(f"    {month}: ¥{amount:,}")

if __name__ == '__main__':
    print("業者管理ダッシュボード用テストデータを作成します...")
    create_test_data()
    print("\n✅ 完了しました！")
    print("http://localhost:8000/orders/contractor-dashboard/ でダッシュボードを確認してください。")