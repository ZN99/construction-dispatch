from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_http_methods
import json
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

from .models import Survey, SurveyReport, SurveyPhoto, Surveyor, WorkerNotification
from .survey_record_forms import (
    SurveyRecordForm,
    SurveyPhotoUploadForm,
    SurveyStartForm,
    SurveyCompletionForm,
    QuickPhotoForm,
    VoiceMemoForm,
)


def survey_record_dashboard(request):
    """調査記録ダッシュボード"""
    today = timezone.now().date()

    # 今日の調査予定
    today_surveys = Survey.objects.filter(
        scheduled_date__date=today, status__in=["scheduled", "in_progress"]
    ).select_related("project", "project__customer", "surveyor")

    # 進行中の調査
    in_progress = Survey.objects.filter(status="in_progress").select_related(
        "project", "project__customer", "surveyor"
    )

    # 最近完了した調査
    recent_completed = SurveyReport.objects.filter(
        is_ready_for_assignment=True,
        created_at__date__gte=today - timezone.timedelta(days=7),
    ).select_related("survey", "survey__project")[:10]

    context = {
        "today_surveys": today_surveys,
        "in_progress": in_progress,
        "recent_completed": recent_completed,
        "today": today,
    }
    return render(request, "surveys/record_dashboard.html", context)


def survey_start(request, survey_id):
    """調査開始"""
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == "POST":
        with transaction.atomic():
            # 調査ステータスを進行中に更新
            survey.status = "in_progress"
            survey.actual_start_time = timezone.now()
            survey.save()

            # 調査記録を取得または作成
            survey_report, created = SurveyReport.objects.get_or_create(
                survey=survey,
                defaults={
                    "actual_area": 0.0,  # 初期値、後で更新される
                    "access_notes": "",  # 初期値、後で更新される
                    "surveyor_notes": "",  # 初期値、後で更新される
                }
            )

            if created:
                messages.success(request, f"調査「{survey.project.title}」を開始しました")
            else:
                messages.info(request, f"調査「{survey.project.title}」を再開しました")

            return redirect("survey_record_form", report_id=survey_report.id)

    context = {
        "survey": survey,
    }
    return render(request, "surveys/survey_start.html", context)


def survey_record_form(request, report_id):
    """調査記録フォーム"""
    report = get_object_or_404(SurveyReport, id=report_id)

    if request.method == "POST":
        form = SurveyRecordForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.updated_at = timezone.now()
            report.save()
            messages.success(request, "調査記録を保存しました")
            return redirect("survey_record_form", report_id=report.id)
    else:
        form = SurveyRecordForm(instance=report)

    # 関連写真を取得
    photos = SurveyPhoto.objects.filter(survey_report=report)

    context = {
        "form": form,
        "report": report,
        "photos": photos,
        "survey": report.survey,
    }
    return render(request, "surveys/survey_record_form.html", context)


@csrf_exempt
def photo_upload_ajax(request, report_id):
    """写真アップロード（Ajax）"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    report = get_object_or_404(SurveyReport, id=report_id)

    try:
        photo_file = request.FILES.get("photo")
        location = request.POST.get("location", "overview")
        description = request.POST.get("description", "")

        if not photo_file:
            return JsonResponse({"error": "写真ファイルが必要です"}, status=400)

        # 画像の圧縮
        image = Image.open(photo_file)

        # サイズ制限（最大1920px）
        max_size = 1920
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # JPEGで保存
        output = BytesIO()
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")
        image.save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)

        # ファイル名を生成
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"survey_{report.id}_{location}_{timestamp}.jpg"

        # SurveyPhotoオブジェクトを作成
        survey_photo = SurveyPhoto.objects.create(
            survey_report=report, location=location, description=description
        )

        # 圧縮した画像を保存
        survey_photo.photo.save(filename, ContentFile(output.getvalue()), save=True)

        return JsonResponse(
            {
                "success": True,
                "photo_id": survey_photo.id,
                "photo_url": survey_photo.photo.url,
                "description": survey_photo.description,
                "location": survey_photo.get_location_display(),
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def survey_complete(request, report_id):
    """調査完了"""
    report = get_object_or_404(SurveyReport, id=report_id)
    survey = report.survey

    if request.method == "POST":
        form = SurveyCompletionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                status = form.cleaned_data["status"]
                completion_notes = form.cleaned_data["completion_notes"]

                # 調査記録の更新
                report.is_ready_for_assignment = status == "completed"
                if completion_notes:
                    report.surveyor_notes = (
                        report.surveyor_notes or ""
                    ) + f"\n[完了時メモ] {completion_notes}"
                report.save()

                # 調査ステータスの更新
                if status == "completed":
                    survey.status = "completed"
                    survey.actual_end_time = timezone.now()
                    survey.is_survey_completed = True
                elif status == "rescheduled":
                    survey.status = "rescheduled"
                else:
                    survey.status = "completed"
                    survey.actual_end_time = timezone.now()

                survey.save()

                # 職人への通知を作成
                if status == "completed":
                    create_worker_notifications(survey, report)

                messages.success(request, f'調査を{form.cleaned_data["status"]}として完了しました')
                return redirect("survey_record_dashboard")
    else:
        form = SurveyCompletionForm()

    context = {
        "form": form,
        "report": report,
        "survey": survey,
    }
    return render(request, "surveys/survey_complete.html", context)


def create_worker_notifications(survey, report):
    """職人への通知を作成"""
    notification_message = f"""
