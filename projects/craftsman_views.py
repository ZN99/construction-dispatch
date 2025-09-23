from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import json

from .models import (
    Craftsman,
    Assignment,
    CraftsmanSchedule,
    Project,
    CraftsmanRating,
    Surveyor,
    ProjectType,
)
from .craftsman_forms import (
    CraftsmanSearchForm,
    AssignmentForm,
    AssignmentResponseForm,
    CraftsmanScheduleForm,
    BulkScheduleForm,
    ProjectMatchingForm,
    QuickAssignmentForm,
)
from .craftsman_matching import (
    CraftsmanMatcher,
    search_craftsmen,
    get_craftsman_availability_calendar,
)


def craftsman_dashboard(request):
    """職人選定ダッシュボード"""
    today = timezone.now().date()

    # 統計データ
    stats = {
        "total_craftsmen": Craftsman.objects.filter(is_active=True).count(),
        "pending_assignments": Assignment.objects.filter(status="inquiry").count(),
        "confirmed_today": Assignment.objects.filter(
            status="confirmed", scheduled_start_date=today
        ).count(),
        "busy_craftsmen": Craftsman.objects.filter(
            is_active=True,
            assignment__status__in=["confirmed", "in_progress"],
            assignment__scheduled_start_date__lte=today,
            assignment__scheduled_end_date__gte=today,
        )
        .distinct()
        .count(),
    }

    # 打診中の案件
    pending_assignments = (
        Assignment.objects.filter(status="inquiry")
        .select_related("project", "craftsman", "assigned_by")
        .order_by("-created_at")[:10]
    )

    # 今日開始予定の案件
    today_assignments = Assignment.objects.filter(
        status="confirmed", scheduled_start_date=today
    ).select_related("project", "craftsman")

    # 稼働率の高い職人
    busy_craftsmen = []
    matcher = CraftsmanMatcher()
    for craftsman in Craftsman.objects.filter(is_active=True)[:10]:
        workload = matcher.get_workload_analysis(craftsman, days=7)
        if workload["workload_percentage"] > 70:
            busy_craftsmen.append({"craftsman": craftsman, "workload": workload})

    context = {
        "stats": stats,
        "pending_assignments": pending_assignments,
        "today_assignments": today_assignments,
        "busy_craftsmen": busy_craftsmen,
    }
    return render(request, "craftsman/dashboard.html", context)


def craftsman_search(request):
    """職人検索"""
    form = CraftsmanSearchForm(request.GET or None)
    craftsmen = []
    search_performed = False

    if form.is_valid() and any(form.cleaned_data.values()):
        search_performed = True
        filters = {k: v for k, v in form.cleaned_data.items() if v}
        craftsmen = search_craftsmen(filters)

        # 稼働率情報を追加
        matcher = CraftsmanMatcher()
        craftsmen_with_workload = []
        for craftsman in craftsmen:
            workload = matcher.get_workload_analysis(craftsman)
            craftsmen_with_workload.append(
                {"craftsman": craftsman, "workload": workload}
            )
        craftsmen = craftsmen_with_workload

    context = {
        "form": form,
        "craftsmen": craftsmen,
        "search_performed": search_performed,
    }
    return render(request, "craftsman/search.html", context)


def project_matching(request):
    """プロジェクト職人マッチング"""
    form = ProjectMatchingForm(request.GET or None)
    matches = []
    project = None

    if form.is_valid():
        project = form.cleaned_data["project"]
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        max_results = form.cleaned_data["max_results"]

        matcher = CraftsmanMatcher()
        matches = matcher.find_best_matches(project, start_date, end_date, max_results)

    context = {
        "form": form,
        "matches": matches,
        "project": project,
    }
    return render(request, "craftsman/project_matching.html", context)


def assignment_create(request, craftsman_id=None, project_id=None):
    """案件アサイン作成"""
    craftsman = get_object_or_404(Craftsman, id=craftsman_id) if craftsman_id else None
    project = get_object_or_404(Project, id=project_id) if project_id else None

    if request.method == "POST":
        form = AssignmentForm(request.POST, craftsman=craftsman, project=project)
        if form.is_valid():
            assignment = form.save(commit=False)
            # assigned_byを設定（仮でSurveyorの最初のレコードを使用）
            assignment.assigned_by = Surveyor.objects.first()
            assignment.save()

            messages.success(
                request,
                f"{assignment.craftsman.name}さんに案件「{assignment.project.title}」を打診しました",
            )
            return redirect("assignment_detail", assignment.id)
    else:
        form = AssignmentForm(craftsman=craftsman, project=project)

    context = {
        "form": form,
        "craftsman": craftsman,
        "project": project,
    }
    return render(request, "craftsman/assignment_create.html", context)


def assignment_detail(request, assignment_id):
    """案件アサイン詳細"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    context = {
        "assignment": assignment,
    }
    return render(request, "craftsman/assignment_detail.html", context)


def assignment_response(request, assignment_id):
    """案件返答処理"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.method == "POST":
        form = AssignmentResponseForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.response_date = timezone.now()
            assignment.save()

            status_text = assignment.get_status_display()
            messages.success(
                request, f"案件「{assignment.project.title}」への返答を{status_text}として記録しました"
            )
            return redirect("assignment_detail", assignment.id)
    else:
        form = AssignmentResponseForm(instance=assignment)

    context = {
        "form": form,
        "assignment": assignment,
    }
    return render(request, "craftsman/assignment_response.html", context)


