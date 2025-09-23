#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ダミープロジェクトデータを作成するスクリプト（架空のデータのみ）
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from order_management.models import Project, ProgressStepTemplate, ProjectProgressStep
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def parse_date(date_str):
    """日付文字列をdateオブジェクトに変換"""
    if not date_str or date_str == '' or date_str == 'null':
        return None
    try:
        # 2025/06/10 形式
        if '/' in date_str:
            return datetime.strptime(date_str, '%Y/%m/%d').date()
        return None
    except:
        return None

def parse_amount(amount_str):
    """金額文字列をDecimalに変換"""
    if not amount_str or amount_str == '' or amount_str == '¥0':
        return Decimal('0')
    try:
        # ¥記号とカンマを除去
        cleaned = amount_str.replace('¥', '').replace(',', '').replace('-', '')
        return Decimal(cleaned)
    except:
        return Decimal('0')

# ダミープロジェクトデータ（架空の企業と場所）
projects_data = [
    {
        'site_name': '住宅A リビング改修工事',
        'site_address': 'テスト県デモ市サンプル町1-2-3',
        'work_type': '内装',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/10',
        'contractor_name': 'サンプル工務店',
        'contractor_address': 'ダミー県テスト市架空町1-25-1',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/02/01',
        'work_end_date': '2025/03/20',
        'estimated_amount': '¥1,500,000'
    },
    {
        'site_name': '戸建住宅B 外壁塗装工事',
        'site_address': 'ダミー県架空市テスト町2-3-4',
        'work_type': '塗装',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/15',
        'contractor_name': 'デモ建設有限会社',
        'contractor_address': 'テスト県サンプル市デモ区1-3-1',
        'payment_due_date': '2025/06/30',
        'work_start_date': '2025/03/01',
        'work_end_date': '2025/05/31',
        'estimated_amount': '¥2,800,000'
    },
    {
        'site_name': 'マンションC 共用部改修工事',
        'site_address': 'サンプル県デモ市テスト区3-4-5',
        'work_type': '総合',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/20',
        'contractor_name': 'テスト建設株式会社',
        'contractor_address': 'ダミー県サンプル市架空町2-16-1',
        'payment_due_date': '2025/05/31',
        'work_start_date': '2025/03/15',
        'work_end_date': '2025/05/15',
        'estimated_amount': '¥3,500,000'
    },
    {
        'site_name': '店舗D 内装リニューアル工事',
        'site_address': 'テスト県架空市サンプル町4-5-6',
        'work_type': '内装',
        'order_status': '進行中',
        'estimate_issued_date': '2025/01/05',
        'contractor_name': 'ダミー工務店',
        'contractor_address': 'サンプル県テスト市デモ区4-1-13',
        'payment_due_date': '2025/04/30',
        'work_start_date': '2025/01/20',
        'work_end_date': '2025/04/20',
        'estimated_amount': '¥2,200,000'
    },
    {
        'site_name': '事務所E 空調設備更新工事',
        'site_address': 'ダミー県テスト市架空区5-6-7',
        'work_type': '設備',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/01',
        'contractor_name': 'サンプル設備株式会社',
        'contractor_address': 'テスト県ダミー市サンプル町2-15-2',
        'payment_due_date': '2025/04/30',
        'work_start_date': '2025/02/15',
        'work_end_date': '2025/04/15',
        'estimated_amount': '¥1,800,000'
    },
    {
        'site_name': 'アパートF 屋上防水工事',
        'site_address': 'サンプル県架空市デモ町6-7-8',
        'work_type': '防水',
        'order_status': '進行中',
        'estimate_issued_date': '2024/12/20',
        'contractor_name': 'テスト防水工業',
        'contractor_address': 'ダミー県サンプル市テスト区4-8-33',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/01/10',
        'work_end_date': '2025/03/10',
        'estimated_amount': '¥1,650,000'
    },
    {
        'site_name': '住宅G キッチン改修工事',
        'site_address': 'テスト県デモ市架空町7-8-9',
        'work_type': 'リフォーム',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/25',
        'contractor_name': 'ダミーリフォーム合同会社',
        'contractor_address': 'サンプル県架空市テスト町2-2-8',
        'payment_due_date': '2025/05/31',
        'work_start_date': '2025/03/01',
        'work_end_date': '2025/04/30',
        'estimated_amount': '¥950,000'
    },
    {
        'site_name': 'ビルH エントランス改修工事',
        'site_address': 'ダミー県サンプル市デモ区8-9-10',
        'work_type': '内装',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/05',
        'contractor_name': 'サンプル内装株式会社',
        'contractor_address': 'テスト県デモ市架空町6-10-1',
        'payment_due_date': '2025/06/30',
        'work_start_date': '2025/03/15',
        'work_end_date': '2025/06/15',
        'estimated_amount': '¥2,400,000'
    },
    {
        'site_name': '倉庫I 床面補修工事',
        'site_address': 'サンプル県テスト市架空区9-10-11',
        'work_type': '土木',
        'order_status': '完了',
        'estimate_issued_date': '2024/11/15',
        'contractor_name': 'デモ土木工業',
        'contractor_address': 'ダミー県サンプル市テスト町2-7-3',
        'payment_due_date': '2025/01/31',
        'work_start_date': '2024/12/01',
        'work_end_date': '2025/01/15',
        'estimated_amount': '¥1,350,000'
    },
    {
        'site_name': '店舗J 看板設置工事',
        'site_address': 'テスト県架空市サンプル町10-11-12',
        'work_type': 'サイン',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/30',
        'contractor_name': 'テストサイン工業',
        'contractor_address': 'ダミー県デモ市架空区2-2-2',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/02/10',
        'work_end_date': '2025/03/10',
        'estimated_amount': '¥750,000'
    }
]

