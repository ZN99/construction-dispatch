from django.urls import path
from . import survey_views

survey_urlpatterns = [
    # 調査ダッシュボード
    path("surveys/", survey_views.survey_dashboard, name="survey_dashboard"),
    # 調査一覧・詳細
    path("surveys/list/", survey_views.SurveyListView.as_view(), name="survey_list"),
    path(
        "surveys/<int:pk>/",
        survey_views.SurveyDetailView.as_view(),
        name="survey_detail",
    ),
    # 調査カレンダー
    path("surveys/calendar/", survey_views.survey_calendar, name="survey_calendar"),
    # 調査アサイン
    path(
        "projects/<int:project_id>/assign-survey/",
        survey_views.survey_assign,
        name="survey_assign",
    ),
    path(
        "surveys/auto-assign/",
        survey_views.auto_assign_surveys,
        name="auto_assign_surveys",
    ),
    # 調査完了
    path(
        "surveys/<int:survey_id>/complete/",
        survey_views.survey_complete,
        name="survey_complete",
    ),
    path(
        "surveys/<int:survey_id>/reschedule/",
        survey_views.survey_reschedule,
        name="survey_reschedule",
    ),
    # ルート最適化
    path(
        "surveys/routes/", survey_views.survey_route_optimization, name="survey_routes"
    ),
]
