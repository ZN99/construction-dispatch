from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Surveyor, Survey, SurveyWorkflowStep, SurveyStepProgress


class FieldSurveyorLoginView(View):
    """現場調査員専用ログイン画面"""
    template_name = 'surveys/field/login.html'

    def get(self, request):
        # 既にログイン済みで調査員プロファイルがある場合はダッシュボードにリダイレクト
        if request.user.is_authenticated:
            try:
                surveyor = Surveyor.objects.get(user=request.user)
                return redirect('surveys:field_dashboard')
            except Surveyor.DoesNotExist:
                # 調査員プロファイルがない場合は本部用にリダイレクト
                return redirect('dashboard')

        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'ユーザー名とパスワードを入力してください。')
            return render(request, self.template_name)

        # 認証を試行
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 調査員プロファイルの存在確認
            try:
                surveyor = Surveyor.objects.get(user=user, is_active=True)
                login(request, user)

                # セッションに調査員情報を保存
                request.session['is_field_surveyor'] = True
                request.session['surveyor_id'] = surveyor.id
                request.session['surveyor_name'] = surveyor.name

                messages.success(request, f'{surveyor.name}さん、ログインしました。')

                # AJAX リクエストの場合
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('surveys:field_dashboard')
                    })

                return redirect('surveys:field_dashboard')

            except Surveyor.DoesNotExist:
                messages.error(request, 'このアカウントは現場調査員として登録されていません。')
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません。')

        # AJAX エラーレスポンス
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'ログインに失敗しました。'
            })

        return render(request, self.template_name)


class FieldSurveyorLogoutView(View):
    """現場調査員専用ログアウト"""

    def get(self, request):
        return self.post(request)

    def post(self, request):
        if request.user.is_authenticated:
            surveyor_name = request.session.get('surveyor_name', '')
            logout(request)
            if surveyor_name:
                messages.success(request, f'{surveyor_name}さん、ログアウトしました。')
            else:
                messages.success(request, 'ログアウトしました。')

        return redirect('order_management:landing')


class FieldSurveyorMixin:
    """現場調査員専用のアクセス制御Mixin"""

    def dispatch(self, request, *args, **kwargs):
        # ログインチェック
        if not request.user.is_authenticated:
            messages.warning(request, 'ログインが必要です。')
            return redirect('surveys:field_login')

        # 現場調査員プロファイルのチェック
        try:
            surveyor = Surveyor.objects.get(user=request.user, is_active=True)
            # リクエストオブジェクトに調査員情報を追加
            request.surveyor = surveyor

            # セッションに調査員情報が不足している場合は補完
            if not request.session.get('is_field_surveyor'):
                request.session['is_field_surveyor'] = True
                request.session['surveyor_id'] = surveyor.id
                request.session['surveyor_name'] = surveyor.name

        except Surveyor.DoesNotExist:
            # 本部スタッフの場合は親切に案内
            if request.user.is_staff:
                messages.info(request, '本部スタッフの方は本部システムをご利用ください。')
                return redirect('order_management:dashboard')
            else:
                messages.error(request, 'このアカウントは現場調査員として登録されていません。')
                logout(request)
                return redirect('surveys:field_login')

        return super().dispatch(request, *args, **kwargs)


# 現場調査員専用のダッシュボードビュー
from django.views.generic import TemplateView
from django.db.models import Q
from django.utils import timezone
from datetime import date, timedelta

