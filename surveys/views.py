from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count
import json
from datetime import date, timedelta

from .models import Survey, SurveyRoom, SurveyWall, SurveyDamage, SurveyPhoto, Surveyor
from order_management.models import Project
from .views_ext import SurveyRecordDetailView, ProjectSurveyListView, ProjectSurveyCreateView


class FieldSurveyorMixin:
    """現場調査員専用のアクセス制御Mixin"""

    def dispatch(self, request, *args, **kwargs):
        # ログインチェック
        if not request.user.is_authenticated:
            from django.contrib import messages
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
            from django.contrib import messages
            from django.contrib.auth import logout
            messages.error(request, 'このアカウントは現場調査員として登録されていません。')
            logout(request)
            return redirect('surveys:field_login')

        return super().dispatch(request, *args, **kwargs)


class SurveyListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """調査一覧画面（改良版）"""
    model = Survey
    template_name = 'surveys/survey_list_enhanced.html'
    context_object_name = 'surveys'
    paginate_by = 10

    def test_func(self):
        """管理者のみアクセス可能"""
        return self.request.user.is_staff

    def handle_no_permission(self):
        """権限がない場合の処理"""
        from django.shortcuts import redirect
        from django.urls import reverse

        # 現在のパスを含めて権限ガイダンスページにリダイレクト
        permission_url = reverse('order_management:permission_denied')
        current_path = self.request.get_full_path()
        return redirect(f"{permission_url}?next={current_path}")

    def get_queryset(self):
        queryset = Survey.objects.select_related('project', 'surveyor').prefetch_related(
            'rooms', 'damages', 'photos'
        )

        # フィルタリング
        status = self.request.GET.get('status')
        surveyor = self.request.GET.get('surveyor')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        search = self.request.GET.get('search')

        if status:
            queryset = queryset.filter(status=status)
        if surveyor:
            queryset = queryset.filter(surveyor_id=surveyor)
        if date_from:
            queryset = queryset.filter(scheduled_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(scheduled_date__lte=date_to)
        if search:
            queryset = queryset.filter(
                Q(project__site_name__icontains=search) |
                Q(project__management_no__icontains=search) |
                Q(surveyor__name__icontains=search)
            )

        return queryset.order_by('-scheduled_date', '-scheduled_start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 統計情報
        context['total_surveys'] = Survey.objects.count()
        context['in_progress_surveys'] = Survey.objects.filter(status='in_progress').count()
        context['scheduled_surveys'] = Survey.objects.filter(status='scheduled').count()
        context['completed_surveys'] = Survey.objects.filter(status='completed').count()
        context['cancelled_surveys'] = Survey.objects.filter(status='cancelled').count()

        # 承認関連統計
        context['pending_approval_surveys'] = Survey.objects.filter(status='pending_approval').count()
        context['approved_surveys'] = Survey.objects.filter(status='approved').count()
        context['rejected_surveys'] = Survey.objects.filter(status='rejected').count()

        # 承認待ち調査一覧（親方用）
        context['pending_approval_list'] = Survey.objects.filter(
            status='pending_approval'
        ).select_related('project', 'surveyor').order_by('-updated_at')[:10]

        # 今日のスケジュール
        today = timezone.now().date()
        context['today_surveys'] = Survey.objects.filter(
            scheduled_date=today
        ).select_related('project', 'surveyor').order_by('scheduled_start_time')

        # 今週のスケジュール
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        context['week_surveys'] = Survey.objects.filter(
            scheduled_date__gte=week_start,
            scheduled_date__lte=week_end
        ).count()

        # フィルター用データ
        context['surveyors'] = Surveyor.objects.filter(assigned_surveys__isnull=False).distinct()
        context['filter_params'] = self.request.GET.copy()

        return context


class SurveyDetailView(LoginRequiredMixin, DetailView):
    """調査詳細画面"""
    model = Survey
    template_name = 'surveys/survey_detail.html'
    context_object_name = 'survey'


class SurveyCreateView(LoginRequiredMixin, CreateView):
    """調査作成画面"""
    model = Survey
    template_name = 'surveys/survey_create.html'
    fields = ['project', 'surveyor', 'scheduled_date', 'scheduled_start_time', 'estimated_duration']
    success_url = reverse_lazy('surveys:survey_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['surveyors'] = Surveyor.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # プロジェクトの現地調査ステータスを更新
        project = form.instance.project
        project.survey_status = 'scheduled'
        project.save()
        return response


class SurveyScheduleView(LoginRequiredMixin, ListView):
    """現地調査スケジュール管理画面"""
    model = Survey
    template_name = 'surveys/survey_schedule.html'
    context_object_name = 'surveys'

    def get_queryset(self):
        return Survey.objects.select_related('project', 'surveyor').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 統計情報
        context['total_surveys'] = Survey.objects.count()
        context['in_progress_surveys'] = Survey.objects.filter(status='in_progress').count()
        context['scheduled_surveys'] = Survey.objects.filter(status='scheduled').count()
        context['completed_surveys'] = Survey.objects.filter(status='completed').count()

        # 今日のスケジュール
        today = timezone.now().date()
        context['today_surveys'] = Survey.objects.filter(
            scheduled_date=today
        ).select_related('project', 'surveyor')

        # フィルター用データ
        context['projects'] = Project.objects.filter(survey_required=True)
        context['surveyors'] = Surveyor.objects.filter(is_active=True)

        return context


class SurveyFormView(FieldSurveyorMixin, DetailView):
    """現地調査実施画面（現場調査員用）"""
    model = Survey
    template_name = 'surveys/survey_form.html'
    context_object_name = 'survey'

    def get_object(self):
        """自分に割り当てられた調査のみ取得"""
        pk = self.kwargs.get('pk')
        return get_object_or_404(Survey, pk=pk, surveyor=self.request.surveyor)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = self.object.rooms.prefetch_related('walls')
        context['damages'] = self.object.damages.all()
        context['photos'] = self.object.photos.all()
        return context


class SurveyUpdateView(LoginRequiredMixin, UpdateView):
    """調査編集画面"""
    model = Survey
    template_name = 'surveys/survey_edit.html'
    fields = ['project', 'surveyor', 'scheduled_date', 'scheduled_start_time', 'estimated_duration', 'notes']


class SurveyStartView(FieldSurveyorMixin, View):
    """調査開始画面（現場調査員用）"""

    def get(self, request, pk):
        """調査開始確認画面を表示"""
        # 自分に割り当てられた調査のみアクセス可能
        survey = get_object_or_404(Survey, pk=pk, surveyor=request.surveyor)
        context = {
            'survey': survey,
            'rooms': survey.rooms.prefetch_related('walls'),
            'damages': survey.damages.all(),
            'photos': survey.photos.all(),
        }
        return render(request, 'surveys/survey_start.html', context)

    def post(self, request, pk):
        """調査を開始して記録フォームにリダイレクト"""
        # 自分に割り当てられた調査のみ操作可能
        survey = get_object_or_404(Survey, pk=pk, surveyor=request.surveyor)

        # 調査ステータスを進行中に更新
        survey.status = 'in_progress'
        survey.actual_start_time = timezone.now()
        survey.save()

        # 成功メッセージ
        messages.success(request, f'調査「{survey.project.site_name}」を開始しました')

        # 直接 surveys アプリ内で調査記録管理をする場合
        # （projects.models.Survey との連携をスキップ）

        # surveys アプリ内で調査記録を管理する場合は、
        # survey_record_form を surveys アプリ内のビューにリダイレクト
        # 例: surveys:survey_form
        return redirect('surveys:survey_form', pk=survey.pk)


class SurveyCompleteView(FieldSurveyorMixin, DetailView):
    """調査完了画面（現場調査員用）"""
    model = Survey
    template_name = 'surveys/survey_complete.html'
    context_object_name = 'survey'

    def get_object(self):
        """自分に割り当てられた調査のみ取得"""
        pk = self.kwargs.get('pk')
        return get_object_or_404(Survey, pk=pk, surveyor=self.request.surveyor)


class SurveyReportView(LoginRequiredMixin, DetailView):
    """調査レポート画面"""
    model = Survey
    template_name = 'surveys/survey_report.html'
    context_object_name = 'survey'


class SurveyDeleteView(LoginRequiredMixin, View):
    """調査削除"""

    def post(self, request, pk):
        """調査を削除"""
        survey = get_object_or_404(Survey, pk=pk)

        try:
            survey_name = f"{survey.project.site_name}"
            survey.delete()

            messages.success(request, f'調査「{survey_name}」を削除しました')

            # AJAX リクエストの場合はJSON レスポンス
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f'調査「{survey_name}」を削除しました'})

            return redirect('surveys:survey_list')

        except Exception as e:
            error_message = f'削除エラー: {str(e)}'

            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message})

            messages.error(request, error_message)
            return redirect('surveys:survey_list')


