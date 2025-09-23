from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Avg, Count, Max, Min
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import date, timedelta

from .models import (
    Project,
    ConstructionProgress,
    ProgressPhoto,
    ProjectIssue,
    ProjectCompletion,
    Craftsman,
    Assignment,
    ProjectEditSession,
)
from .construction_forms import (
    ConstructionProgressForm,
    ProgressPhotoForm,
    ProjectIssueForm,
    IssueUpdateForm,
    ProjectCompletionForm,
    ProgressSearchForm,
    QuickProgressForm,
)


def construction_dashboard(request):
    """施工管理ダッシュボード"""
    # 進行中プロジェクトの統計
    active_projects = Project.objects.filter(status__in=["in_progress", "confirmed"])

    # 進捗統計
    progress_stats = {}
    if active_projects.exists():
        # 最新の進捗率を取得
        latest_progress = (
            ConstructionProgress.objects.filter(project__in=active_projects)
            .values("project")
            .annotate(latest_rate=Max("progress_rate"), latest_date=Max("report_date"))
        )

        progress_stats = {
            "total_projects": active_projects.count(),
            "avg_progress": sum(p["latest_rate"] for p in latest_progress)
            / len(latest_progress)
            if latest_progress
            else 0,
            "delayed_projects": 0,
            "completed_this_week": 0,
        }

        # 遅れプロジェクト数
        for project in active_projects:
            latest = project.construction_progress.first()
            if latest and latest.is_delayed:
                progress_stats["delayed_projects"] += 1

        # 今週完了プロジェクト数
        week_ago = timezone.now() - timedelta(days=7)
        progress_stats["completed_this_week"] = ProjectCompletion.objects.filter(
            completion_date__gte=week_ago.date(), status="completed"
        ).count()

    # 進捗率別プロジェクト分布
    progress_distribution = []
    for project in active_projects:
        latest = project.construction_progress.first()
        if latest:
            progress_distribution.append(
                {
                    "project": project,
                    "progress_rate": latest.progress_rate,
                    "is_delayed": latest.is_delayed,
                    "latest_report": latest.report_date,
                    "has_issues": latest.has_issues,
                }
            )

    progress_distribution.sort(key=lambda x: x["progress_rate"])

    # 未解決問題
    open_issues = (
        ProjectIssue.objects.filter(status__in=["open", "in_progress"])
        .select_related("project")
        .order_by("-priority", "-created_at")[:10]
    )

    # 最近の進捗報告
    recent_progress = ConstructionProgress.objects.select_related(
        "project", "craftsman"
    ).order_by("-report_date")[:10]

    # 完了間近のプロジェクト
    near_completion = []
    for project in active_projects:
        latest = project.construction_progress.first()
        if latest and latest.progress_rate >= 80:
            near_completion.append(
                {
                    "project": project,
                    "progress_rate": latest.progress_rate,
                    "completion": getattr(project, "completion", None),
                }
            )

    context = {
        "progress_stats": progress_stats,
        "progress_distribution": progress_distribution,
        "open_issues": open_issues,
        "recent_progress": recent_progress,
        "near_completion": near_completion,
    }
    return render(request, "construction/dashboard.html", context)


def project_progress_detail(request, project_id):
    """案件別進捗詳細"""
    project = get_object_or_404(Project, id=project_id)

    # 進捗履歴
    progress_history = project.construction_progress.select_related("craftsman")

    # 最新進捗
    latest_progress = progress_history.first()

    # 進捗写真
    progress_photos = ProgressPhoto.objects.filter(progress__project=project).order_by(
        "-taken_at"
    )

    # 問題・課題
    project_issues = project.issues.order_by("-created_at")

    # 完了情報
    try:
        completion = project.completion
    except ProjectCompletion.DoesNotExist:
        completion = None

    # 担当職人
    assigned_craftsmen = Assignment.objects.filter(
        project=project, status__in=["confirmed", "in_progress"]
    ).select_related("craftsman")

    context = {
        "project": project,
        "latest_progress": latest_progress,
        "progress_history": progress_history,
        "progress_photos": progress_photos,
        "project_issues": project_issues,
        "completion": completion,
        "assigned_craftsmen": assigned_craftsmen,
    }
    return render(request, "construction/project_detail.html", context)


