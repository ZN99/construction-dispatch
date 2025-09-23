#!/usr/bin/env python3
"""
本番環境用のユーザーアカウント作成スクリプト

使用方法:
python create_production_users.py

本番環境でのデプロイ後に実行して、必要なユーザーアカウントを作成します。
"""

import os
import sys
import django

# Djangoの設定を読み込む
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth.models import User
from surveys.models import Surveyor


def create_production_users():
    """本番環境用のユーザーアカウントを作成"""

    print("本番環境用ユーザーアカウント作成ツール")
    print("=" * 50)

    # 1. スーパーユーザー（admin）
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@company.com',
            password='admin123',
            first_name='管理者',
            last_name='システム'
        )
        print("✅ スーパーユーザー 'admin' を作成しました")
        print("   ユーザー名: admin")
        print("   パスワード: admin123")
    else:
        print("✅ スーパーユーザー 'admin' は既に存在します")

    # 2. 本部管理者ユーザー
    if not User.objects.filter(username='headquarters').exists():
        headquarters_user = User.objects.create_user(
            username='headquarters',
            email='headquarters@company.com',
            password='headquarters123',
            first_name='本部',
            last_name='管理者',
            is_staff=True,
            is_active=True
        )
        print("✅ 本部管理者 'headquarters' を作成しました")
        print("   ユーザー名: headquarters")
        print("   パスワード: headquarters123")
    else:
        print("✅ 本部管理者 'headquarters' は既に存在します")

    # 3. 調査員ユーザー
    surveyors_data = [
        {
            'name': '田中 太郎',
            'employee_id': 'S001',
            'username': 'tanaka',
            'email': 'tanaka@company.com',
            'phone': '090-1111-0001'
        },
        {
            'name': '佐藤 花子',
            'employee_id': 'S002',
            'username': 'sato',
            'email': 'sato@company.com',
            'phone': '090-1111-0002'
        },
        {
            'name': '山田 次郎',
            'employee_id': 'S003',
            'username': 'S003',
            'email': 'yamada@company.com',
            'phone': '090-1111-0003'
        },
        {
            'name': '鈴木 美穂',
            'employee_id': 'S004',
            'username': 'S004',
            'email': 'suzuki@company.com',
            'phone': '090-1111-0004'
        }
    ]

    print("\n--- 調査員ユーザー作成 ---")

    for surveyor_data in surveyors_data:
        # ユーザーアカウント作成
        username = surveyor_data['username']
        password = f"{surveyor_data['employee_id']}2024"

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=surveyor_data['email'],
                password=password,
                first_name=surveyor_data['name'].split()[1],
                last_name=surveyor_data['name'].split()[0],
                is_staff=False,
                is_active=True
            )
            print(f"✅ ユーザー '{username}' を作成しました")
        else:
            user = User.objects.get(username=username)
            print(f"✅ ユーザー '{username}' は既に存在します")

        # 調査員データ作成
        if not Surveyor.objects.filter(employee_id=surveyor_data['employee_id']).exists():
            surveyor = Surveyor.objects.create(
                name=surveyor_data['name'],
                employee_id=surveyor_data['employee_id'],
                email=surveyor_data['email'],
                phone=surveyor_data['phone'],
                user=user,
                is_active=True
            )
            print(f"   調査員データ '{surveyor.name}' を作成しました")
            print(f"   パスワード: {password}")
        else:
            print(f"   調査員データ '{surveyor_data['name']}' は既に存在します")

    print("\n" + "=" * 50)
    print("📈 本番環境セットアップ完了!")
    print("\n🔐 ログイン情報:")
    print("【Django管理画面】")
    print("   URL: /admin/")
    print("   ユーザー名: admin")
    print("   パスワード: admin123")
    print("\n【本部管理システム】")
    print("   URL: /orders/")
    print("   ユーザー名: headquarters")
    print("   パスワード: headquarters123")
    print("\n【現場調査システム】")
    print("   URL: /surveys/field/login/")
    for surveyor_data in surveyors_data:
        username = surveyor_data['username']
        password = f"{surveyor_data['employee_id']}2024"
        print(f"   {surveyor_data['name']}: {username} / {password}")

    print("\n⚠️  セキュリティ注意:")
    print("   本番環境では必ずパスワードを変更してください！")


if __name__ == "__main__":
    create_production_users()