"""
本物さながらのテストデータ生成スクリプト

建設業の現実的なデータを生成します：
- 過去6ヶ月分の完工プロジェクト（季節性を反映）
- 現在進行中のプロジェクト
- パイプライン案件（ネタ、施工日待ち）
- キャッシュフロー取引
- プロジェクト進捗記録
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Djangoセットアップ
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth.models import User
from order_management.models import Project, CashFlowTransaction, ProjectProgress, ForecastScenario, SeasonalityIndex
from django.utils import timezone


def get_or_create_user():
    """テストユーザーを取得または作成"""
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'is_staff': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ テストユーザー作成: {user.username}")
    return user


def clear_existing_data():
    """既存のテストデータをクリア"""
    print("\n🗑️  既存データをクリア中...")
    ProjectProgress.objects.all().delete()
    CashFlowTransaction.objects.all().delete()
    Project.objects.all().delete()
    print("✅ クリア完了")


def generate_realistic_projects(user):
    """リアルなプロジェクトデータを生成"""
    print("\n🏗️  プロジェクトデータ生成中...")

    # 建設業の現実的な施工種別
    work_types = [
        '外壁塗装', '屋根工事', '防水工事', 'タイル工事',
        '足場工事', '解体工事', '内装工事', '左官工事'
    ]

    # エリア
    areas = [
        '東京都渋谷区', '東京都新宿区', '東京都港区', '横浜市中区',
        '川崎市幸区', 'さいたま市大宮区', '千葉市中央区'
    ]

    # 季節性指数（月別の売上傾向）
    seasonal_factors = {
        1: 0.75,   # 1月: 冬季、少ない
        2: 0.85,   # 2月: 少ない
        3: 1.40,   # 3月: 年度末、多い！
        4: 1.10,   # 4月: 新年度
        5: 1.05,   # 5月
        6: 0.95,   # 6月: 梅雨
        7: 0.90,   # 7月: 梅雨
        8: 0.80,   # 8月: 夏季休暇
        9: 1.15,   # 9月: 下半期
        10: 1.10,  # 10月
        11: 1.05,  # 11月
        12: 0.95,  # 12月: 年末
    }

    projects = []
    today = datetime.now().date()

    # ========================================
    # 1. 過去6ヶ月の完工プロジェクト（30件）
    # ========================================
    print("  📦 完工プロジェクト生成中...")
    completed_count = 0
    for i in range(30):
        # ランダムな完工日（過去6ヶ月以内）
        days_ago = random.randint(1, 180)
        completion_date = today - timedelta(days=days_ago)
        month = completion_date.month

        # 基本売上（500万～2000万）
        base_value = Decimal(str(random.randint(5000000, 20000000)))

        # 季節性を反映
        seasonal_multiplier = Decimal(str(seasonal_factors.get(month, 1.0)))
        order_value = int(base_value * seasonal_multiplier)

        # プロジェクト作成
        management_no = f"C{completion_date.strftime('%Y%m')}{i+1:03d}"
        work_type = random.choice(work_types)
        area = random.choice(areas)

        # 着工日（完工の1-3ヶ月前）
        construction_days = random.randint(30, 90)
        start_date = completion_date - timedelta(days=construction_days)

        project = Project.objects.create(
            management_no=management_no,
            site_name=f"{area} {work_type}工事",
            site_address=f"{area}〇〇ビル",
            work_type=work_type,
            project_status='完工',
            order_amount=order_value,
            estimate_issued_date=start_date - timedelta(days=random.randint(7, 30)),
            contract_date=start_date - timedelta(days=random.randint(1, 10)),
            work_start_date=start_date,
            work_end_date=completion_date - timedelta(days=random.randint(0, 5)),
            completion_date=completion_date,
            client_name='中村建設',
            project_manager=random.choice(['田中', '佐藤', '鈴木', '高橋']),
            notes=f"{month}月完工案件（季節性指数: {seasonal_multiplier}）"
        )
        projects.append(project)
        completed_count += 1

        # キャッシュフロー生成（入金）
        CashFlowTransaction.objects.create(
            project=project,
            transaction_type='revenue_cash',
            amount=order_value,
            transaction_date=completion_date + timedelta(days=random.randint(30, 60)),
            description='工事代金入金',
            is_planned=True
        )

        # 出金（原価75%）
        cost = int(order_value * Decimal('0.75'))
        CashFlowTransaction.objects.create(
            project=project,
            transaction_type='expense_cash',
            amount=cost,
            transaction_date=completion_date + timedelta(days=random.randint(10, 40)),
            description='下請・材料費支払',
            is_planned=random.random() < 0.3  # 30%は予定、70%は実績
        )

    print(f"  ✅ 完工プロジェクト {completed_count}件生成")

    # ========================================
    # 2. 進行中プロジェクト（10件）
    # ========================================
    print("  🚧 進行中プロジェクト生成中...")
    in_progress_count = 0
    for i in range(10):
        # 着工済み、完工予定は1-2ヶ月後
        days_started = random.randint(10, 60)
        start_date = today - timedelta(days=days_started)
        completion_date = today + timedelta(days=random.randint(10, 60))

        order_value = random.randint(8000000, 25000000)
        management_no = f"P{today.strftime('%Y%m')}{i+1:03d}"
        work_type = random.choice(work_types)
        area = random.choice(areas)

        project = Project.objects.create(
            management_no=management_no,
            site_name=f"{area} {work_type}工事",
            site_address=f"{area}〇〇マンション",
            work_type=work_type,
            project_status='進行中',
            order_amount=order_value,
            estimate_issued_date=start_date - timedelta(days=20),
            contract_date=start_date - timedelta(days=7),
            work_start_date=start_date,
            work_end_date=completion_date,
            client_name='山田工務店',
            project_manager=random.choice(['伊藤', '渡辺', '山本', '中村']),
            notes='進行中案件'
        )
        projects.append(project)
        in_progress_count += 1

        # 進捗記録を追加
        total_days = (completion_date - start_date).days
        elapsed_days = (today - start_date).days
        progress_rate = min(Decimal('90.00'), (Decimal(str(elapsed_days)) / Decimal(str(total_days))) * Decimal('100.00'))

        # ランダムでリスクを設定
        has_risk = random.random() < 0.3

        ProjectProgress.objects.create(
            project=project,
            recorded_date=today,
            recorded_by=user,
            progress_rate=progress_rate,
            status='on_track' if not has_risk else 'at_risk',
            notes=f'順調に進行中（{int(progress_rate)}%完了）' if not has_risk else '天候不良により若干遅延の可能性',
            milestone_name=f'{work_type}完了' if progress_rate > 50 else f'{work_type}開始',
            milestone_date=completion_date if progress_rate > 50 else start_date + timedelta(days=10),
            milestone_completed=progress_rate > 50,
            has_risk=has_risk,
            risk_level='medium' if has_risk else 'low',
            risk_description='天候不良リスク' if has_risk else ''
        )

        # キャッシュフロー（着手金）
        deposit = int(order_value * Decimal('0.3'))
        CashFlowTransaction.objects.create(
            project=project,
            transaction_type='revenue_cash',
            amount=deposit,
            transaction_date=start_date + timedelta(days=3),
            description='着手金',
            is_planned=False  # 実績
        )

    print(f"  ✅ 進行中プロジェクト {in_progress_count}件生成")

    # ========================================
    # 3. 施工日待ちプロジェクト（8件）
    # ========================================
    print("  ⏳ 施工日待ちプロジェクト生成中...")
    waiting_count = 0
    for i in range(8):
        order_value = random.randint(6000000, 18000000)
        management_no = f"W{today.strftime('%Y%m')}{i+1:03d}"
        work_type = random.choice(work_types)
        area = random.choice(areas)

        # 着工予定は1-3週間後
        start_date = today + timedelta(days=random.randint(7, 21))
        completion_date = start_date + timedelta(days=random.randint(30, 60))

        project = Project.objects.create(
            management_no=management_no,
            site_name=f"{area} {work_type}工事",
            site_address=f"{area}〇〇ハイツ",
            work_type=work_type,
            project_status='施工日待ち',
            order_amount=order_value,
            estimate_issued_date=today - timedelta(days=random.randint(10, 30)),
            contract_date=today - timedelta(days=random.randint(1, 10)),
            work_end_date=completion_date,
            client_name='佐藤組',
            project_manager=random.choice(['小林', '加藤', '吉田', '山田']),
            notes='受注済み、施工日調整中'
        )
        projects.append(project)
        waiting_count += 1

    print(f"  ✅ 施工日待ちプロジェクト {waiting_count}件生成")

    # ========================================
    # 4. ネタ（見込み）プロジェクト（12件）
    # ========================================
    print("  💡 ネタプロジェクト生成中...")
    neta_count = 0
    for i in range(12):
        order_value = random.randint(5000000, 20000000)
        management_no = f"N{today.strftime('%Y%m')}{i+1:03d}"
        work_type = random.choice(work_types)
        area = random.choice(areas)

        project = Project.objects.create(
            management_no=management_no,
            site_name=f"{area} {work_type}工事",
            site_address=f"{area}〇〇アパート",
            work_type=work_type,
            project_status='ネタ',
            order_amount=order_value,
            estimate_issued_date=today - timedelta(days=random.randint(1, 14)),
            client_name='鈴木建設',
            project_manager=random.choice(['佐々木', '山口', '松本', '井上']),
            notes='見積提出済み、返答待ち'
        )
        projects.append(project)
        neta_count += 1

    print(f"  ✅ ネタプロジェクト {neta_count}件生成")

    # ========================================
    # 5. NGプロジェクト（5件）
    # ========================================
    print("  ❌ NGプロジェクト生成中...")
    ng_count = 0
    for i in range(5):
        order_value = random.randint(4000000, 15000000)
        management_no = f"NG{today.strftime('%Y%m')}{i+1:03d}"
        work_type = random.choice(work_types)
        area = random.choice(areas)

        project = Project.objects.create(
            management_no=management_no,
            site_name=f"{area} {work_type}工事",
            site_address=f"{area}〇〇ホール",
            work_type=work_type,
            project_status='NG',
            order_amount=order_value,
            estimate_issued_date=today - timedelta(days=random.randint(20, 60)),
            client_name='田中工業',
            project_manager=random.choice(['木村', '林', '斎藤', '清水']),
            notes='価格不一致により失注'
        )
        projects.append(project)
        ng_count += 1

    print(f"  ✅ NGプロジェクト {ng_count}件生成")

    total_projects = completed_count + in_progress_count + waiting_count + neta_count + ng_count
    print(f"\n✅ 合計 {total_projects}件のプロジェクト生成完了")

    return projects


def generate_forecast_scenarios(user):
    """予測シナリオを生成"""
    print("\n📊 予測シナリオ生成中...")

    scenarios = []

    # 通常シナリオ（デフォルト）
    normal_scenario = ForecastScenario.objects.create(
        name='2025年度 標準予測',
        description='過去実績ベースの標準的な予測シナリオ',
        scenario_type='normal',
        conversion_rate_neta=Decimal('30.00'),
        conversion_rate_waiting=Decimal('85.00'),
        cost_rate=Decimal('75.00'),
        forecast_months=12,
        seasonality_enabled=True,
        fixed_cost_multiplier=Decimal('1.00'),
        variable_cost_multiplier=Decimal('1.00'),
        is_default=True,
        is_active=True,
        created_by=user
    )
    scenarios.append(normal_scenario)
    print("  ✅ 通常シナリオ作成")

    # 季節性指数を手動設定
    SeasonalityIndex.objects.create(
        forecast_scenario=normal_scenario,
        january_index=Decimal('0.75'),
        february_index=Decimal('0.85'),
        march_index=Decimal('1.40'),
        april_index=Decimal('1.10'),
        may_index=Decimal('1.05'),
        june_index=Decimal('0.95'),
        july_index=Decimal('0.90'),
        august_index=Decimal('0.80'),
        september_index=Decimal('1.15'),
        october_index=Decimal('1.10'),
        november_index=Decimal('1.05'),
        december_index=Decimal('0.95'),
        use_auto_calculation=False
    )
    print("  ✅ 季節性指数設定")

    # 最悪シナリオ
    worst_scenario = ForecastScenario.objects.create(
        name='2025年度 保守的予測',
        description='景気悪化を想定した保守的シナリオ',
        scenario_type='worst',
        conversion_rate_neta=Decimal('20.00'),
        conversion_rate_waiting=Decimal('70.00'),
        cost_rate=Decimal('80.00'),
        forecast_months=12,
        seasonality_enabled=True,
        fixed_cost_multiplier=Decimal('1.00'),
        variable_cost_multiplier=Decimal('1.00'),
        is_default=False,
        is_active=True,
        created_by=user
    )
    scenarios.append(worst_scenario)
    print("  ✅ 最悪シナリオ作成")

    # 最良シナリオ
    best_scenario = ForecastScenario.objects.create(
        name='2025年度 楽観的予測',
        description='市況好転を想定した楽観的シナリオ',
        scenario_type='best',
        conversion_rate_neta=Decimal('40.00'),
        conversion_rate_waiting=Decimal('95.00'),
        cost_rate=Decimal('70.00'),
        forecast_months=12,
        seasonality_enabled=True,
        fixed_cost_multiplier=Decimal('1.00'),
        variable_cost_multiplier=Decimal('1.00'),
        is_default=False,
        is_active=True,
        created_by=user
    )
    scenarios.append(best_scenario)
    print("  ✅ 最良シナリオ作成")

    # 各シナリオの予測を計算
    print("\n  🔮 予測計算中...")
    for scenario in scenarios:
        scenario.calculate_forecast()
        print(f"    ✅ {scenario.name} 計算完了")

    print(f"\n✅ {len(scenarios)}件の予測シナリオ生成完了")


def main():
    """メイン処理"""
    print("=" * 60)
    print("🏗️  建設業 リアルテストデータ生成ツール")
    print("=" * 60)

    # ユーザー取得
    user = get_or_create_user()

    # データクリア
    response = input("\n⚠️  既存データを削除してよろしいですか？ (yes/no): ")
    if response.lower() == 'yes':
        clear_existing_data()
    else:
        print("⚠️  既存データはそのまま保持されます")

    # プロジェクト生成
    projects = generate_realistic_projects(user)

    # 予測シナリオ生成
    generate_forecast_scenarios(user)

    # サマリー表示
    print("\n" + "=" * 60)
    print("📊 生成データサマリー")
    print("=" * 60)
    print(f"完工:         {Project.objects.filter(project_status='完工').count()}件")
    print(f"進行中:       {Project.objects.filter(project_status='進行中').count()}件")
    print(f"施工日待ち:   {Project.objects.filter(project_status='施工日待ち').count()}件")
    print(f"ネタ:         {Project.objects.filter(project_status='ネタ').count()}件")
    print(f"NG:           {Project.objects.filter(project_status='NG').count()}件")
    print(f"\nキャッシュフロー取引: {CashFlowTransaction.objects.count()}件")
    print(f"進捗記録:     {ProjectProgress.objects.count()}件")
    print(f"予測シナリオ: {ForecastScenario.objects.count()}件")

    # 売上サマリー
    completed = Project.objects.filter(project_status='完工')
    total_revenue = sum(p.order_amount for p in completed if p.order_amount)
    print(f"\n完工案件売上合計: ¥{int(total_revenue):,}")

    print("\n" + "=" * 60)
    print("✅ テストデータ生成完了！")
    print("=" * 60)
    print("\n次のコマンドでサーバーを起動してください：")
    print("  python manage.py runserver")
    print("\nログイン情報：")
    print("  URL: http://localhost:8000/orders/login/")
    print("  Username: testuser")
    print("  Password: testpass123")
    print("\n売上予測ダッシュボード：")
    print("  http://localhost:8000/orders/forecast/")


if __name__ == '__main__':
    main()