def progress_report_create(request, project_id):
    """進捗報告作成"""
    project = get_object_or_404(Project, id=project_id)

    # 担当職人を取得
    assigned_craftsmen = Assignment.objects.filter(
        project=project, status__in=["confirmed", "in_progress"]
    ).select_related("craftsman")

    if request.method == "POST":
        craftsman_id = request.POST.get("craftsman")
        craftsman = (
            get_object_or_404(Craftsman, id=craftsman_id) if craftsman_id else None
        )

        form = ConstructionProgressForm(
            request.POST, project=project, craftsman=craftsman
        )

        if form.is_valid():
            progress = form.save()

            # 追加項目を処理
            additional_items = {}
            keys = request.POST.getlist('additional_item_keys[]')
            values = request.POST.getlist('additional_item_values[]')

            for key, value in zip(keys, values):
                if key.strip() and value.strip():
                    additional_items[key.strip()] = value.strip()

            if additional_items:
                progress.additional_items = additional_items
                progress.save()

            # 写真アップロード処理
            photos = request.FILES.getlist("photos")
            photo_descriptions = request.POST.getlist("photo_descriptions")
            photo_types = request.POST.getlist("photo_types")

            for i, photo in enumerate(photos):
                ProgressPhoto.objects.create(
                    progress=progress,
                    photo=photo,
                    description=photo_descriptions[i]
                    if i < len(photo_descriptions)
                    else "",
                    photo_type=photo_types[i] if i < len(photo_types) else "during",
                )

            # メッセージを作成
            message = f"案件「{project.title}」の進捗報告を作成しました。"
            if additional_items:
                item_count = len(additional_items)
                message += f" 追加項目{item_count}件を含む。"

            messages.success(request, message)
            return redirect("project_progress_detail", project_id=project.id)

    else:
        form = ConstructionProgressForm(project=project)

    context = {
        "project": project,
        "form": form,
        "assigned_craftsmen": assigned_craftsmen,
    }
    return render(request, "construction/progress_create.html", context)


