from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.utils import timezone
from datetime import date
import json

from .models import Survey, SurveyWorkflowStep, SurveyStepProgress, SurveyRoom, SurveyWall, SurveyPhoto, Surveyor
from order_management.models import Project


class DemoSurveyListView(TemplateView):
    """デモ用調査一覧ビュー"""
    template_name = 'surveys/demo_survey_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context


class CrossReplacementChecklistView(TemplateView):
    """クロス張り替え調査チェックリストビュー"""
    template_name = 'surveys/cross_replacement_checklist.html'

    def get_template_names(self):
        """モバイルデバイスまたはシンプルUIパラメータが指定された場合は専用テンプレートを使用"""
        if self._is_mobile_or_simple_ui():
            return ['surveys/mobile_elderly_checklist.html']
        return [self.template_name]

    def _is_mobile_or_simple_ui(self):
        """モバイルデバイスまたはシンプルUIパラメータの判定"""
        # URLパラメータで明示的に指定された場合
        if (self.request.GET.get('mobile') == '1' or
            self.request.GET.get('elderly') == '1' or  # 後方互換性のため残す
            self.request.GET.get('simple') == '1'):
            return True

        # User-Agentでモバイルデバイスを判定
        user_agent = self.request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
        return any(keyword in user_agent for keyword in mobile_keywords)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_id = self.kwargs.get('survey_id') or self.kwargs.get('pk')
        survey = get_object_or_404(Survey, id=survey_id)

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

        context.update({
            'survey': survey,
            'current_step': current_step,
            'steps_progress': steps_progress,
            'current_room': current_room,
            'current_wall': current_wall,
            'completion_percentage': self._calculate_completion_percentage(steps_progress),
            'previous_step_id': previous_step_id,
            'all_steps': all_steps,
        })

        return context

    def _get_next_step(self, survey):
        """次の未完了ステップを取得"""
        # まずはクロス張り替え用の基本ステップを定義順で取得
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


@csrf_exempt
def start_step(request, survey_id, step_id):
    """ステップ開始API"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    survey = get_object_or_404(Survey, id=survey_id)
    step = get_object_or_404(SurveyWorkflowStep, id=step_id)

    progress, created = SurveyStepProgress.objects.get_or_create(
        survey=survey,
        workflow_step=step,
        defaults={
            'status': 'in_progress',
            'started_at': timezone.now()
        }
    )

    if not created and progress.status == 'not_started':
        progress.status = 'in_progress'
        progress.started_at = timezone.now()
        progress.save()

    return JsonResponse({
        'success': True,
        'step_id': step.id,
        'status': progress.status
    })


@csrf_exempt
def complete_step(request, survey_id, step_id):
    """ステップ完了API"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    survey = get_object_or_404(Survey, id=survey_id)
    step = get_object_or_404(SurveyWorkflowStep, id=step_id)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    progress, created = SurveyStepProgress.objects.get_or_create(
        survey=survey,
        workflow_step=step,
        defaults={
            'status': 'completed',
            'started_at': timezone.now(),
            'completed_at': timezone.now(),
            'data': data
        }
    )

    if not created:
        progress.status = 'completed'
        progress.completed_at = timezone.now()
        progress.data.update(data)
        progress.save()

    # 次のステップIDを取得
    next_step = _get_next_incomplete_step(survey)

    # 全ステップ完了チェック
    is_fully_completed = next_step is None

    if is_fully_completed and survey.status in ['scheduled', 'in_progress']:
        # 全ステップ完了時に調査を承認待ちステータスに変更
        survey.status = 'pending_approval'
        survey.actual_end_time = timezone.now()
        survey.save()

    return JsonResponse({
        'success': True,
        'step_id': step.id,
        'next_step_id': next_step.id if next_step else None,
        'completion_percentage': _calculate_overall_completion(survey),
        'survey_completed': is_fully_completed,
        'survey_status': survey.get_status_display()
    })


def _get_next_incomplete_step(survey):
    """次の未完了ステップを取得"""
    steps = SurveyWorkflowStep.objects.all().order_by('step_number')

    for step in steps:
        progress = SurveyStepProgress.objects.filter(
            survey=survey,
            workflow_step=step
        ).first()

        if not progress or progress.status != 'completed':
            return step

    return None


def _calculate_overall_completion(survey):
    """全体完了率を計算"""
    total_steps = SurveyWorkflowStep.objects.count()
    completed_steps = SurveyStepProgress.objects.filter(
        survey=survey,
        status='completed'
    ).count()

    if total_steps == 0:
        return 0

    return int((completed_steps / total_steps) * 100)


