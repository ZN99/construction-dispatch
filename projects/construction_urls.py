from django.urls import path
from . import construction_views

construction_urlpatterns = [
    # ダッシュボード
    path(
        "construction/",
        construction_views.construction_dashboard,
        name="construction_dashboard",
    ),
    # 案件別進捗管理
    path(
        "construction/projects/<int:project_id>/",
        construction_views.project_progress_detail,
        name="project_progress_detail",
    ),
    path(
        "construction/projects/<int:project_id>/progress/create/",
        construction_views.progress_report_create,
        name="progress_report_create",
    ),
    path(
        "construction/projects/<int:project_id>/quick-progress/",
        construction_views.quick_progress_update,
        name="quick_progress_update",
    ),
    # 問題管理
    path(
        "construction/projects/<int:project_id>/issue/create/",
        construction_views.issue_create,
        name="issue_create",
    ),
    path(
        "construction/issues/<int:issue_id>/update/",
        construction_views.issue_update,
        name="issue_update",
    ),
    path("construction/issues/", construction_views.issues_list, name="issues_list"),
    # 完了管理
    path(
        "construction/projects/<int:project_id>/completion/",
        construction_views.completion_manage,
        name="completion_manage",
    ),
    # 写真管理
    path(
        "construction/projects/<int:project_id>/photos/",
        construction_views.photo_gallery,
        name="photo_gallery",
    ),
    # 検索・分析
    path(
        "construction/search/",
        construction_views.progress_search,
        name="progress_search",
    ),
    path(
        "construction/analytics/",
        construction_views.progress_analytics,
        name="progress_analytics",
    ),
    # 編集セッション管理
    path(
        "construction/projects/<int:project_id>/edit-session/save/",
        construction_views.edit_session_save,
        name="edit_session_save",
    ),
    path(
        "construction/projects/<int:project_id>/edit-session/load/",
        construction_views.edit_session_load,
        name="edit_session_load",
    ),
]