def update_projects():
    """プロジェクトデータを更新"""
    print("=" * 50)
    print("ダミープロジェクトデータの作成を開始")
    print("=" * 50)

    # 既存のプロジェクトを削除（オプション）
    if input("既存のプロジェクトデータを削除しますか？ (y/n): ").lower() == 'y':
        Project.objects.all().delete()
        print("既存のプロジェクトデータを削除しました")

    # スーパーユーザーを取得または作成
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@demo.example.com',
            'is_superuser': True,
            'is_staff': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("管理者ユーザーを作成しました")

    # プロジェクトを作成
    for idx, data in enumerate(projects_data, 1):
        management_no = f"DEMO-{idx:04d}"

        project = Project.objects.create(
            management_no=management_no,
            site_name=data['site_name'],
            site_address=data['site_address'],
            work_type=data['work_type'],
            order_status=data['order_status'],
            estimate_issued_date=parse_date(data['estimate_issued_date']),
            contractor_name=data['contractor_name'],
            contractor_address=data['contractor_address'],
            payment_due_date=parse_date(data['payment_due_date']),
            work_start_date=parse_date(data['work_start_date']),
            work_end_date=parse_date(data['work_end_date']),
            estimated_amount=parse_amount(data['estimated_amount']),
            created_by=admin_user,
            updated_by=admin_user
        )

        print(f"作成: {management_no} - {data['site_name']}")

        # 進行ステップを作成
        if ProgressStepTemplate.objects.exists():
            templates = ProgressStepTemplate.objects.all().order_by('order')
            for template in templates:
                # ステータスに応じて完了状態を設定
                if data['order_status'] == '完了':
                    is_completed = True
                elif data['order_status'] == '進行中':
                    is_completed = random.choice([True, False])
                else:
                    is_completed = False

                ProjectProgressStep.objects.create(
                    project=project,
                    template=template,
                    is_completed=is_completed,
                    completed_date=timezone.now() if is_completed else None
                )

    print("=" * 50)
    print(f"合計 {len(projects_data)} 件のダミープロジェクトを作成しました")
    print("=" * 50)

if __name__ == '__main__':
    update_projects()