def quick_progress_update(request, project_id):
    """クイック進捗更新（AJAX）"""
    if request.method == "POST":
        project = get_object_or_404(Project, id=project_id)

        # デバッグ: リクエストデータをログ出力
        print(f"DEBUG: quick_progress_update - プロジェクト: {project.title}")
        print(f"DEBUG: POST データ: {dict(request.POST)}")


        # 担当職人を取得
        craftsman_id = request.POST.get("craftsman")
        if craftsman_id:
            craftsman = get_object_or_404(Craftsman, id=craftsman_id)
        else:
            # 最初の担当職人を取得
            assignment = Assignment.objects.filter(
                project=project, status__in=["confirmed", "in_progress"]
            ).first()
            if assignment:
                craftsman = assignment.craftsman
            else:
                # アサインされた職人がいない場合は、最初の利用可能な職人を使用
                craftsman = Craftsman.objects.filter(is_active=True).first()
                if not craftsman:
                    return JsonResponse({"success": False, "error": "利用可能な職人が見つかりません。職人を登録してください。"})

        form = QuickProgressForm(
            request.POST, project=project, craftsman=craftsman
        )

        if form.is_valid():
            progress = form.save()

            # 追加項目を処理（クイック更新でも対応）
            additional_items = {}

            # フォームから送信された追加項目
            keys = request.POST.getlist('additional_item_keys[]')
            values = request.POST.getlist('additional_item_values[]')
            print(f"DEBUG: フォームから受信した追加項目キー: {keys}")
            print(f"DEBUG: フォームから受信した追加項目値: {values}")

            for key, value in zip(keys, values):
                if key.strip() and value.strip():
                    additional_items[key.strip()] = value.strip()
                    print(f"DEBUG: 追加項目登録: {key.strip()} = {value.strip()}")

            # 編集セッションから追加項目を取得・統合
            session_id = request.POST.get('session_id')
            print(f"DEBUG: セッションID: {session_id}")
            if session_id:
                try:
                    edit_session = ProjectEditSession.objects.get(
                        project=project,
                        session_id=session_id
                    )
                    print(f"DEBUG: 編集セッション見つかりました: {edit_session.additional_items}")
                    if edit_session.additional_items:
                        # 編集セッションの項目を統合（フォームの項目が優先）
                        for key, value in edit_session.additional_items.items():
                            if key.strip() and value.strip() and key not in additional_items:
                                additional_items[key.strip()] = value.strip()
                                print(f"DEBUG: セッションから追加項目統合: {key.strip()} = {value.strip()}")
                except ProjectEditSession.DoesNotExist:
                    print("DEBUG: 編集セッションが見つかりません")

            print(f"DEBUG: 最終的な追加項目: {additional_items}")
            if additional_items:
                progress.additional_items = additional_items
                progress.save()
                print(f"DEBUG: 追加項目を進捗に保存しました: {progress.id}")

            # 進捗更新成功後、編集セッションをクリア
            if session_id:
                try:
                    edit_session = ProjectEditSession.objects.get(
                        project=project,
                        session_id=session_id
                    )
                    edit_session.delete()
                except ProjectEditSession.DoesNotExist:
                    pass

            return JsonResponse(
                {
                    "success": True,
                    "progress_id": progress.id,
                    "progress_rate": progress.progress_rate,
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request method"})


def issue_create(request, project_id):
    """問題報告作成"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = ProjectIssueForm(request.POST, project=project, user=request.user)

        if form.is_valid():
            issue = form.save()
            messages.success(request, f"問題「{issue.title}」を報告しました。")
            return redirect("project_progress_detail", project_id=project.id)

    else:
        form = ProjectIssueForm(project=project, user=request.user)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "construction/issue_create.html", context)


def issue_update(request, issue_id):
    """問題更新"""
    issue = get_object_or_404(ProjectIssue, id=issue_id)

    if request.method == "POST":
        form = IssueUpdateForm(request.POST, instance=issue)

        if form.is_valid():
            updated_issue = form.save()
            messages.success(request, f"問題「{updated_issue.title}」を更新しました。")
            return redirect("project_progress_detail", project_id=issue.project.id)

    else:
        form = IssueUpdateForm(instance=issue)

    context = {
        "issue": issue,
        "form": form,
    }
    return render(request, "construction/issue_update.html", context)


def issues_list(request):
    """問題一覧"""
    issues = ProjectIssue.objects.select_related(
        "project", "reported_by", "assigned_to"
    )

    # フィルタリング
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    project_filter = request.GET.get("project")

    if status_filter:
        issues = issues.filter(status=status_filter)

    if priority_filter:
        issues = issues.filter(priority=priority_filter)

    if project_filter:
        issues = issues.filter(project_id=project_filter)

    issues = issues.order_by("-created_at")

    # ページネーション
    paginator = Paginator(issues, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # フィルター用データ
    projects = Project.objects.filter(status__in=["in_progress", "confirmed"]).order_by(
        "title"
    )

    context = {
        "page_obj": page_obj,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
        "project_filter": project_filter,
        "projects": projects,
        "status_choices": ProjectIssue.STATUS_CHOICES,
        "priority_choices": ProjectIssue.PRIORITY_CHOICES,
    }
    return render(request, "construction/issues_list.html", context)


def completion_manage(request, project_id):
    """完了管理"""
    project = get_object_or_404(Project, id=project_id)

    try:
        completion = project.completion
    except ProjectCompletion.DoesNotExist:
        completion = None

    if request.method == "POST":
        form = ProjectCompletionForm(request.POST, instance=completion, project=project)

        if form.is_valid():
            completion = form.save()
            messages.success(request, f"案件「{project.title}」の完了情報を更新しました。")
            return redirect("project_progress_detail", project_id=project.id)

    else:
        form = ProjectCompletionForm(instance=completion, project=project)

    # 完了に必要な写真チェック
    final_photos = ProgressPhoto.objects.filter(
        progress__project=project, photo_type="after"
    ).count()

    context = {
        "project": project,
        "form": form,
        "completion": completion,
        "final_photos_count": final_photos,
    }
    return render(request, "construction/completion_manage.html", context)


def progress_search(request):
    """進捗検索"""
    form = ProgressSearchForm(request.GET)
    progress_list = ConstructionProgress.objects.select_related(
        "project", "craftsman"
    ).order_by("-report_date")

    if form.is_valid():
        data = form.cleaned_data

        if data["project"]:
            progress_list = progress_list.filter(project=data["project"])

        if data["craftsman"]:
            progress_list = progress_list.filter(craftsman=data["craftsman"])

        if data["progress_rate_min"]:
            progress_list = progress_list.filter(
                progress_rate__gte=data["progress_rate_min"]
            )

        if data["progress_rate_max"]:
            progress_list = progress_list.filter(
                progress_rate__lte=data["progress_rate_max"]
            )

        if data["date_from"]:
            progress_list = progress_list.filter(
                report_date__date__gte=data["date_from"]
            )

        if data["date_to"]:
            progress_list = progress_list.filter(report_date__date__lte=data["date_to"])

        if data["has_issues"]:
            progress_list = progress_list.exclude(issues="")

    # ページネーション
    paginator = Paginator(progress_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "form": form,
        "page_obj": page_obj,
    }
    return render(request, "construction/progress_search.html", context)


def progress_analytics(request):
    """進捗分析"""
    # 月別進捗分析
    monthly_stats = (
        ConstructionProgress.objects.extra(
            select={"month": "DATE_FORMAT(report_date, '%%Y-%%m')"}
        )
        .values("month")
        .annotate(
            avg_progress=Avg("progress_rate"),
            report_count=Count("id"),
            issue_count=Count("id", filter=Q(issues__isnull=False, issues__gt="")),
        )
        .order_by("month")
    )

    # 職人別パフォーマンス
    craftsman_stats = (
        ConstructionProgress.objects.values("craftsman__name")
        .annotate(
            avg_progress=Avg("progress_rate"),
            report_count=Count("id"),
            avg_working_hours=Avg("working_hours"),
        )
        .order_by("-avg_progress")
    )

    # 問題種別統計
    issue_stats = (
        ProjectIssue.objects.values("issue_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    context = {
        "monthly_stats": monthly_stats,
        "craftsman_stats": craftsman_stats,
        "issue_stats": issue_stats,
    }
    return render(request, "construction/analytics.html", context)


def photo_gallery(request, project_id):
    """案件別写真ギャラリー"""
    project = get_object_or_404(Project, id=project_id)

    photos = (
        ProgressPhoto.objects.filter(progress__project=project)
        .select_related("progress")
        .order_by("-taken_at")
    )

    # 写真種別でフィルタリング
    photo_type = request.GET.get("type")
    if photo_type:
        photos = photos.filter(photo_type=photo_type)

    context = {
        "project": project,
        "photos": photos,
        "photo_type": photo_type,
        "photo_types": ProgressPhoto.PHOTO_TYPE_CHOICES,
    }
    return render(request, "construction/photo_gallery.html", context)


def edit_session_save(request, project_id):
    """編集セッションの保存（AJAX）"""
    if request.method == "POST":
        project = get_object_or_404(Project, id=project_id)

        # セッションIDを取得または生成
        session_id = request.POST.get("session_id")
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())

        # 編集セッションを取得または作成
        edit_session, created = ProjectEditSession.objects.get_or_create(
            project=project,
            session_id=session_id,
            defaults={
                "user_id": str(request.user.id) if request.user.is_authenticated else None,
                "edit_mode": request.POST.get("edit_mode", "false").lower() == "true",
                "additional_items": {}
            }
        )

        # 編集モード状態を更新
        edit_mode = request.POST.get("edit_mode", "false").lower() == "true"
        edit_session.edit_mode = edit_mode

        # 追加項目を処理
        action = request.POST.get("action")

        if action == "save_item":
            key = request.POST.get("key", "").strip()
            value = request.POST.get("value", "").strip()
            if key and value:
                edit_session.save_additional_item(key, value)
                return JsonResponse({
                    "success": True,
                    "message": "追加項目を保存しました",
                    "session_id": session_id,
                    "additional_items": edit_session.get_additional_items_list()
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "キーと値は必須です"
                })

        elif action == "remove_item":
            key = request.POST.get("key", "").strip()
            if key:
                edit_session.remove_additional_item(key)
                return JsonResponse({
                    "success": True,
                    "message": "追加項目を削除しました",
                    "session_id": session_id,
                    "additional_items": edit_session.get_additional_items_list()
                })

        elif action == "update_mode":
            edit_session.save()
            return JsonResponse({
                "success": True,
                "message": f"編集モード: {edit_session.edit_mode}",
                "session_id": session_id,
                "edit_mode": edit_session.edit_mode,
                "additional_items": edit_session.get_additional_items_list()
            })

        # 全体状態を保存
        edit_session.save()
        return JsonResponse({
            "success": True,
            "session_id": session_id,
            "edit_mode": edit_session.edit_mode,
            "additional_items": edit_session.get_additional_items_list()
        })

    return JsonResponse({"success": False, "error": "Invalid request method"})


def edit_session_load(request, project_id):
    """編集セッションの読み込み（AJAX）"""
    if request.method == "GET":
        project = get_object_or_404(Project, id=project_id)
        session_id = request.GET.get("session_id")

        if session_id:
            try:
                edit_session = ProjectEditSession.objects.get(
                    project=project,
                    session_id=session_id
                )

                if edit_session.is_expired:
                    edit_session.delete()
                    return JsonResponse({
                        "success": False,
                        "error": "セッションが期限切れです"
                    })

                return JsonResponse({
                    "success": True,
                    "session_id": session_id,
                    "edit_mode": edit_session.edit_mode,
                    "additional_items": edit_session.get_additional_items_list()
                })

            except ProjectEditSession.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "error": "セッションが見つかりません"
                })

        # アクティブなセッションを検索
        active_sessions = ProjectEditSession.objects.filter(
            project=project,
            edit_mode=True
        ).order_by("-last_activity")

        if active_sessions.exists():
            session = active_sessions.first()
            if not session.is_expired:
                return JsonResponse({
                    "success": True,
                    "session_id": session.session_id,
                    "edit_mode": session.edit_mode,
                    "additional_items": session.get_additional_items_list()
                })

        return JsonResponse({
            "success": True,
            "session_id": None,
            "edit_mode": False,
            "additional_items": []
        })

    return JsonResponse({"success": False, "error": "Invalid request method"})
