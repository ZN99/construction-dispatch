#!/usr/bin/env python3
"""
現場調査員用のユーザーアカウントを作成するスクリプト

使用方法:
python create_field_surveyor_accounts.py

このスクリプトは既存の調査員（Surveyor）に対してユーザーアカウントを作成し、
現場調査員システムにログインできるようにします。
"""

import os
import sys
import django

# Djangoの設定を読み込む
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth.models import User
from surveys.models import Surveyor


def create_field_surveyor_accounts():
    """調査員にユーザーアカウントを作成"""

    print("現場調査員用ユーザーアカウント作成ツール")
    print("=" * 50)

    # 既存の調査員を取得
    surveyors = Surveyor.objects.filter(is_active=True)

    if not surveyors.exists():
        print("❌ 調査員が登録されていません。")
        print("   まず調査員を登録してからこのスクリプトを実行してください。")
        return

    print(f"📊 有効な調査員: {surveyors.count()}名")
    print()

    created_count = 0
    updated_count = 0

    for surveyor in surveyors:
        print(f"処理中: {surveyor.name} ({surveyor.employee_id})")

        # 既にユーザーアカウントが関連付けられている場合
        if surveyor.user:
            print(f"  ✅ 既にアカウントが存在: {surveyor.user.username}")
            continue

        # 社員番号をユーザー名として使用
        username = surveyor.employee_id

        # 既存のユーザー名チェック
        if User.objects.filter(username=username).exists():
            print(f"  ⚠️  ユーザー名「{username}」は既に使用されています")
            # 代替案: surveyor_ + employee_id
            username = f"surveyor_{surveyor.employee_id}"
            if User.objects.filter(username=username).exists():
                print(f"  ❌ 代替ユーザー名「{username}」も使用済みです")
                continue

        # パスワード生成（初期パスワード: 社員番号 + "2024"）
        initial_password = f"{surveyor.employee_id}2024"

        try:
            # ユーザーアカウント作成
            user = User.objects.create_user(
                username=username,
                email=surveyor.email or f"{username}@company.com",
                password=initial_password,
                first_name=surveyor.name,
                is_staff=False,  # 一般ユーザー（管理者ではない）
                is_active=True
            )

            # 調査員とユーザーを関連付け
            surveyor.user = user
            surveyor.save()

            print(f"  ✅ アカウント作成完了")
            print(f"     ユーザー名: {username}")
            print(f"     初期パスワード: {initial_password}")
            print(f"     ログインURL: http://localhost:8000/surveys/field/login/")

            created_count += 1

        except Exception as e:
            print(f"  ❌ エラー: {str(e)}")

    print()
    print("=" * 50)
    print(f"📈 処理結果:")
    print(f"   新規作成: {created_count}アカウント")
    print(f"   既存: {surveyors.count() - created_count}アカウント")
    print()

    if created_count > 0:
        print("🔐 セキュリティ注意事項:")
        print("   1. 初期パスワードは「社員番号+2024」です")
        print("   2. 調査員に初回ログイン時のパスワード変更を推奨してください")
        print("   3. 本番環境では安全なパスワードポリシーを実装してください")
        print()

        print("🌐 アクセス方法:")
        print("   現場調査員システム: http://localhost:8000/surveys/field/login/")
        print("   本部システム: http://localhost:8000/orders/")


if __name__ == "__main__":
    create_field_surveyor_accounts()