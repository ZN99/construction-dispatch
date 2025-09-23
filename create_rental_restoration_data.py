#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
賃貸住宅原状回復工事用のダミープロジェクトデータ作成スクリプト
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
        cleaned = amount_str.replace('¥', '').replace(',', '').replace('-', '')
        return Decimal(cleaned)
    except:
        return Decimal('0')

# リアルな地名リスト（実在しない組み合わせ）
areas = [
    '新宿区', '渋谷区', '世田谷区', '港区', '中央区',
    '千代田区', '目黒区', '品川区', '大田区', '杉並区'
]

# 一般的な姓リスト
last_names = [
    '田中', '佐藤', '鈴木', '高橋', '渡辺',
    '伊藤', '山本', '中村', '小林', '加藤',
    '吉田', '山田', '松本', '井上', '木村'
]

# 間取りリスト
room_types = [
    '1K', '1DK', '1LDK', '2K', '2DK', '2LDK',
    '3DK', '3LDK', '4LDK', '4SLDK'
]

# リアルなマンション名リスト
apartment_names = [
    'グランドメゾン', 'パークハイツ', 'エスプラナード',
    'レジデンス', 'ガーデンコート', 'プラザハウス',
    'シティタワー', 'ロイヤルマンション', 'グリーンヒルズ',
    'サンシャインハイム', 'オークランド', 'フォレストビュー'
]

# 工事内容リスト（原状回復に特化）
work_details = [
    'クロス張替え・クリーニング',
    '全面クリーニング・補修',
    'フローリング補修・クロス張替え',
    'キッチン・浴室クリーニング',
    '畳表替え・襖張替え',
    'エアコンクリーニング・消臭作業',
    'クロス全面張替え',
    '床補修・建具調整',
    '水回りクリーニング・コーキング打替え',
    'ベランダ防水・クリーニング'
]

def generate_projects_data():
    """賃貸原状回復プロジェクトデータを生成"""
    projects = []

    for i in range(50):  # 50件のダミーデータを生成
        area = random.choice(areas)
        last_name = random.choice(last_names)
        room_type = random.choice(room_types)
        apartment = random.choice(apartment_names)
        room_number = random.randint(101, 1205)
        work_detail = random.choice(work_details)

        # 金額を間取りに応じて設定
        if '1' in room_type:
            base_amount = random.randint(15, 35) * 10000
        elif '2' in room_type:
            base_amount = random.randint(25, 55) * 10000
        elif '3' in room_type:
            base_amount = random.randint(35, 75) * 10000
        else:
            base_amount = random.randint(45, 95) * 10000

        # 工期を設定（3日〜14日）
        work_days = random.randint(3, 14)

        # 日付を設定
        start_date = date.today() + timedelta(days=random.randint(-30, 30))
        end_date = start_date + timedelta(days=work_days)
        estimate_date = start_date - timedelta(days=random.randint(7, 21))
        payment_date = end_date + timedelta(days=30)

        # ステータスを決定
        if start_date > date.today():
            status = '受注'
        elif end_date < date.today():
            status = random.choice(['完了', '完了'])
        else:
            status = '進行中'

        project = {
            'site_name': f'【{room_type}】{area}{last_name}様邸 {apartment}{room_number}号室',
            'site_address': f'東京都{area}{random.randint(1,9)}-{random.randint(1,20)}-{random.randint(1,30)}',
            'work_type': '原状回復',
            'work_detail': work_detail,
            'order_status': status,
            'estimate_issued_date': estimate_date.strftime('%Y/%m/%d'),
            'contractor_name': f'{random.choice(["東京", "都心", "首都圏"])}不動産管理株式会社',
            'contractor_address': f'東京都{random.choice(areas)}{random.randint(1,9)}-{random.randint(1,20)}-{random.randint(1,30)}',
            'payment_due_date': payment_date.strftime('%Y/%m/%d'),
            'work_start_date': start_date.strftime('%Y/%m/%d'),
            'work_end_date': end_date.strftime('%Y/%m/%d'),
            'estimated_amount': f'¥{base_amount:,}'
        }

        projects.append(project)

    return projects

def create_rental_restoration_projects():
    """賃貸原状回復プロジェクトデータを作成"""
    print("=" * 50)
    print("賃貸原状回復ダミープロジェクトの作成を開始")
    print("=" * 50)

    # 既存のプロジェクトを削除（スクリプト実行時は自動で削除）
    print("既存のプロジェクトデータを削除します...")
    Project.objects.all().delete()
    print("既存のプロジェクトデータを削除しました")

    print("賃貸原状回復プロジェクトデータを生成中...")

    # プロジェクトデータを生成
    projects_data = generate_projects_data()

    # プロジェクトを作成
    for idx, data in enumerate(projects_data, 1):
        management_no = f"RR-{idx:05d}"  # RR = Rental Restoration

        # notesに工事詳細を追加
        notes = f"工事内容: {data['work_detail']}\n"
        notes += f"管理会社: {data['contractor_name']}\n"
        notes += "退去後の原状回復工事"

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
            estimate_amount=parse_amount(data['estimated_amount']),
            notes=notes
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
                    # 進行中の場合は一部完了
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
    print(f"合計 {len(projects_data)} 件の賃貸原状回復プロジェクトを作成しました")
    print("=" * 50)

    # サンプルデータを表示
    print("\n作成されたプロジェクトのサンプル:")
    for project in projects_data[:5]:
        print(f"  - {project['site_name']}")
        print(f"    工事: {project['work_detail']}")
        print(f"    金額: {project['estimated_amount']}")
        print()

if __name__ == '__main__':
    create_rental_restoration_projects()