#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
調査員データを作成するスクリプト
"""

import os
import sys
import django
from datetime import date

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from surveys.models import Surveyor

def create_surveyors():
    """調査員データを作成"""

    print("調査員データを作成中...")

    # 既存のユーザーを取得
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = None

    try:
        tanaka_user = User.objects.get(username='tanaka')
    except User.DoesNotExist:
        tanaka_user = None

    try:
        sato_user = User.objects.get(username='sato')
    except User.DoesNotExist:
        sato_user = None

    # 調査員データ
    surveyors_data = [
        {
            'name': '田中 太郎',
            'employee_id': 'S001',
            'email': 'tanaka@company.com',
            'phone': '080-1234-5678',
            'department': '建築調査部',
            'specialties': '建築調査, 耐震診断, 設備点検',
            'certifications': '一級建築士, 建築物調査員',
            'experience_years': 8,
            'hire_date': date(2016, 4, 1),
            'user': tanaka_user,
            'notes': 'チームリーダー。大型建築物の調査経験豊富。'
        },
        {
            'name': '佐藤 花子',
            'employee_id': 'S002',
            'email': 'sato@company.com',
            'phone': '080-2345-6789',
            'department': '設備調査部',
            'specialties': '設備調査, 電気設備点検, 空調設備診断',
            'certifications': '電気工事士, 建築設備士',
            'experience_years': 5,
            'hire_date': date(2019, 4, 1),
            'user': sato_user,
            'notes': '設備関係の専門家。精密な調査で定評あり。'
        },
        {
            'name': '山田 次郎',
            'employee_id': 'S003',
            'email': 'yamada@company.com',
            'phone': '080-3456-7890',
            'department': '土木調査部',
            'specialties': '土木調査, 構造診断, 地盤調査',
            'certifications': '技術士, 一級土木施工管理技士',
            'experience_years': 12,
            'hire_date': date(2012, 4, 1),
            'notes': 'ベテラン調査員。複雑な構造物の調査が得意。'
        },
        {
            'name': '鈴木 美穂',
            'employee_id': 'S004',
            'email': 'suzuki@company.com',
            'phone': '080-4567-8901',
            'department': '建築調査部',
            'specialties': '内装調査, 壁面診断, 防水調査',
            'certifications': '二級建築士, 建築仕上診断技術者',
            'experience_years': 3,
            'hire_date': date(2021, 4, 1),
            'notes': '新進気鋭の調査員。丁寧な作業が評価されている。'
        },
        {
            'name': '管理者',
            'employee_id': 'ADMIN',
            'email': 'admin@company.com',
            'phone': '080-0000-0000',
            'department': '管理部',
            'specialties': 'システム管理, 総合調査',
            'certifications': 'システム管理者',
            'experience_years': 15,
            'hire_date': date(2009, 4, 1),
            'user': admin_user,
            'notes': 'システム管理者兼ベテラン調査員。'
        }
    ]

    # 既存の調査員を削除
    Surveyor.objects.all().delete()

    # 新しい調査員を作成
    created_count = 0
    for data in surveyors_data:
        try:
            surveyor = Surveyor.objects.create(**data)
            created_count += 1
            print(f"✓ {surveyor.name} ({surveyor.employee_id})")
        except Exception as e:
            print(f"✗ {data['name']} の作成に失敗: {str(e)}")

    print(f"\n完了: {created_count}件の調査員を作成しました。")

if __name__ == '__main__':
    create_surveyors()