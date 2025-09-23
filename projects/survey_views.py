from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Survey, Surveyor, Project, SurveyRoute
from .forms import SurveyForm, SurveyAssignForm, SurveyCompletionForm
import json


class SurveyListView(ListView):
    model = Survey
    template_name = "projects/survey_list.html"
    context_object_name = "surveys"
    paginate_by = 20

    def get_queryset(self):
        queryset = Survey.objects.select_related(
            "project", "surveyor", "project__customer"
        )

        # フィルタリング
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        surveyor = self.request.GET.get("surveyor")
        if surveyor:
            queryset = queryset.filter(surveyor_id=surveyor)

        date_filter = self.request.GET.get("date")
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                queryset = queryset.filter(scheduled_date__date=filter_date)
            except ValueError:
                pass

        return queryset.order_by("scheduled_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["surveyors"] = Surveyor.objects.filter(is_active=True)
        context["status_choices"] = Survey.STATUS_CHOICES
        return context


class SurveyDetailView(DetailView):
    model = Survey
    template_name = "projects/survey_detail.html"
    context_object_name = "survey"


def survey_calendar(request):
    """調査員別カレンダービュー"""
    # 日付範囲の設定
    today = timezone.now().date()
    start_date = today - timedelta(days=7)
    end_date = today + timedelta(days=30)

    # 調査データの取得
    surveys = Survey.objects.filter(
        scheduled_date__date__range=[start_date, end_date]
    ).select_related("project", "surveyor", "project__customer")

    surveyors = Surveyor.objects.filter(is_active=True)

    # カレンダー用データの構築
    calendar_data = {}
    for surveyor in surveyors:
        calendar_data[surveyor.id] = {"name": surveyor.name, "surveys": []}

    for survey in surveys:
        if survey.surveyor and survey.surveyor.id in calendar_data:
            calendar_data[survey.surveyor.id]["surveys"].append(
                {
                    "id": survey.id,
                    "title": survey.project.title,
                    "customer": survey.project.customer.name,
                    "start": survey.scheduled_date.isoformat(),
                    "duration": survey.estimated_duration,
                    "status": survey.status,
                    "priority": survey.priority,
                    "address": survey.project.address[:50] + "..."
                    if len(survey.project.address) > 50
                    else survey.project.address,
                }
            )

    context = {
        "calendar_data": calendar_data,
        "surveyors": surveyors,
        "today": today.isoformat(),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    return render(request, "projects/survey_calendar.html", context)


def survey_assign(request, project_id):
    """案件に調査をアサイン"""
    project = get_object_or_404(Project, id=project_id)

    # 既に調査が存在するかチェック
    survey, created = Survey.objects.get_or_create(
        project=project, defaults={"status": "scheduled"}
    )

    if request.method == "POST":
        form = SurveyAssignForm(request.POST, instance=survey)
        if form.is_valid():
            survey = form.save()
            messages.success(request, f"調査を{survey.surveyor.name}にアサインしました。")
            return redirect("survey_detail", pk=survey.pk)
    else:
        form = SurveyAssignForm(instance=survey)

    # 調査員の推奨順序を計算
    recommended_surveyors = get_recommended_surveyors(project, survey.scheduled_date)

    context = {
        "form": form,
        "project": project,
        "survey": survey,
        "recommended_surveyors": recommended_surveyors,
    }

    return render(request, "projects/survey_assign.html", context)


def get_recommended_surveyors(project, scheduled_date=None):
    """調査員の推奨順序を計算"""
    if not scheduled_date:
        scheduled_date = timezone.now().date()

    surveyors = Surveyor.objects.filter(is_active=True)
    recommended = []

    for surveyor in surveyors:
        score = 0
        reasons = []

        # その日の調査件数をチェック
        daily_count = Survey.objects.filter(
            surveyor=surveyor, scheduled_date__date=scheduled_date
        ).count()

        if daily_count < surveyor.daily_capacity:
            score += 10
            reasons.append(f"空き時間あり ({daily_count}/{surveyor.daily_capacity}件)")
        else:
            score -= 20
            reasons.append(f"満員 ({daily_count}/{surveyor.daily_capacity}件)")

        # 地域の近さ（簡易版）
        if surveyor.base_location and project.address:
            if surveyor.base_location in project.address:
                score += 15
                reasons.append("地域が近い")

        recommended.append(
            {
                "surveyor": surveyor,
                "score": score,
                "reasons": reasons,
                "daily_count": daily_count,
            }
        )

    # スコア順でソート
    recommended.sort(key=lambda x: x["score"], reverse=True)
    return recommended


def survey_complete(request, survey_id):
    """調査完了処理"""
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == "POST":
        # シンプルな完了処理
        survey.status = "completed"
        survey.is_survey_completed = True
        survey.actual_end_time = timezone.now()
        if not survey.actual_start_time:
            survey.actual_start_time = survey.actual_end_time - timedelta(
                minutes=survey.estimated_duration
            )
        survey.save()

        messages.success(request, "調査を完了しました。")
        return redirect("survey_detail", pk=survey.pk)

    return render(request, "projects/survey_complete.html", {"survey": survey})


def survey_reschedule(request, survey_id):
    """調査の再スケジューリング"""
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == "POST":
        form = SurveyAssignForm(request.POST, instance=survey)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.status = "rescheduled"
            survey.save()

            messages.success(request, "調査を再スケジュールしました。")
            return redirect("survey_detail", pk=survey.pk)
    else:
        form = SurveyAssignForm(instance=survey)

    # 推奨調査員を再計算
    recommended_surveyors = get_recommended_surveyors(
        survey.project, survey.scheduled_date
    )

    context = {
        "form": form,
        "survey": survey,
        "recommended_surveyors": recommended_surveyors,
    }

    return render(request, "projects/survey_reschedule.html", context)


def survey_route_optimization(request):
    """調査ルート最適化"""
    date_str = request.GET.get("date", timezone.now().date().isoformat())
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        target_date = timezone.now().date()

    surveyor_id = request.GET.get("surveyor")
    if surveyor_id:
        surveyor = get_object_or_404(Surveyor, id=surveyor_id)
        surveys = Survey.objects.filter(
            surveyor=surveyor,
            scheduled_date__date=target_date,
            status__in=["scheduled", "in_progress"],
        ).select_related("project")

        # 簡易的なルート最適化（実際にはより高度なアルゴリズムを使用）
        optimized_surveys = optimize_route(list(surveys))

        context = {
            "surveyor": surveyor,
            "date": target_date,
            "surveys": optimized_surveys,
            "total_surveys": len(optimized_surveys),
        }

        return render(request, "projects/survey_route_detail.html", context)

    # 全調査員の概要
    surveyors = Surveyor.objects.filter(is_active=True)
    route_data = []

    for surveyor in surveyors:
        daily_surveys = Survey.objects.filter(
            surveyor=surveyor, scheduled_date__date=target_date
        ).count()

        route_data.append(
            {
                "surveyor": surveyor,
                "daily_surveys": daily_surveys,
                "capacity_usage": f"{daily_surveys}/{surveyor.daily_capacity}",
            }
        )

    context = {
        "date": target_date,
        "route_data": route_data,
        "surveyors": surveyors,
    }

    return render(request, "projects/survey_routes.html", context)


def optimize_route(surveys):
    """簡易的なルート最適化"""
    if not surveys:
        return []

    # 実際にはより高度なアルゴリズム（TSP、遺伝的アルゴリズムなど）を使用
    # ここでは住所の文字列ソートによる簡易実装
    return sorted(surveys, key=lambda s: s.project.address)


def auto_assign_surveys(request):
    """未アサインの調査を自動アサイン"""
    unassigned_surveys = Survey.objects.filter(
        surveyor__isnull=True, status="scheduled"
    ).select_related("project")

    assigned_count = 0
    for survey in unassigned_surveys:
        recommended = get_recommended_surveyors(survey.project, survey.scheduled_date)
        if recommended and recommended[0]["score"] > 0:
            best_surveyor = recommended[0]["surveyor"]
            survey.surveyor = best_surveyor
            survey.save()
            assigned_count += 1

    messages.success(request, f"{assigned_count}件の調査を自動アサインしました。")
    return redirect("survey_list")


def survey_dashboard(request):
    """調査ダッシュボード"""
    today = timezone.now().date()

    # 統計データ
    stats = {
        "today_surveys": Survey.objects.filter(scheduled_date__date=today).count(),
        "pending_surveys": Survey.objects.filter(
            status="scheduled", surveyor__isnull=True
        ).count(),
        "completed_today": Survey.objects.filter(
            scheduled_date__date=today, status="completed"
        ).count(),
        "overdue_surveys": Survey.objects.filter(
            scheduled_date__lt=timezone.now(), status="scheduled"
        ).count(),
    }

    # 調査員別の稼働状況
    surveyor_stats = []
    for surveyor in Surveyor.objects.filter(is_active=True):
        daily_count = Survey.objects.filter(
            surveyor=surveyor, scheduled_date__date=today
        ).count()

        surveyor_stats.append(
            {
                "surveyor": surveyor,
                "daily_count": daily_count,
                "capacity": surveyor.daily_capacity,
                "usage_rate": round((daily_count / surveyor.daily_capacity) * 100)
                if surveyor.daily_capacity > 0
                else 0,
            }
        )

    # 今週の調査予定
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_surveys = (
        Survey.objects.filter(scheduled_date__date__range=[week_start, week_end])
        .select_related("project", "surveyor", "project__customer")
        .order_by("scheduled_date")
    )

    context = {
        "stats": stats,
        "surveyor_stats": surveyor_stats,
        "weekly_surveys": weekly_surveys,
        "today": today,
    }

    return render(request, "projects/survey_dashboard.html", context)
