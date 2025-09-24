#!/usr/bin/env python
"""
Create realistic payment variations and paid projects
- Payment timing after work completion
- End-of-next-month payment patterns
- Various payment statuses
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random
import calendar

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, '/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch')
django.setup()

from django.utils import timezone
from order_management.models import Project

def get_month_end_date(year, month):
    """指定した年月の月末日を取得"""
    return datetime(year, month, calendar.monthrange(year, month)[1]).date()

def create_realistic_payment_schedule():
    """現実的な入金スケジュールを設定"""
    print("=" * 60)
    print("CREATING REALISTIC PAYMENT SCHEDULES")
    print("=" * 60)

    # 全プロジェクトを取得
    projects = Project.objects.filter(estimate_amount__gt=0)
    total_projects = projects.count()

    print(f"処理対象プロジェクト: {total_projects}件")

    # 入金パターンの定義
    payment_patterns = [
        {
            'name': '工事完了後翌月末払い',
            'weight': 40,
            'days_after_completion': lambda: random.randint(30, 35)  # 翌月末
        },
        {
            'name': '工事完了後当月末払い',
            'weight': 25,
            'days_after_completion': lambda: random.randint(10, 20)  # 当月末
        },
        {
            'name': '工事完了後15日以内',
            'weight': 20,
            'days_after_completion': lambda: random.randint(7, 15)
        },
        {
            'name': '工事完了後45日以内',
            'weight': 10,
            'days_after_completion': lambda: random.randint(35, 45)
        },
        {
            'name': '工事完了後即時',
            'weight': 5,
            'days_after_completion': lambda: random.randint(1, 5)
        }
    ]

    # 入金ステータスの分布
    payment_status_distribution = [
        ('scheduled', '入金予定', 50),    # 50%
        ('executed', '入金済み', 35),     # 35%
        ('overdue', '遅延', 15),          # 15%
    ]

    updated_count = 0
    paid_projects = []
    overdue_projects = []

    for project in projects:
        # 作業完了日を設定（まだない場合）
        if not project.work_end_date:
            # payment_due_dateから逆算して作業完了日を設定
            if project.payment_due_date:
                work_duration = random.randint(7, 21)  # 7-21日間の作業
                project.work_end_date = project.payment_due_date - timedelta(days=work_duration)
            else:
                # payment_due_dateもない場合は、現在から過去にランダム設定
                days_ago = random.randint(10, 90)
                project.work_end_date = timezone.now().date() - timedelta(days=days_ago)

        # 作業完了フラグを設定
        if not project.work_end_completed:
            if project.work_end_date <= timezone.now().date():
                project.work_end_completed = True

        # 入金パターンを選択
        pattern_choice = random.choices(
            payment_patterns,
            weights=[p['weight'] for p in payment_patterns]
        )[0]

        # 入金予定日を作業完了日ベースで設定
        if project.work_end_date:
            days_after = pattern_choice['days_after_completion']()
            new_payment_due_date = project.work_end_date + timedelta(days=days_after)

            # 翌月末払いの場合は月末に調整
            if pattern_choice['name'] == '工事完了後翌月末払い':
                next_month = new_payment_due_date.replace(day=1) + timedelta(days=32)
                new_payment_due_date = get_month_end_date(next_month.year, next_month.month)
            elif pattern_choice['name'] == '工事完了後当月末払い':
                new_payment_due_date = get_month_end_date(
                    project.work_end_date.year,
                    project.work_end_date.month
                )

            project.payment_due_date = new_payment_due_date

        # 入金ステータスを設定
        status_choice = random.choices(
            payment_status_distribution,
            weights=[dist[2] for dist in payment_status_distribution]
        )[0]

        project.payment_status = status_choice[0]

        # 入金済みの場合は実行日を設定
        if status_choice[0] == 'executed':
            if project.payment_due_date:
                # 予定日の前後数日で実際の入金日を設定
                variance_days = random.randint(-3, 7)  # 3日早い〜7日遅い
                project.payment_executed_date = project.payment_due_date + timedelta(days=variance_days)
            else:
                project.payment_executed_date = timezone.now().date() - timedelta(days=random.randint(1, 30))

            paid_projects.append(project)

        # 遅延の場合
        elif status_choice[0] == 'overdue':
            if project.payment_due_date and project.payment_due_date < timezone.now().date():
                overdue_projects.append(project)

        # billing_amountが設定されていない場合は estimate_amount の 95% に設定
        if not project.billing_amount and project.estimate_amount:
            variance = Decimal(str(random.uniform(0.90, 1.00)))  # 90-100%
            project.billing_amount = (project.estimate_amount * variance).quantize(Decimal('1'))

        project.save()
        updated_count += 1

        if updated_count % 10 == 0:
            print(f"進捗: {updated_count}/{total_projects}")

    return paid_projects, overdue_projects, updated_count

def show_payment_summary():
    """入金状況のサマリーを表示"""
    print("\n" + "=" * 60)
    print("PAYMENT SUMMARY")
    print("=" * 60)

    # ステータス別集計
    status_summary = {}
    total_revenue = Decimal('0')

    for status_code, status_name, _ in [
        ('scheduled', '入金予定', 0),
        ('executed', '入金済み', 0),
        ('overdue', '遅延', 0)
    ]:
        projects = Project.objects.filter(payment_status=status_code, estimate_amount__gt=0)
        count = projects.count()
        revenue = sum(p.billing_amount or p.estimate_amount or 0 for p in projects)

        status_summary[status_code] = {
            'name': status_name,
            'count': count,
            'revenue': revenue
        }
        total_revenue += revenue

    # 表示
    for status_code, data in status_summary.items():
        percentage = (data['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
        print(f"{data['name']:>8s}: {data['count']:>3d}件 | ¥{data['revenue']:>12,.0f} ({percentage:>5.1f}%)")

    print(f"{'総計':>8s}: {sum(d['count'] for d in status_summary.values()):>3d}件 | ¥{total_revenue:>12,.0f}")

    # 月別入金予定
    print("\n月別入金予定:")
    for month in range(8, 13):  # 8月-12月
        projects = Project.objects.filter(
            payment_due_date__year=2025,
            payment_due_date__month=month,
            estimate_amount__gt=0
        )
        revenue = sum(p.billing_amount or p.estimate_amount or 0 for p in projects)
        paid_revenue = sum(
            p.billing_amount or p.estimate_amount or 0
            for p in projects if p.payment_status == 'executed'
        )

        print(f"  {month:>2d}月: ¥{revenue:>10,.0f} (入金済み: ¥{paid_revenue:>10,.0f})")

def create_additional_completed_projects():
    """追加で完了済みプロジェクトを作成"""
    print("\n" + "=" * 60)
    print("ENSURING SUFFICIENT COMPLETED PROJECTS")
    print("=" * 60)

    # 現在の完了済みプロジェクト数
    completed_projects = Project.objects.filter(work_end_completed=True)
    current_completed = completed_projects.count()

    print(f"現在の完了済みプロジェクト: {current_completed}件")

    # 50件以上の完了済みプロジェクトを確保
    target_completed = 50
    if current_completed < target_completed:
        projects_to_complete = Project.objects.filter(
            work_end_completed=False
        )[:target_completed - current_completed]

        for project in projects_to_complete:
            # 過去の日付で完了させる
            days_ago = random.randint(5, 60)
            project.work_end_date = timezone.now().date() - timedelta(days=days_ago)
            project.work_end_completed = True
            project.save()

        print(f"追加で{len(projects_to_complete)}件のプロジェクトを完了に設定")

def main():
    print("🏗️  Creating Realistic Payment Variations")

    # 完了済みプロジェクトを確保
    create_additional_completed_projects()

    # 現実的な入金スケジュールを作成
    paid_projects, overdue_projects, updated_count = create_realistic_payment_schedule()

    print(f"\n✅ 処理完了: {updated_count}件のプロジェクトを更新")
    print(f"💰 入金済みプロジェクト: {len(paid_projects)}件")
    print(f"⚠️  遅延プロジェクト: {len(overdue_projects)}件")

    # サマリー表示
    show_payment_summary()

    print(f"\n🎯 主な改善点:")
    print(f"  ✓ 入金タイミングを工事完了後に設定")
    print(f"  ✓ 翌月末払いパターンを追加")
    print(f"  ✓ 入金済み・遅延・予定のバリエーション作成")
    print(f"  ✓ billing_amountの自動設定")

if __name__ == "__main__":
    main()