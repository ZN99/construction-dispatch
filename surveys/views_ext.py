"""追加のView定義"""
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Survey, Surveyor
from order_management.models import Project


class SurveyRecordDetailView(LoginRequiredMixin, DetailView):
    """調査記録詳細画面（改良版）"""
    model = Survey
    template_name = 'surveys/survey_record_detail.html'
    context_object_name = 'survey'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.object

        # 関連データ
        context['rooms'] = survey.rooms.prefetch_related('walls')
        context['damages'] = survey.damages.all()
        context['photos'] = survey.photos.all().order_by('-uploaded_at')

        # 写真を種別ごとに分類
        photos_by_type = {}
        for photo in context['photos']:
            type_key = photo.get_photo_type_display()
            if type_key not in photos_by_type:
                photos_by_type[type_key] = []
            photos_by_type[type_key].append(photo)
        context['photos_by_type'] = photos_by_type

        # 統計情報
        context['wall_count'] = survey.get_total_wall_count()
        context['room_count'] = survey.rooms.count()
        context['damage_count'] = survey.damages.count()
        context['photo_count'] = survey.photos.count()

        # 履歴情報（今後実装用のプレースホルダー）
        context['history'] = []
        context['related_files'] = []

        return context


class ProjectSurveyListView(LoginRequiredMixin, ListView):
    """案件に紐づく調査一覧"""
    model = Survey
    template_name = 'surveys/project_survey_list.html'
    context_object_name = 'surveys'

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Survey.objects.filter(project_id=project_id).select_related('surveyor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        context['project'] = get_object_or_404(Project, pk=project_id)

        # 統計情報を追加
        surveys = context['surveys']
        context['stats'] = {
            'total': surveys.count(),
            'scheduled': surveys.filter(status='scheduled').count(),
            'in_progress': surveys.filter(status='in_progress').count(),
            'completed': surveys.filter(status='completed').count(),
            'cancelled': surveys.filter(status='cancelled').count(),
        }

        return context


class ProjectSurveyCreateView(LoginRequiredMixin, CreateView):
    """案件に紐づく調査作成"""
    model = Survey
    template_name = 'surveys/project_survey_create.html'
    fields = ['surveyor', 'scheduled_date', 'scheduled_start_time', 'estimated_duration']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        context['project'] = get_object_or_404(Project, pk=project_id)
        context['surveyors'] = Surveyor.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        project_id = self.kwargs['project_id']
        form.instance.project_id = project_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('order_management:project_detail', kwargs={'pk': self.kwargs['project_id']})