def craftsman_schedule_calendar(request, craftsman_id=None):
    """職人スケジュールカレンダー"""
    craftsman = get_object_or_404(Craftsman, id=craftsman_id) if craftsman_id else None

    # 表示期間
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=30)

    calendar_data = []
    if craftsman:
        calendar_data = get_craftsman_availability_calendar(
            craftsman, start_date, end_date
        )

    # 全職人リスト
    craftsmen = Craftsman.objects.filter(is_active=True).order_by("name")

    context = {
        "craftsman": craftsman,
        "craftsmen": craftsmen,
        "calendar_data": calendar_data,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "craftsman/schedule_calendar.html", context)


@csrf_exempt
def quick_assignment(request):
    """クイックアサイン（Ajax）"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body)
        craftsman = get_object_or_404(Craftsman, id=data["craftsman_id"])
        project = get_object_or_404(Project, id=data["project_id"])

        # 簡易アサイン作成
        assignment = Assignment.objects.create(
            project=project,
            craftsman=craftsman,
            assigned_by=Surveyor.objects.first(),  # 仮の担当者
            scheduled_start_date=data["start_date"],
            scheduled_end_date=data["end_date"],
            estimated_hours=data.get("estimated_hours", 8),
            offered_rate=craftsman.hourly_rate,
            contact_method=data.get("contact_method", "phone"),
            inquiry_message=f"案件「{project.title}」についてご相談があります。",
        )

        return JsonResponse(
            {
                "success": True,
                "assignment_id": assignment.id,
                "message": f"{craftsman.name}さんに打診しました",
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def craftsman_workload_api(request, craftsman_id):
    """職人稼働率API"""
    craftsman = get_object_or_404(Craftsman, id=craftsman_id)
    days = int(request.GET.get("days", 30))

    matcher = CraftsmanMatcher()
    workload = matcher.get_workload_analysis(craftsman, days)

    return JsonResponse(workload)


def schedule_bulk_update(request):
    """スケジュール一括更新"""
    if request.method == "POST":
        form = BulkScheduleForm(request.POST)
        if form.is_valid():
            craftsman = form.cleaned_data["craftsman"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            is_available = form.cleaned_data["is_available"]
            exclude_weekends = form.cleaned_data["exclude_weekends"]
            notes = form.cleaned_data["notes"]

            created_count = 0
            current_date = start_date

            with transaction.atomic():
                while current_date <= end_date:
                    # 土日除外オプション
                    if exclude_weekends and current_date.weekday() >= 5:
                        current_date += timedelta(days=1)
                        continue

                    schedule, created = CraftsmanSchedule.objects.get_or_create(
                        craftsman=craftsman,
                        date=current_date,
                        defaults={"is_available": is_available, "notes": notes},
                    )

                    if not created:
                        schedule.is_available = is_available
                        if notes:
                            schedule.notes = notes
                        schedule.save()

                    created_count += 1
                    current_date += timedelta(days=1)

            messages.success(
                request, f"{craftsman.name}さんのスケジュールを{created_count}日分更新しました"
            )
            return redirect("craftsman_schedule_calendar", craftsman_id=craftsman.id)
    else:
        form = BulkScheduleForm()

    context = {
        "form": form,
    }
    return render(request, "craftsman/schedule_bulk_update.html", context)


class AssignmentListView(ListView):
    """案件アサイン一覧"""

    model = Assignment
    template_name = "craftsman/assignment_list.html"
    context_object_name = "assignments"
    paginate_by = 20

    def get_queryset(self):
        queryset = Assignment.objects.select_related(
            "project", "craftsman", "assigned_by"
        ).order_by("-created_at")

        # フィルタリング
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        craftsman_id = self.request.GET.get("craftsman")
        if craftsman_id:
            queryset = queryset.filter(craftsman_id=craftsman_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["craftsmen"] = Craftsman.objects.filter(is_active=True).order_by("name")
        context["status_choices"] = Assignment.STATUS_CHOICES
        context["current_status"] = self.request.GET.get("status", "")
        context["current_craftsman"] = self.request.GET.get("craftsman", "")
        return context


class CraftsmanDetailView(DetailView):
    """職人詳細"""

    model = Craftsman
    template_name = "craftsman/craftsman_detail.html"
    context_object_name = "craftsman"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        craftsman = self.object

        # 稼働率分析
        matcher = CraftsmanMatcher()
        context["workload"] = matcher.get_workload_analysis(craftsman)

        # 最近のアサイン履歴
        context["recent_assignments"] = (
            Assignment.objects.filter(craftsman=craftsman)
            .select_related("project")
            .order_by("-created_at")[:10]
        )

        # 評価履歴
        context["ratings"] = (
            CraftsmanRating.objects.filter(craftsman=craftsman)
            .select_related("assignment", "surveyor")
            .order_by("-created_at")[:5]
        )

        # 今後のスケジュール
        today = timezone.now().date()
        context["upcoming_schedule"] = get_craftsman_availability_calendar(
            craftsman, today, today + timedelta(days=14)
        )

        return context


def contact_craftsman(request, assignment_id, method):
    """職人連絡機能"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    craftsman = assignment.craftsman

    if method == "phone":
        # 電話リンク
        phone_url = f"tel:{craftsman.phone}"
        return redirect(phone_url)

    elif method == "line":
        if craftsman.line_id:
            # LINE連携（実装時はLINE API使用）
            line_url = f"https://line.me/ti/p/{craftsman.line_id}"
            return redirect(line_url)
        else:
            messages.warning(request, f"{craftsman.name}さんのLINE IDが設定されていません")

    elif method == "email":
        if craftsman.email:
            # メール作成
            import urllib.parse

            subject = f"案件「{assignment.project.title}」について"
            body = assignment.inquiry_message
            mailto_url = f"mailto:{craftsman.email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            return redirect(mailto_url)
        else:
            messages.warning(request, f"{craftsman.name}さんのメールアドレスが設定されていません")

    return redirect("assignment_detail", assignment.id)
