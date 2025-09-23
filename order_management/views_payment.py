from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q, Sum, Count, Case, When, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import Project
from subcontract_management.models import Subcontract, Contractor, InternalWorker
import calendar


def calculate_next_payment_date(contractor, base_date=None):
    """
    業者の支払いサイクルと支払日に基づいて次回支払日を計算

    Args:
        contractor: Contractor instance
        base_date: 基準日（デフォルトは今日）

    Returns:
        datetime.date: 次回支払日
    """
    if base_date is None:
        base_date = timezone.now().date()

    if not contractor.payment_day:
        return base_date  # 支払日が設定されていない場合は基準日を返す

    payment_day = contractor.payment_day
    payment_cycle = contractor.payment_cycle or 'monthly'

    # 今月の支払日を計算
    try:
        this_month_payment = base_date.replace(day=payment_day)
    except ValueError:
        # 31日設定で30日しかない月など
        import calendar
        last_day = calendar.monthrange(base_date.year, base_date.month)[1]
        this_month_payment = base_date.replace(day=min(payment_day, last_day))

    # 支払いサイクルに応じて次回支払日を計算
    if payment_cycle == 'monthly':
        if this_month_payment > base_date:
            return this_month_payment
        else:
            # 来月の支払日
            next_month = base_date + relativedelta(months=1)
            try:
                return next_month.replace(day=payment_day)
            except ValueError:
                last_day = calendar.monthrange(next_month.year, next_month.month)[1]
                return next_month.replace(day=min(payment_day, last_day))

    elif payment_cycle == 'bimonthly':
        if this_month_payment > base_date:
            return this_month_payment
        else:
            # 2ヶ月後の支払日
            next_payment = base_date + relativedelta(months=2)
            try:
                return next_payment.replace(day=payment_day)
            except ValueError:
                last_day = calendar.monthrange(next_payment.year, next_payment.month)[1]
                return next_payment.replace(day=min(payment_day, last_day))

    elif payment_cycle == 'quarterly':
        if this_month_payment > base_date:
            return this_month_payment
        else:
            # 3ヶ月後の支払日
            next_payment = base_date + relativedelta(months=3)
            try:
                return next_payment.replace(day=payment_day)
            except ValueError:
                last_day = calendar.monthrange(next_payment.year, next_payment.month)[1]
                return next_payment.replace(day=min(payment_day, last_day))

    else:  # custom or other
        return base_date


