from django.urls import path
from . import survey_record_views

survey_record_urlpatterns = [
    # 調査記録ダッシュボード
    path(
        "survey-records/dashboard/",
        survey_record_views.survey_record_dashboard,
        name="survey_record_dashboard",
    ),
    # 調査開始 (パスを変更して競合を回避)
    path(
        "survey-records/<int:survey_id>/start/",
        survey_record_views.survey_start,
        name="project_survey_start",
    ),
    # 調査記録フォーム
    path(
        "survey-records/<int:report_id>/form/",
        survey_record_views.survey_record_form,
        name="survey_record_form",
    ),
    # 調査完了
    path(
        "survey-records/<int:report_id>/complete/",
        survey_record_views.survey_complete,
        name="survey_record_complete",
    ),
    # 写真アップロード（Ajax）
    path(
        "survey-records/<int:report_id>/photo-upload/",
        survey_record_views.photo_upload_ajax,
        name="photo_upload_ajax",
    ),
    # 音声メモアップロード
    path(
        "survey-records/<int:report_id>/voice-memo/",
        survey_record_views.voice_memo_upload,
        name="voice_memo_upload",
    ),
    # モバイル用調査一覧
    path(
        "survey-records/mobile/",
        survey_record_views.mobile_survey_list,
        name="mobile_survey_list",
    ),
    # 調査記録一覧・詳細
    path(
        "survey-reports/",
        survey_record_views.SurveyReportListView.as_view(),
        name="survey_report_list",
    ),
    path(
        "survey-reports/<int:pk>/",
        survey_record_views.SurveyReportDetailView.as_view(),
        name="survey_report_detail",
    ),
]
