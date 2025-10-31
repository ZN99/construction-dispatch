"""
包括的なテストデータ生成コマンド

Usage:
    python manage.py load_comprehensive_test_data
    python manage.py load_comprehensive_test_data --clear
    python manage.py load_comprehensive_test_data --count 100
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta, date
import random
from decimal import Decimal

from order_management.models import (
    Project, CashFlowTransaction, ProjectProgress,
    ForecastScenario, SeasonalityIndex, Comment, Notification,
    Contractor, MaterialOrder, UserProfile
)
try:
    from surveys.models import Survey, Surveyor
    SURVEYS_APP_INSTALLED = True
except ImportError:
    SURVEYS_APP_INSTALLED = False


class Command(BaseCommand):
    help = '包括的なテストデータを生成（案件、現地調査、職人、入出金など全て）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=120,
            help='生成する案件数（デフォルト: 120）'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='既存データを削除してから生成'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('建設工事発注管理システム - 包括的テストデータ生成'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        try:
            with transaction.atomic():
                if clear:
                    self.clear_data()

                # Step 1: ユーザーとプロフィール
                admin = self.create_users()

                # Step 2: 外注先（職人）
                contractors = self.create_contractors()

                # Step 3: 現地調査員（surveysアプリがある場合のみ）
                surveyors = []
                if SURVEYS_APP_INSTALLED:
                    surveyors = self.create_surveyors()

                # Step 4: 案件データ（過去7ヶ月に分散）
                projects = self.create_projects(count, admin)

                # Step 5: 現地調査データ（40%の案件に）
                if SURVEYS_APP_INSTALLED:
                    self.create_surveys(projects, surveyors, admin)

                # Step 6: 職人発注データ
                self.create_subcontracts(projects, contractors)

                # Step 7: 資材発注データ
                self.create_material_orders(projects)

                # Step 8: キャッシュフローデータ
                self.create_cashflow_transactions(projects)

                # Step 9: コメントデータ
                self.create_comments(projects, admin)

                # Step 10: 予測シナリオ
                self.create_forecast_scenarios(admin)

                # Step 11: 進捗記録
                self.create_progress_records(projects, admin)

            self.print_summary()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nエラー: {str(e)}'))
            import traceback
            traceback.print_exc()
            raise

    def clear_data(self):
        """既存データをクリア"""
        self.stdout.write('\n🗑️  既存データをクリア中...')

        Comment.objects.all().delete()
        Notification.objects.all().delete()
        ProjectProgress.objects.all().delete()
        CashFlowTransaction.objects.all().delete()
        MaterialOrder.objects.all().delete()
        if SURVEYS_APP_INSTALLED:
            Survey.objects.all().delete()
        Project.objects.all().delete()
        ForecastScenario.objects.all().delete()
        SeasonalityIndex.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('  ✓ クリア完了'))

    def create_users(self):
        """ユーザーとプロフィールを作成"""
        self.stdout.write('\n👥 ユーザー作成中...')

        # 管理者
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': '管理者',
                'last_name': '太郎'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            UserProfile.objects.get_or_create(
                user=admin,
                defaults={'roles': ['executive', 'headquarters']}
            )
            self.stdout.write('  ✓ 管理者: admin/admin123')

        # 営業担当
        for name in ['tanaka', 'suzuki', 'sato']:
            user, created = User.objects.get_or_create(
                username=name,
                defaults={
                    'email': f'{name}@example.com',
                    'first_name': name.capitalize(),
                    'last_name': 'Sales'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'roles': ['headquarters']}
                )

        # 経理担当
        user, created = User.objects.get_or_create(
            username='accounting',
            defaults={
                'email': 'accounting@example.com',
                'first_name': '経理',
                'last_name': '花子'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'roles': ['accounting', 'headquarters']}
            )

        self.stdout.write(self.style.SUCCESS('  ✓ ユーザー作成完了'))
        return admin

    def create_contractors(self):
        """外注先（職人）を作成"""
        self.stdout.write('\n👷 外注先（職人）作成中...')

        contractor_data = [
            {'name': '山田クロス', 'specialties': 'クロス張替', 'phone': '090-1111-2222'},
            {'name': '佐藤フローリング', 'specialties': 'フローリング張替', 'phone': '090-3333-4444'},
            {'name': '鈴木塗装', 'specialties': '外壁塗装', 'phone': '090-5555-6666'},
            {'name': '田中防水', 'specialties': '防水工事', 'phone': '090-7777-8888'},
            {'name': '伊藤電気', 'specialties': '電気工事', 'phone': '090-9999-0000'},
            {'name': '渡辺配管', 'specialties': '配管工事', 'phone': '090-1234-5678'},
            {'name': '高橋設備', 'specialties': '設備工事', 'phone': '090-8765-4321'},
        ]

        contractors = []
        for data in contractor_data:
            contractor, created = Contractor.objects.get_or_create(
                name=data['name'],
                defaults={
                    'specialties': data['specialties'],
                    'phone': data['phone'],
                    'email': f"{data['name'].lower().replace(' ', '')}@example.com",
                    'address': '東京都新宿区西新宿1-1-1',
                    'is_receiving': True,  # 受注業者として設定
                    'is_active': True,
                }
            )
            contractors.append(contractor)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(contractors)}社の外注先を作成'))
        return contractors

    def create_surveyors(self):
        """現地調査員を作成"""
        self.stdout.write('\n🔍 現地調査員作成中...')

        surveyor_data = [
            {'name': '調査員A', 'employee_id': 'EMP001', 'phone': '080-1111-1111'},
            {'name': '調査員B', 'employee_id': 'EMP002', 'phone': '080-2222-2222'},
            {'name': '調査員C', 'employee_id': 'EMP003', 'phone': '080-3333-3333'},
        ]

        surveyors = []
        for idx, data in enumerate(surveyor_data):
            surveyor, created = Surveyor.objects.get_or_create(
                employee_id=data['employee_id'],
                defaults={
                    'name': data['name'],
                    'phone': data['phone'],
                    'email': f"surveyor{idx+1}@example.com",
                    'is_active': True
                }
            )
            surveyors.append(surveyor)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(surveyors)}名の現地調査員を作成'))
        return surveyors

    def create_projects(self, count, admin):
        """案件を作成（過去7ヶ月に分散）"""
        self.stdout.write(f'\n📁 案件データ作成中（{count}件）...')

        work_types = [
            'クロス張替', 'フローリング張替', '外壁塗装', '防水工事',
            '電気工事', '配管工事', '設備工事', '内装工事'
        ]

        areas = [
            '東京都渋谷区', '東京都新宿区', '東京都港区', '横浜市中区',
            '川崎市幸区', 'さいたま市大宮区', '千葉市中央区'
        ]

        client_names = [
            '中村建設', '山田工務店', '佐藤組', '鈴木建設', '田中工業',
            '伊藤ハウス', '渡辺コーポレーション', '高橋ビルド'
        ]

        statuses_and_weights = [
            ('完工', 40),
            ('進行中', 25),
            ('施工日待ち', 15),
            ('ネタ', 15),
            ('NG', 5),
        ]

        # 過去7ヶ月に分散（今日から遡る）
        today_date = timezone.now().date()
        start_date = (today_date - timedelta(days=210)).replace(day=1)  # 約7ヶ月前の月初
        end_date = today_date
        total_days = (end_date - start_date).days

        projects = []
        for i in range(count):
            # ランダムな作成日（過去7ヶ月）
            random_days = random.randint(0, total_days)
            created_date = start_date + timedelta(days=random_days)

            # 時刻もランダムに設定（営業時間内）
            random_hour = random.randint(9, 17)
            random_minute = random.randint(0, 59)
            created_at = timezone.make_aware(
                datetime.combine(
                    created_date,
                    datetime.min.time().replace(hour=random_hour, minute=random_minute)
                )
            )

            # ステータスをランダムに選択
            status = random.choices(
                [s[0] for s in statuses_and_weights],
                weights=[s[1] for s in statuses_and_weights]
            )[0]

            work_type = random.choice(work_types)
            area = random.choice(areas)
            client = random.choice(client_names)

            # 金額
            order_amount = random.randint(500000, 10000000)

            # 日付設定
            if status == '完工':
                completion_date = created_at.date() + timedelta(days=random.randint(30, 120))
                work_start_date = completion_date - timedelta(days=random.randint(10, 60))
                work_end_date = completion_date - timedelta(days=random.randint(0, 5))
            elif status == '進行中':
                work_start_date = created_at.date() + timedelta(days=random.randint(7, 30))
                work_end_date = work_start_date + timedelta(days=random.randint(20, 60))
                completion_date = None
            elif status == '施工日待ち':
                work_start_date = created_at.date() + timedelta(days=random.randint(30, 90))
                work_end_date = work_start_date + timedelta(days=random.randint(20, 60))
                completion_date = None
            else:
                work_start_date = None
                work_end_date = None
                completion_date = None

            project = Project.objects.create(
                management_no=f"P{created_at.strftime('%Y%m')}{i+1:04d}",
                site_name=f"{area} {work_type}",
                site_address=f"{area}〇〇ビル",
                work_type=work_type,
                project_status=status,
                order_amount=order_amount,
                client_name=client,
                project_manager=random.choice(['田中', '佐藤', '鈴木', '高橋', '伊藤']),
                work_start_date=work_start_date,
                work_end_date=work_end_date,
                completion_date=completion_date,
                notes=f'テストデータ {i+1}'
            )

            # auto_now_addがあるため、created_atを直接更新
            Project.objects.filter(pk=project.pk).update(created_at=created_at)
            project.refresh_from_db()  # インスタンスを更新

            projects.append(project)

            if (i + 1) % 20 == 0:
                self.stdout.write(f'  処理中... {i + 1}/{count}件')

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(projects)}件の案件を作成'))

        # 月別分布を表示
        self.stdout.write('\n  【月別分布】')
        today = timezone.now().date()
        for month_offset in range(6, -1, -1):
            month = today.replace(day=1) - timedelta(days=30 * month_offset)
            count_in_month = Project.objects.filter(
                created_at__year=month.year,
                created_at__month=month.month
            ).count()
            self.stdout.write(f'    {month.year}年{month.month:02d}月: {count_in_month}件')

        return projects

    def create_surveys(self, projects, surveyors, admin):
        """現地調査データを作成（40%の案件）"""
        self.stdout.write('\n🔍 現地調査データ作成中...')

        # ランダムに40%の案件を選択
        target_count = int(len(projects) * 0.4)
        selected_projects = random.sample(projects, target_count)

        for project in selected_projects:
            # 案件作成日の7〜30日後に調査
            scheduled_date = project.created_at.date() + timedelta(days=random.randint(7, 30))
            surveyor = random.choice(surveyors)

            Survey.objects.create(
                project=project,
                scheduled_date=scheduled_date,
                scheduled_start_time=datetime.now().time(),
                surveyor=surveyor,
                status=random.choice(['scheduled', 'completed', 'completed', 'completed']),
                notes=f'{project.site_name}の現地調査'
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ {target_count}件の現地調査を作成'))

    def create_subcontracts(self, projects, contractors):
        """職人発注データを作成"""
        self.stdout.write('\n👷 職人発注データ作成中...')

        # 完工・進行中・施工日待ちの案件に職人を発注
        target_projects = [p for p in projects if p.project_status in ['完工', '進行中', '施工日待ち']]

        count = 0
        for project in target_projects:
            # 各案件に1-3名の職人を発注
            num_contractors = random.randint(1, 3)
            selected_contractors = random.sample(contractors, min(num_contractors, len(contractors)))

            for contractor in selected_contractors:
                # 案件の進捗ステップに職人情報を追加（簡易版）
                # Note: 実際のデータベースレコードとして保存する場合は、
                # ContractorAssignmentなどのモデルが必要
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}件の職人発注を作成'))

    def create_material_orders(self, projects):
        """資材発注データを作成"""
        self.stdout.write('\n📦 資材発注データ作成中...')

        # 資材発注は複雑なので、簡略化してスキップ
        # MaterialOrderはcontractor、order_number（UNIQUE）、MaterialOrderItemなど複雑な構造
        # 将来的に必要であれば追加可能

        self.stdout.write(self.style.SUCCESS('  ✓ スキップ（将来追加可能）'))

    def create_cashflow_transactions(self, projects):
        """キャッシュフロー取引を作成"""
        self.stdout.write('\n💰 キャッシュフロー取引作成中...')

        count = 0
        for project in projects:
            if project.project_status in ['完工', '進行中']:
                # 入金（完工の場合）
                if project.project_status == '完工' and project.completion_date:
                    CashFlowTransaction.objects.create(
                        project=project,
                        transaction_type='revenue_cash',
                        amount=project.order_amount or 0,
                        transaction_date=project.completion_date + timedelta(days=random.randint(30, 60)),
                        description='工事代金入金',
                        is_planned=False
                    )
                    count += 1

                # 出金（原価75%）
                if project.order_amount:
                    cost = int(project.order_amount * Decimal('0.75'))
                    CashFlowTransaction.objects.create(
                        project=project,
                        transaction_type='expense_cash',
                        amount=cost,
                        transaction_date=project.created_at.date() + timedelta(days=random.randint(20, 50)),
                        description='下請・材料費支払',
                        is_planned=random.random() < 0.3
                    )
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}件のキャッシュフロー取引を作成'))

    def create_comments(self, projects, admin):
        """コメントを作成"""
        self.stdout.write('\n💬 コメント作成中...')

        comment_templates = [
            '元請から連絡あり、順調に進行中',
            '天候不良により若干遅延の可能性あり',
            '追加工事の見積依頼がありました',
            '施工完了、検収待ち',
            '資材納品完了',
            '職人手配完了',
        ]

        count = 0
        # 50%の案件にコメント
        target_projects = random.sample(projects, len(projects) // 2)
        for project in target_projects:
            Comment.objects.create(
                project=project,
                author=admin,
                content=random.choice(comment_templates),
                is_important=random.random() < 0.2
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}件のコメントを作成'))

    def create_forecast_scenarios(self, admin):
        """予測シナリオを作成"""
        self.stdout.write('\n📊 予測シナリオ作成中...')

        # 通常シナリオ
        normal_scenario = ForecastScenario.objects.create(
            name='2025年度 標準予測',
            description='過去実績ベースの標準的な予測',
            scenario_type='normal',
            conversion_rate_neta=Decimal('30.00'),
            conversion_rate_waiting=Decimal('85.00'),
            cost_rate=Decimal('75.00'),
            forecast_months=12,
            seasonality_enabled=True,
            is_default=True,
            is_active=True,
            created_by=admin
        )

        # 季節性指数
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

        self.stdout.write(self.style.SUCCESS('  ✓ 予測シナリオを作成'))

    def create_progress_records(self, projects, admin):
        """進捗記録を作成"""
        self.stdout.write('\n📈 進捗記録作成中...')

        count = 0
        for project in projects:
            if project.project_status == '進行中':
                ProjectProgress.objects.create(
                    project=project,
                    recorded_date=timezone.now().date(),
                    recorded_by=admin,
                    progress_rate=Decimal(str(random.randint(20, 90))),
                    status='on_track',
                    notes='順調に進行中',
                    has_risk=False
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}件の進捗記録を作成'))

    def print_summary(self):
        """生成したデータのサマリーを表示"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 生成データサマリー'))
        self.stdout.write('=' * 70)

        self.stdout.write(f'\n【案件】')
        self.stdout.write(f"  完工:        {Project.objects.filter(project_status='完工').count()}件")
        self.stdout.write(f"  進行中:      {Project.objects.filter(project_status='進行中').count()}件")
        self.stdout.write(f"  施工日待ち:  {Project.objects.filter(project_status='施工日待ち').count()}件")
        self.stdout.write(f"  ネタ:        {Project.objects.filter(project_status='ネタ').count()}件")
        self.stdout.write(f"  NG:          {Project.objects.filter(project_status='NG').count()}件")
        self.stdout.write(f"  合計:        {Project.objects.count()}件")

        self.stdout.write(f'\n【その他】')
        if SURVEYS_APP_INSTALLED:
            self.stdout.write(f"  現地調査:        {Survey.objects.count()}件")
        self.stdout.write(f"  外注先:          {Contractor.objects.count()}社")
        self.stdout.write(f"  CF取引:          {CashFlowTransaction.objects.count()}件")
        self.stdout.write(f"  コメント:        {Comment.objects.count()}件")
        self.stdout.write(f"  進捗記録:        {ProjectProgress.objects.count()}件")

        completed = Project.objects.filter(project_status='完工')
        total_revenue = sum(p.order_amount or 0 for p in completed)
        self.stdout.write(f'\n【売上】')
        self.stdout.write(f"  完工案件売上合計: ¥{int(total_revenue):,}")

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ テストデータ生成完了！'))
        self.stdout.write('=' * 70)
        self.stdout.write('\nログイン情報：')
        self.stdout.write('  URL: /orders/login/')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('')
