from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q, Sum, Count, Case, When, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Project
import calendar


class ReceiptDashboardView(TemplateView):
    template_name = 'order_management/receipt_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 現在の月を取得（デフォルト）
        now = timezone.now()
        year = int(self.request.GET.get('year', now.year))
        month = int(self.request.GET.get('month', now.month))
        status_filter = self.request.GET.get('status', 'all')

        # 月の開始日と終了日
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()

        # 入金ベース：今月入金予定の案件のみ
        base_query = Project.objects.filter(
            payment_due_date__gte=start_date,
            payment_due_date__lte=end_date,
            estimate_amount__gt=0
        ).exclude(
            contractor_name__isnull=True
        ).exclude(
            contractor_name=''
        )

        # 入金状況による絞り込み
        if status_filter == 'received':
            # 入金済み（工事完了済み案件と仮定）
            base_query = base_query.filter(work_end_completed=True)
        elif status_filter == 'pending':
            # 入金待ち（未完了案件）
            base_query = base_query.filter(work_end_completed=False)
        elif status_filter == 'overdue':
            # 遅延（入金予定日を過ぎている案件）
            today = timezone.now().date()
            base_query = base_query.filter(
                payment_due_date__lt=today,
                work_end_completed=False
            )

        receipt_projects = base_query.order_by('contractor_name', 'payment_due_date')

        # 発注元別の集計データ
        client_summary = {}

        # 今月の入金統計（入金ベース）
        monthly_receipt_stats = {
            'pending_amount': 0,    # 入金待ち
            'received_amount': 0,   # 入金済み
            'overdue_amount': 0,    # 遅延
            'total_receipt': 0      # 今月の総入金予定額
        }

        for project in receipt_projects:
            client_name = project.contractor_name
            if client_name not in client_summary:
                client_summary[client_name] = {
                    'client_name': client_name,
                    'projects': [],
                    'total_amount': 0,
                    'received_amount': 0,
                    'pending_amount': 0,
                    'overdue_amount': 0,
                    'project_count': 0
                }

            # 入金金額の決定
            amount = project.billing_amount or project.estimate_amount or 0

            client_summary[client_name]['projects'].append(project)
            client_summary[client_name]['total_amount'] += amount
            client_summary[client_name]['project_count'] += 1

            # 入金状況別の集計
            today = timezone.now().date()
            if project.work_end_completed:
                # 工事完了済み = 入金済みと仮定
                client_summary[client_name]['received_amount'] += amount
                monthly_receipt_stats['received_amount'] += amount
            elif project.payment_due_date and project.payment_due_date < today:
                # 入金予定日を過ぎている = 遅延
                client_summary[client_name]['overdue_amount'] += amount
                monthly_receipt_stats['overdue_amount'] += amount
            else:
                # その他 = 入金待ち
                client_summary[client_name]['pending_amount'] += amount
                monthly_receipt_stats['pending_amount'] += amount

            monthly_receipt_stats['total_receipt'] += amount

        # 統計情報（入金ベース）
        stats = {
            'total_clients': len(client_summary),
            'total_projects': receipt_projects.count(),
            'total_receipt': monthly_receipt_stats['total_receipt'],
            'pending_amount': monthly_receipt_stats['pending_amount'],
            'received_amount': monthly_receipt_stats['received_amount'],
            'overdue_amount': monthly_receipt_stats['overdue_amount'],
        }

        # 入金状況の選択肢
        receipt_status_choices = [
            ('all', 'すべて'),
            ('pending', '入金待ち'),
            ('received', '入金済み'),
            ('overdue', '遅延'),
        ]

        context.update({
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'status_filter': status_filter,
            'receipt_status_choices': receipt_status_choices,
            'client_summary': client_summary,
            'receipt_projects': receipt_projects,
            'stats': stats,
            'start_date': start_date,
            'end_date': end_date,
        })

        return context