class FieldSurveyorDashboardView(FieldSurveyorMixin, TemplateView):
    """現場調査員専用ダッシュボード"""
    template_name = 'surveys/field/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surveyor = self.request.surveyor

        today = timezone.now().date()

        # 今日の調査
        context['today_surveys'] = surveyor.assigned_surveys.filter(
            scheduled_date=today,
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_start_time')

        # 今週の調査（今日を除く）
        week_start = today + timedelta(days=1)
        week_end = today + timedelta(days=7)
        context['week_surveys'] = surveyor.assigned_surveys.filter(
            scheduled_date__range=[week_start, week_end],
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_date', 'scheduled_start_time')[:10]

        # 進行中の調査
        context['in_progress_surveys'] = surveyor.assigned_surveys.filter(
            status='in_progress'
        ).order_by('scheduled_date')

        # 最近完了した調査
        context['recent_completed'] = surveyor.assigned_surveys.filter(
            status='completed'
        ).order_by('-scheduled_date')[:5]

        # 統計情報
        context['stats'] = {
            'today_count': context['today_surveys'].count(),
            'week_count': context['week_surveys'].count(),
            'in_progress_count': context['in_progress_surveys'].count(),
            'completed_this_month': surveyor.assigned_surveys.filter(
                status='completed',
                scheduled_date__year=today.year,
                scheduled_date__month=today.month
            ).count(),
            'pending_approval_count': surveyor.assigned_surveys.filter(
                status='pending_approval'
            ).count(),
            'approved_count': surveyor.assigned_surveys.filter(
                status='approved'
            ).count(),
            'rejected_count': surveyor.assigned_surveys.filter(
                status='rejected'
            ).count(),
        }

        # 承認関連調査一覧
        context['pending_approval_surveys'] = surveyor.assigned_surveys.filter(
            status='pending_approval'
        ).order_by('-updated_at')[:5]

        context['recent_approved'] = surveyor.assigned_surveys.filter(
            status='approved'
        ).order_by('-approved_at')[:5]

        context['recent_rejected'] = surveyor.assigned_surveys.filter(
            status='rejected'
        ).order_by('-updated_at')[:5]

        return context


class FieldSurveyorSurveyListView(FieldSurveyorMixin, ListView):
    """現場調査員専用の調査一覧"""
    model = Survey
    template_name = 'surveys/field/survey_list.html'
    context_object_name = 'surveys'
    paginate_by = 20

    def get_queryset(self):
        """自分に割り当てられた調査のみ取得"""
        surveyor = self.request.surveyor
        queryset = surveyor.assigned_surveys.all().order_by('-scheduled_date', '-scheduled_start_time')

        # ステータスフィルタ
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surveyor = self.request.surveyor

        # 統計情報
        context['stats'] = {
            'total': surveyor.assigned_surveys.count(),
            'scheduled': surveyor.assigned_surveys.filter(status='scheduled').count(),
            'in_progress': surveyor.assigned_surveys.filter(status='in_progress').count(),
            'completed': surveyor.assigned_surveys.filter(status='completed').count(),
        }

        return context


class FieldSurveyorProfileView(FieldSurveyorMixin, TemplateView):
    """現場調査員のプロファイル表示"""
    template_name = 'surveys/field/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surveyor = self.request.surveyor

        # 統計情報
        context['stats'] = {
            'total_surveys': surveyor.assigned_surveys.count(),
            'completed_surveys': surveyor.assigned_surveys.filter(status='completed').count(),
            'in_progress_surveys': surveyor.assigned_surveys.filter(status='in_progress').count(),
            'scheduled_surveys': surveyor.assigned_surveys.filter(status='scheduled').count(),
        }

        # 月別統計（過去6か月）
        from django.db.models import Count
        from django.utils import timezone
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        monthly_stats = []
        for i in range(6):
            date = timezone.now().date() - relativedelta(months=i)
            count = surveyor.assigned_surveys.filter(
                scheduled_date__year=date.year,
                scheduled_date__month=date.month,
                status='completed'
            ).count()
            monthly_stats.append({
                'month': date.strftime('%Y年%m月'),
                'count': count
            })

        context['monthly_stats'] = list(reversed(monthly_stats))
        return context


class FieldSurveyorChecklistView(FieldSurveyorMixin, TemplateView):
    """現場調査員専用チェックリストビュー"""
    template_name = 'surveys/field/checklist.html'

    def dispatch(self, request, *args, **kwargs):
        # 親クラスの認証チェックを実行
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'status_code') and response.status_code != 200:
            return response

        # 調査へのアクセス権限をチェック
        survey_id = kwargs.get('survey_id')
        try:
            survey = Survey.objects.get(id=survey_id, surveyor=request.surveyor)
            # 調査の状態チェック
            if survey.status not in ['scheduled', 'in_progress', 'pending_approval', 'approved', 'rejected']:
                messages.error(request, 'この調査はアクセスできません。')
                return redirect('surveys:field_dashboard')
        except Survey.DoesNotExist:
            messages.error(request, 'アクセス権限がありません。この調査は他の調査員に割り当てられているか、存在しません。')
            return redirect('surveys:field_dashboard')

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_id = self.kwargs.get('survey_id')
        survey = get_object_or_404(Survey, id=survey_id, surveyor=self.request.surveyor)

        # 現在のステップを取得
        current_step_id = self.request.GET.get('step')
        if current_step_id:
            current_step = get_object_or_404(SurveyWorkflowStep, id=current_step_id)
        else:
            # 最初の未完了ステップを取得
            current_step = self._get_next_step(survey)

        # 全ステップの進捗を取得
        steps_progress = self._get_steps_progress(survey)

        # 現在の部屋と壁面情報を取得
        current_room = survey.rooms.first()
        current_wall = None
        if current_room and current_step.step_type == 'wall_measurement':
            current_wall = current_room.walls.first()

        # 前のステップのIDを計算
        all_steps = SurveyWorkflowStep.objects.all().order_by('step_number')
        previous_step_id = None
        for i, step in enumerate(all_steps):
            if step.id == current_step.id and i > 0:
                previous_step_id = all_steps[i-1].id
                break

        # 調査員情報を追加
        context.update({
            'survey': survey,
            'current_step': current_step,
            'steps_progress': steps_progress,
            'current_room': current_room,
            'current_wall': current_wall,
            'completion_percentage': self._calculate_completion_percentage(steps_progress),
            'previous_step_id': previous_step_id,
            'all_steps': all_steps,
            'surveyor': self.request.surveyor,
            'is_field_survey': True,  # テンプレートで調査員版であることを識別
        })

        return context

    def _get_next_step(self, survey):
        """次の未完了ステップを取得"""
        steps = SurveyWorkflowStep.objects.all().order_by('step_number')

        for step in steps:
            progress = SurveyStepProgress.objects.filter(
                survey=survey,
                workflow_step=step
            ).first()

            if not progress or progress.status != 'completed':
                return step

        # 全て完了している場合は最後のステップを返す
        return steps.last()

    def _get_steps_progress(self, survey):
        """全ステップの進捗状況を取得"""
        steps = SurveyWorkflowStep.objects.all().order_by('step_number')
        progress_data = []

        for step in steps:
            progress = SurveyStepProgress.objects.filter(
                survey=survey,
                workflow_step=step
            ).first()

            progress_data.append({
                'step': step,
                'progress': progress,
                'is_completed': progress and progress.status == 'completed',
                'is_current': progress and progress.status == 'in_progress',
            })

        return progress_data

    def _calculate_completion_percentage(self, steps_progress):
        """完了率を計算"""
        total_steps = len(steps_progress)
        completed_steps = sum(1 for p in steps_progress if p['is_completed'])

        if total_steps == 0:
            return 0

        return int((completed_steps / total_steps) * 100)