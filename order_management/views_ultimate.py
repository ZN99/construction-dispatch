from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q, Sum, Count, Case, When, DecimalField, F
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from decimal import Decimal

from .models import Project, FixedCost, VariableCost
from subcontract_management.models import Subcontract, Contractor, InternalWorker


class UltimateDashboardView(TemplateView):
    """統合型究極ダッシュボード - プロジェクト管理と会計を統合"""
    template_name = 'order_management/ultimate_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 現在の日時と会計情報
        now = timezone.now()
        today = now.date()
        year = int(self.request.GET.get('year', now.year))
        month = int(self.request.GET.get('month', now.month))
        view_type = self.request.GET.get('view', 'financial')  # financial, operational

        # 月の開始日と終了日
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()

        # ====================
        # プロジェクト管理統計
        # ====================

        # プロジェクト基本統計
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(
            Q(work_start_date__lte=today) & Q(work_end_date__gte=today)
        ).count()

        # 受注ヨミ別統計
        status_stats = Project.objects.values('order_status').annotate(
            count=Count('id'),
            total_amount=Sum('estimate_amount')
        ).order_by('order_status')

        # ステータス別カウント
        status_counts = {
            '受注': Project.objects.filter(order_status='受注').count(),
            'NG': Project.objects.filter(order_status='NG').count(),
            'A': Project.objects.filter(order_status='A').count(),
            '検討中': Project.objects.filter(order_status='検討中').count(),
        }

        # 今月の案件統計
        this_month_projects = Project.objects.filter(
            created_at__year=year,
            created_at__month=month
        )
        new_projects_this_month = this_month_projects.count()
        new_orders_this_month = this_month_projects.filter(order_status='受注').count()

        # 進行中案件（工事中）
        ongoing_projects = Project.objects.filter(
            work_start_date__lte=today,
            work_end_date__gte=today
        ).order_by('work_end_date')[:10]

        # 近日開始予定案件
        upcoming_projects = Project.objects.filter(
            work_start_date__gt=today,
            work_start_date__lte=today + timedelta(days=30)
        ).order_by('work_start_date')[:10]

        # 月別推移データ（過去6ヶ月）
        monthly_trends = []
        for i in range(6):
            target_date = today.replace(day=1) - timedelta(days=i*30)
            month_start = target_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            month_projects = Project.objects.filter(
                created_at__date__range=[month_start, month_end]
            )

            monthly_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': calendar.month_name[month_start.month],
                'total': month_projects.count(),
                'received': month_projects.filter(order_status='受注').count(),
                'amount': month_projects.aggregate(Sum('estimate_amount'))['estimate_amount__sum'] or 0
            })

        monthly_trends.reverse()

        # プロジェクト完了率
        completed_projects = Project.objects.filter(
            work_end_completed=True,
            work_end_date__year=year
        ).count()

        completion_rate = 0
        if total_projects > 0:
            completion_rate = (completed_projects / total_projects) * 100

        # ====================
        # 財務・会計統計（Accounting Dashboard から）
        # ====================

        # 入金データ（入金ベース）
        receipt_projects = Project.objects.filter(
            Q(payment_due_date__range=[start_date, end_date]) |
            Q(order_status='受注', billing_amount__gt=0)
        ).exclude(contractor_name__isnull=True).exclude(contractor_name='')

        receipt_total = 0
        receipt_received = 0
        receipt_pending = 0

        for project in receipt_projects:
            amount = project.billing_amount or project.estimate_amount or 0
            receipt_total += amount
            if project.work_end_completed:
                receipt_received += amount
            else:
                receipt_pending += amount

        # 出金データ（出金ベース）
        payment_subcontracts = Subcontract.objects.filter(
            Q(payment_date__range=[start_date, end_date]) |
            Q(billed_amount__gt=0)
        ).select_related('project', 'contractor', 'internal_worker')

        payment_total = 0
        payment_paid = 0
        payment_pending = 0

        for subcontract in payment_subcontracts:
            amount = subcontract.billed_amount or subcontract.contract_amount or 0
            payment_total += amount
            if subcontract.payment_status == 'paid':
                payment_paid += amount
            else:
                payment_pending += amount

        # キャッシュフロー計算
        net_cashflow = receipt_received - payment_paid
        projected_cashflow = receipt_total - payment_total

        # 通帳スタイルのトランザクション
        transactions = []

        # 入金トランザクション
        for project in receipt_projects:
            amount = project.billing_amount or project.estimate_amount or 0
            if amount > 0:
                transactions.append({
                    'date': project.payment_due_date or project.contract_date or start_date,
                    'description': f'入金: {project.site_name}',
                    'client': project.contractor_name,
                    'type': 'receipt',
                    'amount': amount,
                    'status': 'completed' if project.work_end_completed else 'pending',
                    'project': project
                })

        # 出金トランザクション
        for subcontract in payment_subcontracts:
            amount = subcontract.billed_amount or subcontract.contract_amount or 0
            if amount > 0:
                payee = subcontract.contractor.name if subcontract.contractor else subcontract.internal_worker.name
                transactions.append({
                    'date': subcontract.payment_date or start_date,
                    'description': f'出金: {subcontract.site_name}',
                    'client': payee,
                    'type': 'payment',
                    'amount': amount,
                    'status': subcontract.payment_status,
                    'project': subcontract.project
                })

        # 日付順でソート
        transactions.sort(key=lambda x: x['date'])

        # 残高計算
        balance = 0
        for transaction in transactions:
            if transaction['type'] == 'receipt':
                if transaction['status'] == 'completed':
                    balance += transaction['amount']
            else:
                if transaction['status'] == 'paid':
                    balance -= transaction['amount']
            transaction['balance'] = balance

        # 年間業績データ取得
        annual_performance = self.get_annual_performance(year)

        # ====================
        # 統合分析データ（新規）
        # ====================

        # プロジェクト収益性分析
        profitable_projects = []
        for project in Project.objects.filter(order_status='受注')[:10]:
            revenue = project.billing_amount or project.estimate_amount or 0
            costs = Subcontract.objects.filter(project=project).aggregate(
                total=Sum('billed_amount')
            )['total'] or 0

            if revenue > 0:
                profit_margin = ((revenue - costs) / revenue) * 100
                profitable_projects.append({
                    'project': project,
                    'revenue': revenue,
                    'costs': costs,
                    'profit': revenue - costs,
                    'margin': profit_margin
                })

        # 収益性でソート
        profitable_projects.sort(key=lambda x: x['margin'], reverse=True)

        # パイプライン価値（受注見込み案件の総額）
        pipeline_value = Project.objects.filter(
            order_status__in=['A', '検討中']
        ).aggregate(total=Sum('estimate_amount'))['total'] or 0

        # コスト管理統計
        fixed_costs_monthly = FixedCost.objects.filter(is_active=True).aggregate(
            total=Sum('monthly_amount')
        )['total'] or 0

        variable_costs_monthly = VariableCost.objects.filter(
            incurred_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_monthly_costs = fixed_costs_monthly + variable_costs_monthly

        # ====================
        # コンテキストデータ統合
        # ====================

        context.update({
            # 基本情報
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'today': today,
            'view_type': view_type,
            'start_date': start_date,
            'end_date': end_date,

            # プロジェクト管理データ
            'total_projects': total_projects,
            'active_projects': active_projects,
            'new_projects_this_month': new_projects_this_month,
            'new_orders_this_month': new_orders_this_month,
            'completion_rate': completion_rate,
            'status_stats': status_stats,
            'status_counts': status_counts,
            'ongoing_projects': ongoing_projects,
            'upcoming_projects': upcoming_projects,
            'monthly_trends': monthly_trends,

            # 財務データ
            'receipt_total': receipt_total,
            'receipt_received': receipt_received,
            'receipt_pending': receipt_pending,
            'payment_total': payment_total,
            'payment_paid': payment_paid,
            'payment_pending': payment_pending,
            'net_cashflow': net_cashflow,
            'projected_cashflow': projected_cashflow,
            'transactions': transactions[:20],  # 最新20件
            'annual_performance': annual_performance,

            # 統合分析データ
            'profitable_projects': profitable_projects[:5],  # Top 5
            'pipeline_value': pipeline_value,
            'fixed_costs_monthly': fixed_costs_monthly,
            'variable_costs_monthly': variable_costs_monthly,
            'total_monthly_costs': total_monthly_costs,

            # ビュータイプ選択肢
            'view_type_choices': [
                ('financial', '財務詳細ビュー'),
                ('operational', '運用詳細ビュー'),
            ],
        })

        return context

    def get_annual_performance(self, year):
        """年間業績データを計算（AccountingDashboardViewから移植）"""
        # 会計年度: 4月-3月
        fiscal_year_start = datetime(year, 4, 1).date()
        fiscal_year_end = datetime(year + 1, 3, 31).date()
        current_date = timezone.now().date()
        current_month = current_date.month
        current_year = current_date.year

        # 月次データを初期化
        monthly_data = {}
        for i in range(12):
            month_offset = i + 4
            if month_offset > 12:
                target_year = year + 1
                target_month = month_offset - 12
            else:
                target_year = year
                target_month = month_offset

            monthly_data[i] = {
                'year': target_year,
                'month': target_month,
                'month_name': calendar.month_name[target_month],
                'revenue': Decimal('0'),
                'cost_of_sales': Decimal('0'),
                'cost_labor': Decimal('0'),
                'cost_materials': Decimal('0'),
                'gross_profit': Decimal('0'),
                'sales_expense': Decimal('0'),
                'fixed_costs': Decimal('0'),
                'operating_profit': Decimal('0'),
                'is_actual': False,
                'is_current': False,
                # 新規追加: プロジェクト統計
                'new_projects': 0,
                'completed_projects': 0,
            }

        # 実績データとフラグの設定
        for i, data in monthly_data.items():
            target_date = datetime(data['year'], data['month'], 1).date()
            if target_date <= current_date:
                data['is_actual'] = True
            if data['year'] == current_year and data['month'] == current_month:
                data['is_current'] = True

            # プロジェクト統計追加
            month_projects = Project.objects.filter(
                created_at__year=data['year'],
                created_at__month=data['month']
            )
            data['new_projects'] = month_projects.count()
            data['completed_projects'] = month_projects.filter(work_end_completed=True).count()

        # 売上高・売上原価の計算
        revenue_projects = Project.objects.filter(
            order_status='受注',
            billing_amount__gt=0
        )

        for project in revenue_projects:
            # 売上計上日（入金予定日ベースに変更）
            revenue_date = project.payment_due_date
            if not revenue_date or not (fiscal_year_start <= revenue_date <= fiscal_year_end):
                continue

            month_index = self.get_fiscal_month_index(revenue_date, year)
            if month_index is not None:
                revenue = project.billing_amount or Decimal('0')
                monthly_data[month_index]['revenue'] += revenue

                subcontracts = Subcontract.objects.filter(project=project)
                for subcontract in subcontracts:
                    cost = subcontract.billed_amount or subcontract.contract_amount or Decimal('0')
                    monthly_data[month_index]['cost_of_sales'] += cost

                    if subcontract.worker_type == 'external':
                        monthly_data[month_index]['cost_labor'] += cost

        # 販管費の計算
        variable_costs = VariableCost.objects.filter(
            incurred_date__range=[fiscal_year_start, fiscal_year_end]
        )

        for cost in variable_costs:
            month_index = self.get_fiscal_month_index(cost.incurred_date, year)
            if month_index is not None:
                monthly_data[month_index]['sales_expense'] += cost.amount

        # 固定費の計算
        for i, data in monthly_data.items():
            target_year = data['year']
            target_month = data['month']

            fixed_costs = FixedCost.objects.filter(is_active=True)
            monthly_fixed_total = Decimal('0')

            for fixed_cost in fixed_costs:
                if fixed_cost.is_active_in_month(target_year, target_month):
                    monthly_fixed_total += fixed_cost.monthly_amount

            monthly_data[i]['fixed_costs'] = monthly_fixed_total

        # 損益計算
        for i, data in monthly_data.items():
            data['gross_profit'] = data['revenue'] - data['cost_of_sales']
            data['operating_profit'] = data['gross_profit'] - data['sales_expense'] - data['fixed_costs']

        # 今月度・年度累計の計算
        current_month_data = None
        ytd_data = {
            'revenue': Decimal('0'),
            'cost_of_sales': Decimal('0'),
            'gross_profit': Decimal('0'),
            'sales_expense': Decimal('0'),
            'fixed_costs': Decimal('0'),
            'operating_profit': Decimal('0'),
            'new_projects': 0,
            'completed_projects': 0,
        }

        for i, data in monthly_data.items():
            if data['is_current']:
                current_month_data = data

            if data['is_actual']:
                for key in ['revenue', 'cost_of_sales', 'gross_profit', 'sales_expense', 'fixed_costs', 'operating_profit']:
                    ytd_data[key] += data[key]
                ytd_data['new_projects'] += data['new_projects']
                ytd_data['completed_projects'] += data['completed_projects']

        # 利益率計算
        current_month_margin = Decimal('0')
        ytd_margin = Decimal('0')

        if current_month_data and current_month_data['revenue'] > 0:
            current_month_margin = (current_month_data['operating_profit'] / current_month_data['revenue']) * 100

        if ytd_data['revenue'] > 0:
            ytd_margin = (ytd_data['operating_profit'] / ytd_data['revenue']) * 100

        return {
            'current_date': current_date,
            'fiscal_year': year,
            'current_month_data': current_month_data,
            'current_month_margin': current_month_margin,
            'ytd_data': ytd_data,
            'ytd_margin': ytd_margin,
            'monthly_data': monthly_data,
        }

    def get_fiscal_month_index(self, date, fiscal_year):
        """会計年度内の月インデックスを取得"""
        if date.month >= 4:
            if date.year == fiscal_year:
                return date.month - 4
        else:
            if date.year == fiscal_year + 1:
                return date.month + 8
        return None