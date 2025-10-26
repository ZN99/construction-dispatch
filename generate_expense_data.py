#!/usr/bin/env python
"""
出金データ（発生・実績）と買掛金のダミーデータ生成スクリプト
"""
import os
import django
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth.models import User
from order_management.models import Project, CashFlowTransaction

def generate_expense_transactions():
    """
    出金取引データを生成
    - expense_accrual: 発生主義の支出（発注時点）
    - expense_cash: 現金主義の支出（実際の出金）
    """
    print("\n" + "=" * 60)
    print("出金データ生成開始")
    print("=" * 60)

    user = User.objects.first()
    if not user:
        print("❌ ユーザーが存在しません")
        return

    # 進行中または完工のプロジェクトを取得
    projects = list(Project.objects.filter(
        project_status__in=['進行中', '完工', '施工日待ち']
    )[:40])  # 40件のプロジェクトに対して出金データを生成

    if not projects:
        print("❌ 対象プロジェクトが見つかりません")
        return

    print(f"\n対象プロジェクト: {len(projects)}件")

    expense_transactions = []
    today = date.today()

    # 業者リスト（外注先・資材業者）
    suppliers = [
        "株式会社山田建材",
        "鈴木工業",
        "佐藤電気工事",
        "田中設備",
        "高橋塗装",
        "伊藤タイル工業",
        "渡辺左官",
        "中村建設資材",
        "小林機械リース",
        "加藤運送"
    ]

    for project in projects:
        # プロジェクトの受注金額から原価を計算（原価率60-80%）
        order_amount = project.order_amount or Decimal('5000000')
        cost_rate = Decimal(str(random.uniform(0.6, 0.8)))
        total_cost = order_amount * cost_rate

        # コストを複数の支出に分割（材料費、外注費、その他）
        num_expenses = random.randint(3, 8)  # 1プロジェクトあたり3-8件の支出

        # 基準日（契約日または今日から遡る）
        if project.contract_date:
            base_date = project.contract_date
        else:
            base_date = today - timedelta(days=random.randint(30, 180))

        for i in range(num_expenses):
            # 支出金額（総原価を分割）
            if i == num_expenses - 1:
                # 最後は残額
                amount = total_cost
            else:
                # ランダムに10-40%ずつ
                ratio = Decimal(str(random.uniform(0.10, 0.40)))
                amount = (total_cost * ratio).quantize(Decimal('1'))
                total_cost -= amount

            # 発生日（発注日）: 基準日から0-90日後
            accrual_date = base_date + timedelta(days=random.randint(0, 90))

            # 実際の出金日: 発生日から15-60日後
            cash_date = accrual_date + timedelta(days=random.randint(15, 60))

            # 業者名
            supplier = random.choice(suppliers)

            # 説明
            expense_types = [
                "材料費（資材購入）",
                "外注費（工事委託）",
                "設備費",
                "運搬費",
                "機材リース費"
            ]
            description = f"{supplier} - {random.choice(expense_types)}"

            # 1. 発生主義の支出取引（発注時点）
            expense_accrual = CashFlowTransaction(
                project=project,
                transaction_type='expense_accrual',
                amount=amount,
                transaction_date=accrual_date,
                is_planned=False,
                description=f"{description}（発生）"
            )
            expense_transactions.append(expense_accrual)

            # 2. 実際の出金取引
            # 50%の確率で既に出金済み、50%で予定
            is_paid = cash_date <= today or random.random() < 0.5

            expense_cash = CashFlowTransaction(
                project=project,
                transaction_type='expense_cash',
                amount=amount,
                transaction_date=cash_date,
                is_planned=not is_paid,
                description=f"{description}（{'実績' if is_paid else '予定'}）"
            )
            expense_transactions.append(expense_cash)

    # 一括保存
    CashFlowTransaction.objects.bulk_create(expense_transactions, ignore_conflicts=True)

    print(f"\n✅ 出金取引データ生成完了: {len(expense_transactions)}件")

    # 統計情報
    accrual_count = len([t for t in expense_transactions if t.transaction_type == 'expense_accrual'])
    cash_count = len([t for t in expense_transactions if t.transaction_type == 'expense_cash'])
    paid_count = len([t for t in expense_transactions if t.transaction_type == 'expense_cash' and not t.is_planned])
    planned_count = len([t for t in expense_transactions if t.transaction_type == 'expense_cash' and t.is_planned])

    total_accrual = sum(t.amount for t in expense_transactions if t.transaction_type == 'expense_accrual')
    total_cash = sum(t.amount for t in expense_transactions if t.transaction_type == 'expense_cash' and not t.is_planned)

    print(f"\n📊 統計:")
    print(f"   発生主義支出: {accrual_count}件 (¥{total_accrual:,.0f})")
    print(f"   現金支出（実績）: {paid_count}件 (¥{total_cash:,.0f})")
    print(f"   現金支出（予定）: {planned_count}件")

def check_balance():
    """収支バランスを確認"""
    print("\n" + "=" * 60)
    print("収支バランス確認")
    print("=" * 60)

    # 発生主義
    revenue_accrual = CashFlowTransaction.objects.filter(
        transaction_type='revenue_accrual'
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    expense_accrual = CashFlowTransaction.objects.filter(
        transaction_type='expense_accrual'
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    print(f"\n発生主義ベース:")
    print(f"   売上（発生）: ¥{revenue_accrual:,.0f}")
    print(f"   支出（発生）: ¥{expense_accrual:,.0f}")
    print(f"   純利益: ¥{(revenue_accrual - expense_accrual):,.0f}")
    print(f"   利益率: {((revenue_accrual - expense_accrual) / revenue_accrual * 100) if revenue_accrual > 0 else 0:.1f}%")

    # 現金主義
    revenue_cash = CashFlowTransaction.objects.filter(
        transaction_type='revenue_cash',
        is_planned=False
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    expense_cash = CashFlowTransaction.objects.filter(
        transaction_type='expense_cash',
        is_planned=False
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    print(f"\n現金主義ベース:")
    print(f"   入金（実績）: ¥{revenue_cash:,.0f}")
    print(f"   出金（実績）: ¥{expense_cash:,.0f}")
    print(f"   純キャッシュフロー: ¥{(revenue_cash - expense_cash):,.0f}")

    # 売掛金・買掛金
    receivable = CashFlowTransaction.objects.filter(
        transaction_type='revenue_cash',
        is_planned=True
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    payable = CashFlowTransaction.objects.filter(
        transaction_type='expense_cash',
        is_planned=True
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    print(f"\n予定:")
    print(f"   売掛金（入金予定）: ¥{receivable:,.0f}")
    print(f"   買掛金（出金予定）: ¥{payable:,.0f}")

def main():
    from django.db import models

    print("\n" + "🚀 出金データ・買掛金ダミーデータ生成")
    print("=" * 60)

    # 既存データ確認
    existing_expense = CashFlowTransaction.objects.filter(
        transaction_type__in=['expense_accrual', 'expense_cash']
    ).count()

    print(f"\n既存の出金データ: {existing_expense}件")

    if existing_expense > 0:
        print("既存の出金データはそのまま追加生成します")

    # データ生成
    generate_expense_transactions()

    # 収支確認
    check_balance()

    print("\n" + "=" * 60)
    print("🎉 完了！")
    print("=" * 60)
    print("\n次のステップ:")
    print("1. http://127.0.0.1:8000/orders/cashflow/ でキャッシュフロー確認")
    print("2. 発生主義と現金主義の違いを確認")
    print("3. 売掛金・買掛金の残高を確認")

if __name__ == '__main__':
    main()
