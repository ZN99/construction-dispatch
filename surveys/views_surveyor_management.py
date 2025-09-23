from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date

from .models import Surveyor, Survey


class SurveyorListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """調査員一覧"""
    model = Surveyor
    template_name = 'surveys/surveyor/list.html'
    context_object_name = 'surveyors'
    paginate_by = 20

    def test_func(self):
        """管理者のみアクセス可能"""
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = Surveyor.objects.annotate(
            current_surveys=Count('assigned_surveys', filter=Q(assigned_surveys__status__in=['scheduled', 'in_progress'])),
            completed_surveys=Count('assigned_surveys', filter=Q(assigned_surveys__status='completed'))
        )

        # フィルタリング
        status = self.request.GET.get('status')
        department = self.request.GET.get('department')
        search = self.request.GET.get('search')

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        if department:
            queryset = queryset.filter(department__icontains=department)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(department__icontains=search)
            )

        return queryset.order_by('-is_active', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 統計情報
        context['total_surveyors'] = Surveyor.objects.count()
        context['active_surveyors'] = Surveyor.objects.filter(is_active=True).count()
        context['inactive_surveyors'] = Surveyor.objects.filter(is_active=False).count()

        # 部署一覧（フィルター用）
        context['departments'] = Surveyor.objects.values_list('department', flat=True).distinct().exclude(department='')

        return context


class SurveyorDetailView(LoginRequiredMixin, DetailView):
    """調査員詳細"""
    model = Surveyor
    template_name = 'surveys/surveyor/detail.html'
    context_object_name = 'surveyor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 調査履歴
        context['recent_surveys'] = self.object.assigned_surveys.order_by('-scheduled_date')[:10]
        context['current_surveys'] = self.object.assigned_surveys.filter(
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_date')

        # 統計情報
        context['stats'] = {
            'total_surveys': self.object.assigned_surveys.count(),
            'completed_surveys': self.object.get_completed_surveys_count(),
            'current_surveys': self.object.get_current_surveys_count(),
            'experience_level': self.object.get_experience_level(),
        }

        return context


class SurveyorCreateView(LoginRequiredMixin, CreateView):
    """調査員新規登録"""
    model = Surveyor
    template_name = 'surveys/surveyor/form.html'
    fields = [
        'name', 'employee_id', 'email', 'phone', 'department',
        'specialties', 'certifications', 'experience_years',
        'hire_date', 'user', 'notes'
    ]
    success_url = reverse_lazy('surveys:surveyor_list')

    def form_valid(self, form):
        messages.success(self.request, f'調査員「{form.instance.name}」を登録しました。')
        return super().form_valid(form)


class SurveyorUpdateView(LoginRequiredMixin, UpdateView):
    """調査員編集"""
    model = Surveyor
    template_name = 'surveys/surveyor/form.html'
    fields = [
        'name', 'employee_id', 'email', 'phone', 'department',
        'specialties', 'certifications', 'experience_years',
        'hire_date', 'is_active', 'user', 'notes'
    ]
    success_url = reverse_lazy('surveys:surveyor_list')

    def form_valid(self, form):
        messages.success(self.request, f'調査員「{form.instance.name}」を更新しました。')
        return super().form_valid(form)


class SurveyorDeleteView(LoginRequiredMixin, DeleteView):
    """調査員削除"""
    model = Surveyor
    template_name = 'surveys/surveyor/confirm_delete.html'
    success_url = reverse_lazy('surveys:surveyor_list')

    def delete(self, request, *args, **kwargs):
        surveyor = self.get_object()
        messages.success(request, f'調査員「{surveyor.name}」を削除しました。')
        return super().delete(request, *args, **kwargs)


class SurveyorDashboardView(LoginRequiredMixin, DetailView):
    """調査員専用ダッシュボード（自分の情報のみ表示）"""
    model = Surveyor
    template_name = 'surveys/surveyor/dashboard.html'
    context_object_name = 'surveyor'

    def get_object(self):
        """ログインユーザーに関連付けられた調査員プロファイルを取得"""
        try:
            return Surveyor.objects.get(user=self.request.user)
        except Surveyor.DoesNotExist:
            # 調査員プロファイルが存在しない場合の処理
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object is None:
            # 調査員プロファイルがない場合
            context['no_profile'] = True
            return context

        # 自分の調査のみ取得
        context['current_surveys'] = self.object.assigned_surveys.filter(
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_date', 'scheduled_start_time')[:5]

        context['recent_surveys'] = self.object.assigned_surveys.filter(
            status='completed'
        ).order_by('-scheduled_date')[:10]

        context['today_surveys'] = self.object.assigned_surveys.filter(
            scheduled_date=timezone.now().date(),
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_start_time')

        # 簡単な統計
        context['stats'] = {
            'today_count': context['today_surveys'].count(),
            'pending_count': self.object.assigned_surveys.filter(status='scheduled').count(),
            'in_progress_count': self.object.assigned_surveys.filter(status='in_progress').count(),
            'completed_this_month': self.object.assigned_surveys.filter(
                status='completed',
                scheduled_date__year=timezone.now().year,
                scheduled_date__month=timezone.now().month
            ).count(),
        }

        return context


# AJAX Views
def surveyor_search_ajax(request):
    """調査員検索（AJAX）"""
    search = request.GET.get('search', '')
    active_only = request.GET.get('active_only', 'true') == 'true'

    queryset = Surveyor.objects.all()

    if active_only:
        queryset = queryset.filter(is_active=True)

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(department__icontains=search)
        )

    surveyors = []
    for surveyor in queryset[:20]:  # 最大20件
        surveyors.append({
            'id': surveyor.id,
            'name': surveyor.name,
            'employee_id': surveyor.employee_id,
            'department': surveyor.department,
            'experience_level': surveyor.get_experience_level(),
            'current_surveys': surveyor.get_current_surveys_count(),
            'is_active': surveyor.is_active,
            'display_name': surveyor.get_full_display_name(),
        })

    return JsonResponse({
        'surveyors': surveyors,
        'total': queryset.count()
    })


def surveyor_detail_ajax(request, pk):
    """調査員詳細（AJAX）"""
    surveyor = get_object_or_404(Surveyor, pk=pk)

    data = {
        'id': surveyor.id,
        'name': surveyor.name,
        'employee_id': surveyor.employee_id,
        'email': surveyor.email,
        'phone': surveyor.phone,
        'department': surveyor.department,
        'specialties': surveyor.get_specialties_list(),
        'certifications': surveyor.get_certifications_list(),
        'experience_years': surveyor.experience_years,
        'experience_level': surveyor.get_experience_level(),
        'current_surveys': surveyor.get_current_surveys_count(),
        'completed_surveys': surveyor.get_completed_surveys_count(),
        'is_active': surveyor.is_active,
        'status_display': surveyor.get_status_display(),
        'display_name': surveyor.get_full_display_name(),
        'notes': surveyor.notes,
    }

    return JsonResponse(data)