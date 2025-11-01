#!/usr/bin/env python
"""
本番環境用ユーザー作成スクリプト

Usage:
    python setup_production_users.py

このスクリプトは以下のユーザーを作成/更新します：
- superadmin: 全システムアクセス可能な管理者
- sato: 現地調査員
- tanaka: 現地調査員
"""
import os
import sys
import django

# Django setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth.models import User

def create_production_users():
    """本番環境用のユーザーを作成"""

    print("=" * 70)
    print("本番環境用ユーザー作成")
    print("=" * 70)

    users_to_create = [
        {
            'username': 'superadmin',
            'email': 'admin@construction.com',
            'password': 'ConstructionAdmin2024!',
            'first_name': 'Super',
            'last_name': 'Admin',
            'is_superuser': True,
            'is_staff': True,
            'role': '【管理者】全システムアクセス可能'
        },
        {
            'username': 'sato',
            'email': 'sato@construction.com',
            'password': 'Survey2024!',
            'first_name': '花子',
            'last_name': '佐藤',
            'is_superuser': False,
            'is_staff': False,
            'role': '【調査員】現地調査システム用'
        },
        {
            'username': 'tanaka',
            'email': 'tanaka@construction.com',
            'password': 'Survey2024!',
            'first_name': '太郎',
            'last_name': '田中',
            'is_superuser': False,
            'is_staff': False,
            'role': '【調査員】現地調査システム用'
        }
    ]

    print("\n作成/更新するユーザー:\n")

    for user_data in users_to_create:
        username = user_data['username']

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            print(f"⚠️  既存ユーザー更新: {username}")
        else:
            user = User()
            print(f"✨ 新規ユーザー作成: {username}")

        user.username = username
        user.email = user_data['email']
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.is_superuser = user_data['is_superuser']
        user.is_staff = user_data['is_staff']
        user.is_active = True
        user.set_password(user_data['password'])
        user.save()

        print(f"   ID: {username}")
        print(f"   パスワード: {user_data['password']}")
        print(f"   役割: {user_data['role']}\n")

    print("=" * 70)
    print("✅ 全ユーザー作成/更新完了")
    print("=" * 70)

if __name__ == '__main__':
    create_production_users()