@csrf_exempt
def upload_step_photo(request, survey_id, step_id):
    """ステップ用写真アップロードAPI"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    survey = get_object_or_404(Survey, id=survey_id)
    step = get_object_or_404(SurveyWorkflowStep, id=step_id)

    if 'photo' not in request.FILES:
        return JsonResponse({'error': 'No photo uploaded'}, status=400)

    photo_file = request.FILES['photo']
    caption = request.POST.get('caption', '')

    # 写真の種別を決定
    photo_type = 'wall_condition'
    if step.step_type == 'room_setup':
        photo_type = 'room_overview'
    elif step.step_type == 'damage_assessment':
        photo_type = 'damage_detail'

    photo = SurveyPhoto.objects.create(
        survey=survey,
        photo_type=photo_type,
        image=photo_file,
        caption=caption
    )

    return JsonResponse({
        'success': True,
        'photo_id': photo.id,
        'photo_url': photo.image.url if photo.image else None
    })


@csrf_exempt
def delete_photo(request, survey_id, photo_id):
    """写真削除API"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'DELETE method required'}, status=405)

    survey = get_object_or_404(Survey, id=survey_id)
    photo = get_object_or_404(SurveyPhoto, id=photo_id, survey=survey)

    try:
        # ファイルも削除
        if photo.image:
            photo.image.delete()
        photo.delete()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_photo_caption(request, survey_id, photo_id):
    """写真キャプション更新API"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    survey = get_object_or_404(Survey, id=survey_id)
    photo = get_object_or_404(SurveyPhoto, id=photo_id, survey=survey)

    try:
        data = json.loads(request.body) if request.body else {}
        caption = data.get('caption', '')

        photo.caption = caption
        photo.save()

        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def save_measurement_data(request, survey_id, step_id):
    """測定データ保存API"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    survey = get_object_or_404(Survey, id=survey_id)
    step = get_object_or_404(SurveyWorkflowStep, id=step_id)

    try:
        data = json.loads(request.body) if request.body else {}
        room_id = data.get('room_id')
        wall_id = data.get('wall_id')
        measurements = data.get('measurements', {})

        # 測定データをステップ進捗に保存
        progress, created = SurveyStepProgress.objects.get_or_create(
            survey=survey,
            workflow_step=step,
            defaults={
                'status': 'in_progress',
                'started_at': timezone.now(),
                'data': {}
            }
        )

        # 既存データを更新
        if not progress.data:
            progress.data = {}

        if 'measurements' not in progress.data:
            progress.data['measurements'] = {}

        if room_id not in progress.data['measurements']:
            progress.data['measurements'][room_id] = {}

        progress.data['measurements'][room_id][wall_id] = measurements
        progress.save()

        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_step_completion_status(request, survey_id):
    """ステップ完了状況更新API"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    survey = get_object_or_404(Survey, id=survey_id)

    try:
        data = json.loads(request.body) if request.body else {}
        step_type = data.get('step_type')
        is_completed = data.get('completed', False)

        if not step_type:
            return JsonResponse({'error': 'step_type is required'}, status=400)

        # ステップタイプに基づいて該当するステップを取得
        try:
            step = SurveyWorkflowStep.objects.get(step_type=step_type)
        except SurveyWorkflowStep.DoesNotExist:
            return JsonResponse({'error': f'Step with type {step_type} not found'}, status=404)

        # ステップ進捗を取得または作成
        progress, created = SurveyStepProgress.objects.get_or_create(
            survey=survey,
            workflow_step=step,
            defaults={
                'status': 'completed' if is_completed else 'not_started',
                'started_at': timezone.now() if is_completed else None,
                'completed_at': timezone.now() if is_completed else None,
                'data': {}
            }
        )

        if not created:
            # 既存の進捗を更新
            if is_completed:
                progress.status = 'completed'
                if not progress.started_at:
                    progress.started_at = timezone.now()
                progress.completed_at = timezone.now()
            else:
                progress.status = 'not_started'
                progress.completed_at = None
            progress.save()

        return JsonResponse({
            'success': True,
            'step_type': step_type,
            'completed': is_completed,
            'status': progress.status
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class SurveyFormRedirectView(View):
    """調査フォームアクセス時のリダイレクト判定ビュー"""

    def dispatch(self, request, *args, **kwargs):
        survey_id = self.kwargs.get('pk')

        # ログインチェック
        if not request.user.is_authenticated:
            return redirect('surveys:field_login')

        # 調査員かどうかチェック
        try:
            surveyor = Surveyor.objects.get(user=request.user, is_active=True)
            # 調査員の場合は専用画面にリダイレクト
            return redirect('surveys:field_survey_checklist', survey_id=survey_id)
        except Surveyor.DoesNotExist:
            # 調査員でない場合（本部スタッフ等）は一般チェックリスト画面
            return redirect('surveys:cross_replacement_checklist', survey_id=survey_id)