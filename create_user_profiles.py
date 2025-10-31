#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全ユーザーにUserProfileを作成し、適切なロールを割り当てる
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth.models import User
from order_management.models import UserProfile
from order_management.user_roles import UserRole


def create_user_profiles():
    """全ユーザーにUserProfileを作成"""
    print("=== 👥 UserProfile作成開始 ===\n")

    created_count = 0
    updated_count = 0

    # 全ユーザーを取得
    users = User.objects.all()

    for user in users:
        profile, created = UserProfile.objects.get_or_create(user=user)

        if created:
            print(f"✅ 作成: {user.username} ({user.get_full_name() or '名前未設定'})")
            created_count += 1
        else:
            print(f"ℹ️  既存: {user.username} ({user.get_full_name() or '名前未設定'})")
            updated_count += 1

    print(f"\n📊 結果:")
    print(f"  新規作成: {created_count}件")
    print(f"  既存: {updated_count}件")
    print(f"  合計: {created_count + updated_count}件")

    return created_count


def assign_default_roles():
    """主要ユーザーにデフォルトロールを割り当て"""
    print("\n=== 🎭 ロール割り当て開始 ===\n")

    role_assignments = {
        # 管理者・スタッフ
        'admin': [UserRole.EXECUTIVE],  # 役員権限
        'headquarters': [UserRole.EXECUTIVE, UserRole.ACCOUNTING],  # 役員+経理

        # 一般スタッフ（例として）
        'tanaka': [UserRole.SALES],  # 営業
        'sato': [UserRole.ACCOUNTING],  # 経理
        'watanabe_k': [UserRole.WORKER_DISPATCH],  # 職人発注
        'taniguchi_m': [UserRole.SALES],  # 営業
        'ito_h': [UserRole.WORKER_DISPATCH],  # 職人発注
    }

    assigned_count = 0

    for username, roles in role_assignments.items():
        try:
            user = User.objects.get(username=username)
            profile, _ = UserProfile.objects.get_or_create(user=user)

            # ロールを設定（既存のロールは保持）
            if not profile.roles:
                profile.roles = []

            # 新しいロールを追加（重複を避ける）
            for role in roles:
                if role not in profile.roles:
                    profile.roles.append(role)

            profile.save()

            roles_display = ', '.join(roles)
            print(f"✅ {username}: {roles_display}")
            assigned_count += 1

        except User.DoesNotExist:
            print(f"⚠️  ユーザーが見つかりません: {username}")

    print(f"\n📊 ロール割り当て: {assigned_count}件")
    return assigned_count


def display_role_summary():
    """ロール別ユーザー数を表示"""
    print("\n=== 📊 ロール別集計 ===\n")

    profiles = UserProfile.objects.all()

    role_counts = {
        UserRole.SALES: 0,
        UserRole.WORKER_DISPATCH: 0,
        UserRole.ACCOUNTING: 0,
        UserRole.EXECUTIVE: 0,
    }

    no_role_count = 0

    for profile in profiles:
        if not profile.roles:
            no_role_count += 1
            continue

        for role in profile.roles:
            if role in role_counts:
                role_counts[role] += 1

    for role, name in UserRole.CHOICES:
        count = role_counts.get(role, 0)
        print(f"  • {name}: {count}人")

    print(f"  • ロール未設定: {no_role_count}人")
    print(f"\n  総UserProfile数: {profiles.count()}件")


def main():
    print("=" * 60)
    print("ユーザープロファイルとロールの設定")
    print("=" * 60)

    # 1. UserProfile作成
    created = create_user_profiles()

    # 2. ロール割り当て
    assigned = assign_default_roles()

    # 3. 集計表示
    display_role_summary()

    print("\n" + "=" * 60)
    print("✨ 完了")
    print("=" * 60)
    print(f"\n次のステップ:")
    print(f"  1. Django管理画面 (/admin/) でロールを確認・調整")
    print(f"  2. 必要に応じて他のユーザーにもロールを割り当て")


if __name__ == '__main__':
    main()
