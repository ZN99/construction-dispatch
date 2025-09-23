from django.urls import path
from . import views
from .views_ext import SurveyRecordDetailView, ProjectSurveyListView, ProjectSurveyCreateView
from .views_surveyor_management import (
    SurveyorListView, SurveyorDetailView, SurveyorCreateView,
    SurveyorUpdateView, SurveyorDeleteView, SurveyorDashboardView,
    surveyor_search_ajax, surveyor_detail_ajax
)
from .views_field_auth import (
    FieldSurveyorLoginView, FieldSurveyorLogoutView, FieldSurveyorDashboardView,
    FieldSurveyorSurveyListView, FieldSurveyorProfileView, FieldSurveyorChecklistView
)
from .views_checklist import (
    DemoSurveyListView, CrossReplacementChecklistView, start_step, complete_step, upload_step_photo,
    delete_photo, update_photo_caption, save_measurement_data, update_step_completion_status,
    SurveyFormRedirectView
)

app_name = 'surveys'

urlpatterns = [
    # 新しいURL構造に合わせる
    path('list/', views.SurveyListView.as_view(), name='survey_list'),
    path('records/<int:pk>/', SurveyRecordDetailView.as_view(), name='survey_record_detail'),

    # 現地調査スケジュール管理
    path('schedule/', views.SurveyScheduleView.as_view(), name='survey_schedule'),
    path('form/<int:pk>/', SurveyFormRedirectView.as_view(), name='survey_form'),

    # 既存のURL（互換性のため維持）
    path('', views.SurveyListView.as_view(), name='survey_list_compat'),
    path('create/', views.SurveyCreateView.as_view(), name='survey_create'),
    path('<int:pk>/', views.SurveyDetailView.as_view(), name='survey_detail'),
    path('<int:pk>/edit/', views.SurveyUpdateView.as_view(), name='survey_edit'),

    # 調査実施・調査員画面
    path('<int:pk>/start/', views.SurveyStartView.as_view(), name='survey_start'),
    path('<int:pk>/complete/', views.SurveyCompleteView.as_view(), name='survey_complete'),
    path('<int:pk>/report/', views.SurveyReportView.as_view(), name='survey_report'),
    path('<int:pk>/delete/', views.SurveyDeleteView.as_view(), name='survey_delete'),

    # API/AJAX エンドポイント
    path('<int:pk>/api/start/', views.survey_start_api, name='survey_start_api'),
    path('<int:pk>/api/save/', views.survey_save_api, name='survey_save_api'),
    path('<int:pk>/api/complete/', views.survey_complete_api, name='survey_complete_api'),
    path('<int:pk>/approve/', views.survey_approve_api, name='survey_approve'),

    # 案件に紐づく調査一覧
    path('project/<int:project_id>/', ProjectSurveyListView.as_view(), name='project_surveys'),
    path('project/<int:project_id>/create/', ProjectSurveyCreateView.as_view(), name='project_survey_create'),

    # 調査員管理
    path('surveyors/', SurveyorListView.as_view(), name='surveyor_list'),
    path('surveyors/dashboard/', SurveyorDashboardView.as_view(), name='surveyor_dashboard'),
    path('surveyors/create/', SurveyorCreateView.as_view(), name='surveyor_create'),
    path('surveyors/<int:pk>/', SurveyorDetailView.as_view(), name='surveyor_detail'),
    path('surveyors/<int:pk>/edit/', SurveyorUpdateView.as_view(), name='surveyor_update'),
    path('surveyors/<int:pk>/delete/', SurveyorDeleteView.as_view(), name='surveyor_delete'),

    # 調査員管理 AJAX
    path('surveyors/search-ajax/', surveyor_search_ajax, name='surveyor_search_ajax'),
    path('surveyors/<int:pk>/detail-ajax/', surveyor_detail_ajax, name='surveyor_detail_ajax'),

    # 現場調査員専用システム
    path('field/login/', FieldSurveyorLoginView.as_view(), name='field_login'),
    path('field/logout/', FieldSurveyorLogoutView.as_view(), name='field_logout'),
    path('field/dashboard/', FieldSurveyorDashboardView.as_view(), name='field_dashboard'),
    path('field/surveys/', FieldSurveyorSurveyListView.as_view(), name='field_survey_list'),
    path('field/profile/', FieldSurveyorProfileView.as_view(), name='field_profile'),

    # 現場調査員専用チェックリストシステム
    path('field/survey/<int:survey_id>/', FieldSurveyorChecklistView.as_view(), name='field_survey_checklist'),

    # クロス張り替え調査チェックリスト
    path('demo/', DemoSurveyListView.as_view(), name='demo_survey_list'),
    path('<int:survey_id>/checklist/cross-replacement/', CrossReplacementChecklistView.as_view(), name='cross_replacement_checklist'),
    path('<int:survey_id>/step/<int:step_id>/start/', start_step, name='start_step'),
    path('<int:survey_id>/step/<int:step_id>/complete/', complete_step, name='complete_step'),
    path('<int:survey_id>/step/<int:step_id>/upload-photo/', upload_step_photo, name='upload_step_photo'),
    path('<int:survey_id>/step/<int:step_id>/save-measurement/', save_measurement_data, name='save_measurement_data'),
    path('<int:survey_id>/photos/<int:photo_id>/delete/', delete_photo, name='delete_photo'),
    path('<int:survey_id>/photos/<int:photo_id>/update-caption/', update_photo_caption, name='update_photo_caption'),

    # Step completion status API
    path('<int:survey_id>/step-completion/', update_step_completion_status, name='update_step_completion_status'),
]