# API Views
@csrf_exempt
def survey_start_api(request, pk):
    """調査開始API"""
    if request.method == 'POST':
        survey = get_object_or_404(Survey, pk=pk)
        survey.status = 'in_progress'
        survey.actual_start_time = timezone.now()
        survey.save()

        return JsonResponse({
            'success': True,
            'message': '調査を開始しました',
            'start_time': survey.actual_start_time.strftime('%H:%M')
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def survey_save_api(request, pk):
    """調査データ保存API"""
    if request.method == 'POST':
        survey = get_object_or_404(Survey, pk=pk)

        try:
            data = json.loads(request.body)

            # 部屋データの保存
            if 'rooms' in data:
                for room_data in data['rooms']:
                    room, created = SurveyRoom.objects.get_or_create(
                        survey=survey,
                        room_name=room_data['name']
                    )

                    # 壁面データの保存
                    if 'walls' in room_data:
                        for wall_data in room_data['walls']:
                            SurveyWall.objects.update_or_create(
                                room=room,
                                direction=wall_data['direction'],
                                defaults={
                                    'length': wall_data.get('length', 0),
                                    'height': wall_data.get('height', 0),
                                    'opening_area': wall_data.get('opening_area', 0),
                                    'foundation_type': wall_data.get('foundation_type', 'gypsum_board'),
                                    'foundation_condition': wall_data.get('foundation_condition', 'good'),
                                }
                            )

            # 損傷データの保存
            if 'damages' in data:
                for damage_data in data['damages']:
                    SurveyDamage.objects.update_or_create(
                        survey=survey,
                        damage_type=damage_data['type'],
                        defaults={
                            'has_dents': damage_data.get('has_dents', False),
                            'dent_count': damage_data.get('dent_count', 0),
                            'description': damage_data.get('description', ''),
                        }
                    )

            # 備考の保存
            if 'notes' in data:
                survey.notes = data['notes']
                survey.save()

            return JsonResponse({'success': True, 'message': 'データを保存しました'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'エラー: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def survey_complete_api(request, pk):
    """調査完了API"""
    if request.method == 'POST':
        survey = get_object_or_404(Survey, pk=pk)
        survey.status = 'pending_approval'  # 承認待ちステータスに変更
        survey.actual_end_time = timezone.now()
        survey.save()

        return JsonResponse({
            'success': True,
            'message': '調査が完了し、承認待ち状態になりました',
            'end_time': survey.actual_end_time.strftime('%H:%M'),
            'duration': survey.get_actual_duration_minutes()
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def survey_approve_api(request, pk):
    """調査承認/差し戻しAPI"""
    if request.method == 'POST':
        # 管理者のみアクセス可能
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': '権限がありません'})

        survey = get_object_or_404(Survey, pk=pk)
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        try:
            if action == 'approve':
                # 承認処理
                survey.approve(approved_by=request.user.username, approval_notes=notes)
                return JsonResponse({
                    'success': True,
                    'message': f'調査「{survey.project.site_name}」を承認しました',
                    'status': 'approved'
                })
            elif action == 'reject':
                # 差し戻し処理
                if not notes.strip():
                    return JsonResponse({'success': False, 'message': '差し戻し理由を入力してください'})

                survey.reject(approved_by=request.user.username, approval_notes=notes)
                return JsonResponse({
                    'success': True,
                    'message': f'調査「{survey.project.site_name}」を差し戻しました',
                    'status': 'rejected'
                })
            else:
                return JsonResponse({'success': False, 'message': '無効なアクションです'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'エラー: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
