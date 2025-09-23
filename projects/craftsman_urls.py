from django.urls import path
from . import craftsman_views

craftsman_urlpatterns = [
    # ダッシュボード
    path("craftsman/", craftsman_views.craftsman_dashboard, name="craftsman_dashboard"),
    # 職人検索
    path(
        "craftsman/search/", craftsman_views.craftsman_search, name="craftsman_search"
    ),
    # プロジェクトマッチング
    path(
        "craftsman/matching/", craftsman_views.project_matching, name="project_matching"
    ),
    # 職人詳細
    path(
        "craftsman/<int:pk>/",
        craftsman_views.CraftsmanDetailView.as_view(),
        name="craftsman_detail",
    ),
    # アサイン管理
    path(
        "assignments/",
        craftsman_views.AssignmentListView.as_view(),
        name="assignment_list",
    ),
    path(
        "assignments/<int:assignment_id>/",
        craftsman_views.assignment_detail,
        name="assignment_detail",
    ),
    path(
        "assignments/create/",
        craftsman_views.assignment_create,
        name="assignment_create",
    ),
    path(
        "assignments/create/craftsman/<int:craftsman_id>/",
        craftsman_views.assignment_create,
        name="assignment_create_craftsman",
    ),
    path(
        "assignments/create/project/<int:project_id>/",
        craftsman_views.assignment_create,
        name="assignment_create_project",
    ),
    path(
        "assignments/<int:assignment_id>/response/",
        craftsman_views.assignment_response,
        name="assignment_response",
    ),
    # クイックアサイン
    path(
        "api/assignments/quick/",
        craftsman_views.quick_assignment,
        name="quick_assignment",
    ),
    # スケジュール管理
    path(
        "craftsman/schedule/",
        craftsman_views.craftsman_schedule_calendar,
        name="craftsman_schedule_calendar",
    ),
    path(
        "craftsman/<int:craftsman_id>/schedule/",
        craftsman_views.craftsman_schedule_calendar,
        name="craftsman_schedule_calendar",
    ),
    path(
        "craftsman/schedule/bulk-update/",
        craftsman_views.schedule_bulk_update,
        name="schedule_bulk_update",
    ),
    # 連絡機能
    path(
        "assignments/<int:assignment_id>/contact/<str:method>/",
        craftsman_views.contact_craftsman,
        name="contact_craftsman",
    ),
    # API
    path(
        "api/craftsman/<int:craftsman_id>/workload/",
        craftsman_views.craftsman_workload_api,
        name="craftsman_workload_api",
    ),
]
