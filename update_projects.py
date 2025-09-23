#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
賃貸住宅原状回復ダミープロジェクトデータを作成するスクリプト（架空のデータのみ）
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

# 賃貸原状回復ダミープロジェクトデータ
projects_data = [
    {
        'site_name': '【3LDK】新宿区田中様邸 グランドメゾン301号室',
        'site_address': '東京都新宿区西新宿1-2-3',
        'work_type': '原状回復',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/10',
        'contractor_name': '東京不動産管理株式会社',
        'contractor_address': '東京都渋谷区神南1-25-1',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/02/01',
        'work_end_date': '2025/02/07',
        'estimated_amount': '¥650,000'
    },
    {
        'site_name': '【2LDK】渋谷区佐藤様邸 パークハイツ502号室',
        'site_address': '東京都渋谷区恵比寿2-3-4',
        'work_type': '原状回復',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/15',
        'contractor_name': '都心不動産管理株式会社',
        'contractor_address': '東京都港区六本木1-3-1',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/03/01',
        'work_end_date': '2025/03/05',
        'estimated_amount': '¥480,000'
    },
    {
        'site_name': '【1LDK】世田谷区鈴木様邸 エスプラナード203号室',
        'site_address': '東京都世田谷区三軒茶屋3-4-5',
        'work_type': '原状回復',
        'order_status': '進行中',
        'estimate_issued_date': '2025/01/20',
        'contractor_name': '首都圏不動産管理株式会社',
        'contractor_address': '東京都世田谷区下北沢2-16-1',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/01/25',
        'work_end_date': '2025/01/28',
        'estimated_amount': '¥350,000'
    },
    {
        'site_name': '【3LDK】架空区テスト様邸 ダミーパレス705号室',
        'site_address': 'テスト県架空市サンプル町4-5-6',
        'work_type': '原状回復',
        'order_status': '進行中',
        'estimate_issued_date': '2025/01/05',
        'contractor_name': 'ダミー不動産',
        'contractor_address': 'サンプル県テスト市デモ区4-1-13',
        'payment_due_date': '2025/02/28',
        'work_start_date': '2025/01/20',
        'work_end_date': '2025/01/26',
        'estimated_amount': '¥720,000'
    },
    {
        'site_name': '【2DK】ホゲ区フガ様邸 ピヨマンション404号室',
        'site_address': 'ダミー県テスト市架空区5-6-7',
        'work_type': '原状回復',
        'order_status': '完了',
        'estimate_issued_date': '2025/01/01',
        'contractor_name': 'サンプル賃貸管理',
        'contractor_address': 'テスト県ダミー市サンプル町2-15-2',
        'payment_due_date': '2025/02/28',
        'work_start_date': '2025/01/15',
        'work_end_date': '2025/01/18',
        'estimated_amount': '¥380,000'
    },
    {
        'site_name': '【1K】フガ区ピヨ様邸 モケアパート105号室',
        'site_address': 'サンプル県架空市デモ町6-7-8',
        'work_type': '原状回復',
        'order_status': '完了',
        'estimate_issued_date': '2024/12/20',
        'contractor_name': 'テスト住宅管理',
        'contractor_address': 'ダミー県サンプル市テスト区4-8-33',
        'payment_due_date': '2025/01/31',
        'work_start_date': '2025/01/10',
        'work_end_date': '2025/01/12',
        'estimated_amount': '¥180,000'
    },
    {
        'site_name': '【2LDK】ピヨ区モケ様邸 ホゲハイツ802号室',
        'site_address': 'テスト県デモ市架空町7-8-9',
        'work_type': '原状回復',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/25',
        'contractor_name': 'ダミー賃貸サービス',
        'contractor_address': 'サンプル県架空市テスト町2-2-8',
        'payment_due_date': '2025/04/30',
        'work_start_date': '2025/03/01',
        'work_end_date': '2025/03/04',
        'estimated_amount': '¥420,000'
    },
    {
        'site_name': '【3DK】モケ区ポヨ様邸 フガレジデンス601号室',
        'site_address': 'ダミー県サンプル市デモ区8-9-10',
        'work_type': '原状回復',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/05',
        'contractor_name': 'サンプル不動産管理',
        'contractor_address': 'テスト県デモ市架空町6-10-1',
        'payment_due_date': '2025/04/30',
        'work_start_date': '2025/03/15',
        'work_end_date': '2025/03/20',
        'estimated_amount': '¥580,000'
    },
    {
        'site_name': '【1LDK】ポヨ区ホゲ様邸 ピヨビル303号室',
        'site_address': 'サンプル県テスト市架空区9-10-11',
        'work_type': '原状回復',
        'order_status': '完了',
        'estimate_issued_date': '2024/11/15',
        'contractor_name': 'デモ管理サービス',
        'contractor_address': 'ダミー県サンプル市テスト町2-7-3',
        'payment_due_date': '2025/01/31',
        'work_start_date': '2024/12/01',
        'work_end_date': '2024/12/03',
        'estimated_amount': '¥320,000'
    },
    {
        'site_name': '【4LDK】デモ区架空様邸 サンプルタワー1205号室',
        'site_address': 'テスト県架空市サンプル町10-11-12',
        'work_type': '原状回復',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/30',
        'contractor_name': 'テストプロパティ管理',
        'contractor_address': 'ダミー県デモ市架空区2-2-2',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/02/10',
        'work_end_date': '2025/02/17',
        'estimated_amount': '¥850,000'
    },
    {
        'site_name': '【2K】サンプル区テスト様邸 ダミーコーポ201号室',
        'site_address': 'テスト県デモ市サンプル区3-3-3',
        'work_type': '原状回復',
        'order_status': '進行中',
        'estimate_issued_date': '2025/01/18',
        'contractor_name': 'ホゲ不動産管理',
        'contractor_address': 'ダミー県テスト市架空町3-3-3',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/01/22',
        'work_end_date': '2025/01/25',
        'estimated_amount': '¥280,000'
    },
    {
        'site_name': '【3LDK】テスト区デモ様邸 架空マンション908号室',
        'site_address': 'サンプル県デモ市テスト区4-4-4',
        'work_type': '原状回復',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/28',
        'contractor_name': 'フガ賃貸管理',
        'contractor_address': 'テスト県サンプル市デモ区4-4-4',
        'payment_due_date': '2025/04/30',
        'work_start_date': '2025/02/20',
        'work_end_date': '2025/02/26',
        'estimated_amount': '¥680,000'
    },
    {
        'site_name': '【1DK】架空区サンプル様邸 テストハイム107号室',
        'site_address': 'ダミー県架空市テスト町5-5-5',
        'work_type': '原状回復',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/01',
        'contractor_name': 'ピヨ不動産サービス',
        'contractor_address': 'サンプル県テスト市デモ区5-5-5',
        'payment_due_date': '2025/04/30',
        'work_start_date': '2025/03/05',
        'work_end_date': '2025/03/07',
        'estimated_amount': '¥220,000'
    },
    {
        'site_name': '【2LDK】デモ区ダミー様邸 サンプルビレッジ505号室',
        'site_address': 'テスト県架空市サンプル町6-6-6',
        'work_type': '原状回復',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/03',
        'contractor_name': 'モケ管理株式会社',
        'contractor_address': 'ダミー県デモ市架空区6-6-6',
        'payment_due_date': '2025/04/30',
        'work_start_date': '2025/03/10',
        'work_end_date': '2025/03/14',
        'estimated_amount': '¥450,000'
    },
    {
        'site_name': '【3LDK】ホゲ区フガ様邸 ピヨガーデン1102号室',
        'site_address': 'サンプル県テスト市架空区7-7-7',
        'work_type': '原状回復',
        'order_status': '完了',
        'estimate_issued_date': '2024/12/25',
        'contractor_name': 'ポヨ賃貸管理',
        'contractor_address': 'テスト県ダミー市サンプル町7-7-7',
        'payment_due_date': '2025/02/28',
        'work_start_date': '2025/01/08',
        'work_end_date': '2025/01/14',
        'estimated_amount': '¥750,000'
    }
]

def update_projects():
    """プロジェクトデータを更新"""
    print("=" * 50)
    print("ダミープロジェクトデータの作成を開始")
    print("=" * 50)

    # 既存のプロジェクトを削除（スクリプト実行時は自動で削除）
    print("既存のプロジェクトデータを削除します...")
    Project.objects.all().delete()
    print("既存のプロジェクトデータを削除しました")

    print("ダミープロジェクトデータを生成中...")

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
            estimate_amount=parse_amount(data['estimated_amount'])
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