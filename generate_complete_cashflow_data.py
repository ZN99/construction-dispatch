#!/usr/bin/env python
"""
完全なキャッシュフローダミーデータ生成スクリプト
- revenue_accrual: 完工時の売上計上（発生主義）
- revenue_cash: 実際の入金（現金主義）
- expense_accrual: コスト発生（発生主義）
- expense_cash: 実際の出金（現金主義）

リアルな会計データを生成:
1. 売上 > 支出 (利益率15-30%)
2. revenue_accrual ≈ sum(revenue_cash) for each project
3. expense_accrual < revenue_accrual (profit margin)
4. expense_cash ≈ expense_accrual (eventually paid)
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
from django.db import models
from order_management.models import Project, CashFlowTransaction


def clear_existing_data():
    """既存のキャッシュフローデータをクリア"""
    count = CashFlowTransaction.objects.all().count()
    if count > 0:
        print(f"\n既存のCashFlowTransactionデータ {count}件 を削除します...")
        CashFlowTransaction.objects.all().delete()
        print("✅ 削除完了")


def generate_revenue_transactions(projects):
    """
    売上データ生成
    各プロジェクトについて:
    1. revenue_accrual: 完工時に全額計上
    2. revenue_cash: 複数回に分けて入金（前金・中間・完工後）
    """
    transactions = []
    today = date.today()

    print("\n" + "=" * 60)
    print("売上データ生成")
    print("=" * 60)

    for project in projects:
        order_amount = project.order_amount or Decimal('5000000')

        # 完工日を決定
        if project.completion_date:
            completion_date = project.completion_date
        elif project.work_end_date:
            completion_date = project.work_end_date
        else:
            # ランダムに過去の日付
            completion_date = today - timedelta(days=random.randint(0, 120))

        # 1. 発生主義売上 (revenue_accrual) - 完工時に全額計上
        revenue_accrual = CashFlowTransaction(
            project=project,
            transaction_type='revenue_accrual',
            amount=order_amount,
            transaction_date=completion_date,
            is_planned=False,
            description=f"{project.client_name or 'お客様'} - 工事代金（発生）"
        )
        transactions.append(revenue_accrual)

        # 2. 現金主義売上 (revenue_cash) - 複数回に分けて入金
        # 入金パターン: 前金(30%) + 中間金(30%) + 残金(40%)
        payment_schedule = [
            {'ratio': 0.3, 'days_before_completion': 45, 'label': '前金'},
            {'ratio': 0.3, 'days_before_completion': 15, 'label': '中間金'},
            {'ratio': 0.4, 'days_after_completion': 30, 'label': '完工金'}
        ]

        for schedule in payment_schedule:
            amount = (order_amount * Decimal(str(schedule['ratio']))).quantize(Decimal('1'))

            # 入金日を決定
            if 'days_before_completion' in schedule:
                payment_date = completion_date - timedelta(days=schedule['days_before_completion'])
            else:
                payment_date = completion_date + timedelta(days=schedule['days_after_completion'])

            # 入金済みか予定か判定
            is_paid = payment_date <= today

            revenue_cash = CashFlowTransaction(
                project=project,
                transaction_type='revenue_cash',
                amount=amount,
                transaction_date=payment_date,
                is_planned=not is_paid,
                description=f"{project.client_name or 'お客様'} - {schedule['label']}入金{'（実績）' if is_paid else '（予定）'}"
            )
            transactions.append(revenue_cash)

    print(f"✅ 売上データ生成完了: {len(transactions)}件")
    return transactions


def generate_expense_transactions(projects):
    """
    支出データ生成
    各プロジェクトについて:
    1. expense_accrual: コスト発生（原価率70-85%）
    2. expense_cash: 実際の支払い
    """
    transactions = []
    today = date.today()

    print("\n" + "=" * 60)
    print("支出データ生成")
    print("=" * 60)

    # 業者リスト
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

    expense_categories = [
        "材料費（資材購入）",
        "外注費（工事委託）",
        "設備工事費",
        "運搬費",
        "機材リース費"
    ]

    for project in projects:
        order_amount = project.order_amount or Decimal('5000000')

        # 原価率: 70-85% (利益率 15-30%)
        cost_rate = Decimal(str(random.uniform(0.70, 0.85)))
        total_cost = (order_amount * cost_rate).quantize(Decimal('1'))

        # 工事開始日を決定
        if project.work_start_date:
            work_start = project.work_start_date
        elif project.contract_date:
            work_start = project.contract_date + timedelta(days=7)
        else:
            work_start = today - timedelta(days=random.randint(60, 150))

        # コストを複数の支出に分割（3-6件）
        num_expenses = random.randint(3, 6)
        remaining_cost = total_cost

        for i in range(num_expenses):
            # 最後は残額、それ以外はランダムに分割
            if i == num_expenses - 1:
                amount = remaining_cost
            else:
                ratio = Decimal(str(random.uniform(0.15, 0.35)))
                amount = (remaining_cost * ratio).quantize(Decimal('1'))
                remaining_cost -= amount

            supplier = random.choice(suppliers)
            category = random.choice(expense_categories)

            # 発生日: 工事開始から工事期間中にランダム
            accrual_offset = random.randint(0, 60)
            accrual_date = work_start + timedelta(days=accrual_offset)

            # 1. 発生主義支出 (expense_accrual)
            expense_accrual = CashFlowTransaction(
                project=project,
                transaction_type='expense_accrual',
                amount=amount,
                transaction_date=accrual_date,
                is_planned=False,
                description=f"{supplier} - {category}（発生）"
            )
            transactions.append(expense_accrual)

            # 2. 現金支出 (expense_cash) - 発生日から30-60日後に支払い
            payment_delay = random.randint(30, 60)
            cash_date = accrual_date + timedelta(days=payment_delay)

            # 支払い済みか予定か判定
            is_paid = cash_date <= today

            expense_cash = CashFlowTransaction(
                project=project,
                transaction_type='expense_cash',
                amount=amount,
                transaction_date=cash_date,
                is_planned=not is_paid,
                description=f"{supplier} - {category}{'（実績）' if is_paid else '（予定）'}"
            )
            transactions.append(expense_cash)

    print(f"✅ 支出データ生成完了: {len(transactions)}件")
    return transactions


def show_statistics():
    """データ統計を表示"""
    print("\n" + "=" * 60)
    print("生成データ統計")
    print("=" * 60)

    # 各トランザクションタイプの集計
    for ttype in ['revenue_accrual', 'revenue_cash', 'expense_accrual', 'expense_cash']:
        qs = CashFlowTransaction.objects.filter(transaction_type=ttype)
        total = qs.aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')
        count = qs.count()
        print(f"\n{ttype}:")
        print(f"  件数: {count}件")
        print(f"  合計: ¥{total:,.0f}")

        if ttype in ['revenue_cash', 'expense_cash']:
            actual = qs.filter(is_planned=False).count()
            planned = qs.filter(is_planned=True).count()
            actual_total = qs.filter(is_planned=False).aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')
            planned_total = qs.filter(is_planned=True).aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')
            print(f"    実績: {actual}件 (¥{actual_total:,.0f})")
            print(f"    予定: {planned}件 (¥{planned_total:,.0f})")

    # 発生主義ベースの収支
    revenue_accrual = CashFlowTransaction.objects.filter(
        transaction_type='revenue_accrual'
    ).aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')

    expense_accrual = CashFlowTransaction.objects.filter(
        transaction_type='expense_accrual'
    ).aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')

    profit_accrual = revenue_accrual - expense_accrual
    profit_rate = (profit_accrual / revenue_accrual * 100) if revenue_accrual > 0 else Decimal('0')

    print("\n" + "=" * 60)
    print("発生主義ベースの収支")
    print("=" * 60)
    print(f"売上（発生）:     ¥{revenue_accrual:,.0f}")
    print(f"支出（発生）:     ¥{expense_accrual:,.0f}")
    print(f"純利益:           ¥{profit_accrual:,.0f}")
    print(f"利益率:           {profit_rate:.1f}%")

    # 現金主義ベースの収支（実績のみ）
    revenue_cash = CashFlowTransaction.objects.filter(
        transaction_type='revenue_cash',
        is_planned=False
    ).aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')

    expense_cash = CashFlowTransaction.objects.filter(
        transaction_type='expense_cash',
        is_planned=False
    ).aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')

    net_cash = revenue_cash - expense_cash

    print("\n" + "=" * 60)
    print("現金主義ベースの収支（実績のみ）")
    print("=" * 60)
    print(f"入金（実績）:     ¥{revenue_cash:,.0f}")
    print(f"出金（実績）:     ¥{expense_cash:,.0f}")
    print(f"純キャッシュフロー: ¥{net_cash:,.0f}")

    # 売掛金・買掛金
    receivable = CashFlowTransaction.objects.filter(
        transaction_type='revenue_cash',
        is_planned=True
    ).aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')

    payable = CashFlowTransaction.objects.filter(
        transaction_type='expense_cash',
        is_planned=True
    ).aggregate(Sum=models.Sum('amount'))['Sum'] or Decimal('0')

    print("\n" + "=" * 60)
    print("売掛金・買掛金")
    print("=" * 60)
    print(f"売掛金（入金予定）: ¥{receivable:,.0f}")
    print(f"買掛金（出金予定）: ¥{payable:,.0f}")
    print(f"運転資本:           ¥{(receivable - payable):,.0f}")


def main():
    print("\n" + "🚀 完全なキャッシュフローダミーデータ生成")
    print("=" * 60)

    # 既存データをクリア
    clear_existing_data()

    # 対象プロジェクトを取得（完工、進行中、施工日待ち）
    projects = list(Project.objects.filter(
        project_status__in=['完工', '進行中', '施工日待ち']
    ).exclude(order_amount__isnull=True).exclude(order_amount=0)[:50])

    if not projects:
        print("❌ 対象プロジェクトが見つかりません")
        return

    print(f"\n対象プロジェクト: {len(projects)}件")

    # 売上データ生成
    revenue_transactions = generate_revenue_transactions(projects)

    # 支出データ生成
    expense_transactions = generate_expense_transactions(projects)

    # 一括保存
    all_transactions = revenue_transactions + expense_transactions
    print(f"\n保存中... {len(all_transactions)}件")
    CashFlowTransaction.objects.bulk_create(all_transactions, batch_size=500)
    print("✅ 保存完了")

    # 統計表示
    show_statistics()

    print("\n" + "=" * 60)
    print("🎉 完了！")
    print("=" * 60)
    print("\n次のステップ:")
    print("1. http://127.0.0.1:8000/orders/cashflow/ でキャッシュフロー確認")
    print("2. 発生主義と現金主義の違いを確認")
    print("3. 売掛金・買掛金の残高を確認")


if __name__ == '__main__':
    main()