新しい調査が完了しました。

案件: {survey.project.title}
顧客: {survey.project.customer.name}
調査日: {survey.actual_start_time.strftime('%Y年%m月%d日')}
調査員: {survey.surveyor.name}

実測面積: {report.actual_area}㎡
作業難易度: {report.get_difficulty_level_display()}
想定作業日数: {report.estimated_work_days}日

アクセス情報: {report.access_notes[:100]}...
特記事項: {report.special_requirements[:100] if report.special_requirements else 'なし'}
"""

    WorkerNotification.objects.create(
        survey_report=report,
        notification_type="survey_completed",
        title=f"調査完了通知 - {survey.project.title}",
        message=notification_message,
        recipient_email="craftsman-manager@example.com",  # 実際の実装では設定から取得
    )


def mobile_survey_list(request):
    """モバイル用調査一覧"""
    surveyor_id = request.GET.get("surveyor_id")

    if surveyor_id:
        surveys = Survey.objects.filter(
            surveyor_id=surveyor_id, status__in=["scheduled", "in_progress"]
        ).select_related("project", "project__customer")
    else:
        surveys = Survey.objects.filter(
            status__in=["scheduled", "in_progress"]
        ).select_related("project", "project__customer", "surveyor")

    context = {
        "surveys": surveys,
        "is_mobile": True,
    }
    return render(request, "surveys/mobile_survey_list.html", context)


@require_http_methods(["POST"])
def voice_memo_upload(request, report_id):
    """音声メモアップロード"""
    report = get_object_or_404(SurveyReport, id=report_id)

    try:
        voice_file = request.FILES.get("voice_file")
        description = request.POST.get("memo_description", "")

        if not voice_file:
            return JsonResponse({"error": "音声ファイルが必要です"}, status=400)

        # ファイル保存のロジック
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_memo_{report.id}_{timestamp}.wav"

        # 音声ファイルの保存先を設定
        voice_path = f"voice_memos/{filename}"

        # ここでは簡単にパスのみ保存（実際の実装では適切なファイル処理が必要）
        report.voice_memo_url = voice_path
        if description:
            report.surveyor_notes = (
                report.surveyor_notes or ""
            ) + f"\n[音声メモ] {description}"
        report.save()

        return JsonResponse({"success": True, "message": "音声メモが保存されました"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class SurveyReportListView(ListView):
    """調査記録一覧"""

    model = SurveyReport
    template_name = "surveys/report_list.html"
    context_object_name = "reports"
    paginate_by = 20

    def get_queryset(self):
        return SurveyReport.objects.select_related(
            "survey", "survey__project", "survey__project__customer", "survey__surveyor"
        ).order_by("-created_at")


class SurveyReportDetailView(DetailView):
    """調査記録詳細"""

    model = SurveyReport
    template_name = "surveys/report_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["photos"] = SurveyPhoto.objects.filter(survey_report=self.object)
        return context