class PaymentDashboardView(TemplateView):
    template_name = 'order_management/payment_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 現在の月を取得（デフォルト）
        now = timezone.now()
        year = int(self.request.GET.get('year', now.year))
        month = int(self.request.GET.get('month', now.month))
        status_filter = self.request.GET.get('status', 'all')

        # 追加フィルター
        contractor_filter = self.request.GET.get('contractor', 'all')
        amount_min = self.request.GET.get('amount_min', '')
        amount_max = self.request.GET.get('amount_max', '')
        payment_cycle_filter = self.request.GET.get('payment_cycle', 'all')
        worker_type_filter = self.request.GET.get('worker_type', 'all')
        has_bank_info = self.request.GET.get('has_bank_info', 'all')

        # 日付範囲フィルター
        date_filter_type = self.request.GET.get('date_filter_type', 'month')  # month, range, next_payment
        date_start = self.request.GET.get('date_start', '')
        date_end = self.request.GET.get('date_end', '')

        # 日付範囲の決定
        if date_filter_type == 'range' and date_start and date_end:
            start_date = datetime.strptime(date_start, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_end, '%Y-%m-%d').date()
        elif date_filter_type == 'next_payment':
            # 次回支払い予定日でフィルター（今日から30日以内）
            start_date = now.date()
            end_date = now.date() + timedelta(days=30)
        else:  # month (デフォルト)
            start_date = datetime(year, month, 1).date()
            end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()

        # 出金ベース：Subcontractから支払い対象を取得
        base_query = Subcontract.objects.filter(
            Q(payment_date__range=[start_date, end_date]) |
            Q(billed_amount__gt=0)  # テスト用：請求額があるものを表示
        ).select_related('project', 'contractor', 'internal_worker')

        # 支払い状況による絞り込み
        if status_filter != 'all':
            status_mapping = {
                'scheduled': 'pending',
                'executed': 'paid',
                'overdue': 'pending',
                'cancelled': 'pending'
            }
            mapped_status = status_mapping.get(status_filter, status_filter)
            base_query = base_query.filter(payment_status=mapped_status)

        # 業者フィルター
        if contractor_filter != 'all':
            base_query = base_query.filter(contractor_id=contractor_filter)

        # 金額フィルター
        if amount_min:
            try:
                min_amount = float(amount_min)
                base_query = base_query.filter(
                    Q(billed_amount__gte=min_amount) | Q(contract_amount__gte=min_amount)
                )
            except ValueError:
                pass

        if amount_max:
            try:
                max_amount = float(amount_max)
                base_query = base_query.filter(
                    Q(billed_amount__lte=max_amount) | Q(contract_amount__lte=max_amount)
                )
            except ValueError:
                pass

        # 支払いサイクルフィルター
        if payment_cycle_filter != 'all':
            base_query = base_query.filter(contractor__payment_cycle=payment_cycle_filter)

        # 作業者タイプフィルター
        if worker_type_filter != 'all':
            base_query = base_query.filter(worker_type=worker_type_filter)

        # 銀行情報有無フィルター
        if has_bank_info == 'yes':
            base_query = base_query.filter(
                contractor__bank_name__isnull=False,
                contractor__account_number__isnull=False
            ).exclude(
                Q(contractor__bank_name='') | Q(contractor__account_number='')
            )
        elif has_bank_info == 'no':
            base_query = base_query.filter(
                Q(contractor__bank_name__isnull=True) |
                Q(contractor__account_number__isnull=True) |
                Q(contractor__bank_name='') |
                Q(contractor__account_number='')
            )

        payment_subcontracts = base_query.order_by('contractor__name', 'internal_worker__name', 'payment_date')

        # 出金先別の集計データ
        payee_summary = {}

        # 今月の出金統計（出金ベース）
        monthly_outflow_stats = {
            'scheduled_amount': 0,  # 支払予定
            'executed_amount': 0,   # 支払済み
            'overdue_amount': 0,    # 遅延
            'total_outflow': 0      # 今月の総出金額
        }

        # 詳細リスト用のデータ
        paid_sites = []          # 今月振り込み済み現場リスト
        paid_contractors = {}    # 業者別今月振り込み済み金額リスト
        pending_sites = []       # 今月振り込み予定現場（未支払）リスト
        pending_contractors = {} # 業者別今月振り込み予定金額リスト

        for subcontract in payment_subcontracts:
            # 出金先の決定（外注業者 or 社内リソース）
            if subcontract.worker_type == 'external' and subcontract.contractor:
                payee_name = subcontract.contractor.name
                payee_type = '外注業者'
            elif subcontract.worker_type == 'internal' and subcontract.internal_worker:
                payee_name = subcontract.internal_worker.name
                payee_type = '社内リソース'
            else:
                continue  # スキップ

            payee_key = f"{payee_type}:{payee_name}"

            if payee_key not in payee_summary:
                payee_summary[payee_key] = {
                    'payee_name': payee_name,
                    'payee_type': payee_type,
                    'subcontracts': [],
                    'total_amount': 0,
                    'paid_amount': 0,
                    'pending_amount': 0,
                    'overdue_amount': 0,
                    'project_count': 0
                }

            # 支払い金額の決定
            amount = subcontract.billed_amount or subcontract.contract_amount or 0

            payee_summary[payee_key]['subcontracts'].append(subcontract)
            payee_summary[payee_key]['total_amount'] += amount
            payee_summary[payee_key]['project_count'] += 1

            # 支払い状況別の集計
            if subcontract.payment_status == 'paid':
                payee_summary[payee_key]['paid_amount'] += amount
                monthly_outflow_stats['executed_amount'] += amount

                # 今月振り込み済み現場リスト
                paid_sites.append({
                    'site_name': subcontract.site_name,
                    'payee_name': payee_name,
                    'payee_type': payee_type,
                    'amount': amount,
                    'payment_date': subcontract.payment_date,
                    'project': subcontract.project
                })

                # 業者別今月振り込み済み金額リスト
                if payee_name not in paid_contractors:
                    bank_info = None
                    if subcontract.contractor and hasattr(subcontract.contractor, 'bank_name'):
                        bank_info = {
                            'bank_name': getattr(subcontract.contractor, 'bank_name', ''),
                            'account_number': getattr(subcontract.contractor, 'account_number', ''),
                            'account_holder': getattr(subcontract.contractor, 'account_holder', '')
                        }

                    paid_contractors[payee_name] = {
                        'payee_type': payee_type,
                        'total_amount': 0,
                        'sites_count': 0,
                        'bank_info': bank_info,
                        'payment_date': subcontract.payment_date
                    }
                paid_contractors[payee_name]['total_amount'] += amount
                paid_contractors[payee_name]['sites_count'] += 1
            else:
                payee_summary[payee_key]['pending_amount'] += amount
                monthly_outflow_stats['scheduled_amount'] += amount

                # 今月振り込み予定現場（未支払）リスト
                pending_sites.append({
                    'site_name': subcontract.site_name,
                    'payee_name': payee_name,
                    'payee_type': payee_type,
                    'amount': amount,
                    'payment_date': subcontract.payment_date,
                    'project': subcontract.project
                })

                # 業者別今月振り込み予定金額リスト
                if payee_name not in pending_contractors:
                    bank_info = None
                    auto_payment_date = None

                    if subcontract.contractor and hasattr(subcontract.contractor, 'bank_name'):
                        bank_info = {
                            'bank_name': getattr(subcontract.contractor, 'bank_name', ''),
                            'account_number': getattr(subcontract.contractor, 'account_number', ''),
                            'account_holder': getattr(subcontract.contractor, 'account_holder', ''),
                            'payment_cycle': getattr(subcontract.contractor, 'payment_cycle', ''),
                            'payment_day': getattr(subcontract.contractor, 'payment_day', None)
                        }
                        # 自動支払日計算
                        auto_payment_date = calculate_next_payment_date(subcontract.contractor)

                    pending_contractors[payee_name] = {
                        'payee_type': payee_type,
                        'total_amount': 0,
                        'sites_count': 0,
                        'bank_info': bank_info,
                        'payment_date': subcontract.payment_date,
                        'auto_payment_date': auto_payment_date,
                        'contractor': subcontract.contractor  # 業者オブジェクトも含める
                    }
                pending_contractors[payee_name]['total_amount'] += amount
                pending_contractors[payee_name]['sites_count'] += 1

            monthly_outflow_stats['total_outflow'] += amount

        # リストをソート
        paid_sites.sort(key=lambda x: x['payment_date'] or timezone.now().date(), reverse=True)
        pending_sites.sort(key=lambda x: x['payment_date'] or timezone.now().date())

        # 業者別リストをソート（金額順）
        paid_contractors_list = [
            {'name': name, **data} for name, data in
            sorted(paid_contractors.items(), key=lambda x: x[1]['total_amount'], reverse=True)
        ]
        pending_contractors_list = [
            {'name': name, **data} for name, data in
            sorted(pending_contractors.items(), key=lambda x: x[1]['total_amount'], reverse=True)
        ]

        # 統計情報（出金ベース）
        stats = {
            'total_payees': len(payee_summary),
            'total_subcontracts': payment_subcontracts.count(),
            'total_outflow': monthly_outflow_stats['total_outflow'],
            'scheduled_amount': monthly_outflow_stats['scheduled_amount'],
            'executed_amount': monthly_outflow_stats['executed_amount'],
            'overdue_amount': monthly_outflow_stats['overdue_amount'],
            'paid_sites_count': len(paid_sites),
            'pending_sites_count': len(pending_sites),
        }

        # 選択肢の準備
        payment_status_choices = [
            ('all', 'すべて'),
            ('scheduled', '支払予定'),
            ('executed', '支払済み'),
            ('overdue', '遅延'),
            ('cancelled', 'キャンセル'),
        ]

        # 業者選択肢
        contractor_choices = [('all', 'すべての業者')]
        contractor_choices.extend([
            (str(c.id), c.name) for c in Contractor.objects.filter(is_active=True).order_by('name')
        ])

        # 支払いサイクル選択肢
        payment_cycle_choices = [
            ('all', 'すべて'),
            ('monthly', '月払い'),
            ('bimonthly', '隔月払い'),
            ('quarterly', '四半期払い'),
            ('custom', 'その他'),
        ]

        # 作業者タイプ選択肢
        worker_type_choices = [
            ('all', 'すべて'),
            ('external', '外注業者'),
            ('internal', '社内リソース'),
        ]

        # 銀行情報有無選択肢
        bank_info_choices = [
            ('all', 'すべて'),
            ('yes', '銀行情報あり'),
            ('no', '銀行情報なし'),
        ]

        # 日付フィルタータイプ選択肢
        date_filter_type_choices = [
            ('month', '月別'),
            ('range', '期間指定'),
            ('next_payment', '次回支払い予定'),
        ]

        context.update({
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'status_filter': status_filter,
            'payment_status_choices': payment_status_choices,
            'payee_summary': payee_summary,
            'payment_subcontracts': payment_subcontracts,
            'stats': stats,
            'start_date': start_date,
            'end_date': end_date,
            # 詳細リスト
            'paid_sites': paid_sites,
            'paid_contractors': paid_contractors_list,
            'pending_sites': pending_sites,
            'pending_contractors': pending_contractors_list,
            # フィルター関連
            'contractor_filter': contractor_filter,
            'contractor_choices': contractor_choices,
            'amount_min': amount_min,
            'amount_max': amount_max,
            'payment_cycle_filter': payment_cycle_filter,
            'payment_cycle_choices': payment_cycle_choices,
            'worker_type_filter': worker_type_filter,
            'worker_type_choices': worker_type_choices,
            'has_bank_info': has_bank_info,
            'bank_info_choices': bank_info_choices,
            'date_filter_type': date_filter_type,
            'date_filter_type_choices': date_filter_type_choices,
            'date_start': date_start,
            'date_end': date_end,
        })

        return context