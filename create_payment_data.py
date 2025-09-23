#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
出金（支払い）データ作成スクリプト
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Djangoの設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from order_management.models import Project
from subcontract_management.models import Subcontract, Contractor

def create_payment_data():
    """出金データを作成"""

    print("=" * 50)
    print("出金（支払い）データを作成します...")

    # 既存のプロジェクトを取得
    projects = Project.objects.filter(
        contractor_name__isnull=False
    ).exclude(
        contractor_name=''
    )[:30]  # 最初の30件に支払いデータを作成

    if not projects.exists():
        print("❌ プロジェクトが見つかりません")
        return

    print(f"📊 {projects.count()}件のプロジェクトに支払いデータを作成")

    payment_count = 0
    today = date.today()

    # 支払いパターン
    payment_patterns = [
        {'status': '支払済', 'days_offset': -30},  # 30日前に支払済
        {'status': '支払済', 'days_offset': -15},  # 15日前に支払済
        {'status': '支払予定', 'days_offset': 7},   # 7日後に支払予定
        {'status': '支払予定', 'days_offset': 15},  # 15日後に支払予定
        {'status': '支払予定', 'days_offset': 30},  # 30日後に支払予定
        {'status': '遅延', 'days_offset': -7},      # 7日前が期限（遅延）
        {'status': '遅延', 'days_offset': -14},     # 14日前が期限（遅延）
    ]

    for project in projects:
        # ランダムに支払いパターンを選択
        pattern = random.choice(payment_patterns)

        # 支払金額の計算（請求額の70-100%をランダムに）
        base_amount = project.billing_amount or project.estimate_amount or Decimal('0')
        if base_amount == 0:
            base_amount = Decimal(random.randint(300000, 2000000))

        payment_ratio = Decimal(random.randint(70, 100)) / Decimal('100')
        payment_amount = (base_amount * payment_ratio).quantize(Decimal('1'))

        # 支払日の設定
        payment_date = today + timedelta(days=pattern['days_offset'])

        # 実際の支払日（支払済の場合のみ）
        actual_payment_date = None
        if pattern['status'] == '支払済':
            actual_payment_date = payment_date

        # 支払いデータを作成（Subcontractがあればそこに記録）
        try:
            # 既存の下請け契約を取得または作成
            contractor, _ = Contractor.objects.get_or_create(
                name=project.contractor_name,
                defaults={
                    'contact_person': '担当者',
                    'phone': '03-0000-0000',
                    'email': f"{project.contractor_name.replace('株式会社', '').replace(' ', '')}@example.com",
                    'specialties': project.work_type or '一般工事',
                    'is_active': True
                }
            )

            subcontract, created = Subcontract.objects.get_or_create(
                project=project,
                contractor=contractor,
                defaults={
                    'contract_amount': payment_amount,
                    'billed_amount': payment_amount,
                    'payment_due_date': payment_date,
                    'payment_status': 'paid' if pattern['status'] == '支払済' else 'pending',
                    'work_description': project.work_type or '一般工事'
                }
            )

            # Subcontractの支払い情報を更新
            if not created:
                subcontract.billed_amount = payment_amount
                subcontract.payment_due_date = payment_date
                subcontract.payment_status = 'paid' if pattern['status'] == '支払済' else 'pending'

            # 支払済みの場合は支払日を設定
            if pattern['status'] == '支払済':
                subcontract.payment_date = payment_date

            subcontract.save()

            # プロジェクトに支払い情報を追加
            project.payment_amount = payment_amount
            project.payment_due_date = payment_date

            if actual_payment_date:
                project.payment_date = actual_payment_date
                project.payment_status = '支払済'
            elif pattern['status'] == '遅延':
                project.payment_status = '遅延'
            else:
                project.payment_status = '支払予定'

            project.save()

            payment_count += 1

            status_emoji = {
                '支払済': '✅',
                '支払予定': '📅',
                '遅延': '⚠️'
            }.get(pattern['status'], '❓')

            print(f"  {status_emoji} {project.site_name[:20]}... - ¥{payment_amount:,} ({pattern['status']})")

        except Exception as e:
            print(f"  ❌ エラー: {project.site_name} - {str(e)}")

    # 統計情報を表示
    print("\n" + "=" * 50)
    print("📊 支払いデータ作成結果:")
    print(f"  作成件数: {payment_count}件")

    # 支払い状況別の集計 (Subcontractから集計)
    paid_subcontracts = Subcontract.objects.filter(payment_status='paid')
    pending_subcontracts = Subcontract.objects.filter(payment_status='pending')

    # 遅延の判定
    today_date = date.today()
    delayed_subcontracts = Subcontract.objects.filter(
        payment_status='pending',
        payment_due_date__lt=today_date
    )

    paid_total = sum(s.billed_amount or 0 for s in paid_subcontracts)
    scheduled_total = sum(s.billed_amount or 0 for s in pending_subcontracts if not (s.payment_due_date and s.payment_due_date < today_date))
    delayed_total = sum(s.billed_amount or 0 for s in delayed_subcontracts)

    print(f"\n📈 支払い状況:")
    print(f"  ✅ 支払済: {paid_subcontracts.count()}件 (¥{paid_total:,})")
    print(f"  📅 支払予定: {pending_subcontracts.count() - delayed_subcontracts.count()}件 (¥{scheduled_total:,})")
    print(f"  ⚠️ 遅延: {delayed_subcontracts.count()}件 (¥{delayed_total:,})")
    print(f"  💰 合計: ¥{paid_total + scheduled_total + delayed_total:,}")

    print("\n✨ 出金データの作成が完了しました！")
    print("🌐 確認URL: http://localhost:8000/orders/payment/")


if __name__ == '__main__':
    create_payment_data()