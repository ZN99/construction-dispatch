from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from .models import Project
from order_management.models import Project as OrderProject, ProgressStepTemplate, ProjectProgressStep


@csrf_exempt
@require_http_methods(["POST"])
def confirm_project(request, project_id):
    """案件を確定状態にする"""
    try:
        project = get_object_or_404(Project, id=project_id)

        if project.status != "draft":
            return JsonResponse({"success": False, "error": "既に確定済みの案件です"})

        project.status = "confirmed"
        project.save()

        return JsonResponse(
            {
                "success": True,
                "message": "案件を確定しました",
                "new_status": project.get_status_display(),
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def project_workflow_status(request, project_id):
    """プロジェクトのワークフロー状態を取得"""
    try:
        project = get_object_or_404(Project, id=project_id)
        workflow_progress = project.get_workflow_progress()

        return JsonResponse({"success": True, "workflow_progress": workflow_progress})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_survey_step(request, project_id):
    """プロジェクトに現地調査ステップを動的に追加"""
    try:
        project = get_object_or_404(OrderProject, id=project_id)

        # 既存の現地調査ステップがあるかチェック
        existing_survey_step = ProjectProgressStep.objects.filter(
            project=project,
            template__name="現地調査"
        ).exists()

        if existing_survey_step:
            return JsonResponse({
                "success": False,
                "error": "現地調査は既に設定されています"
            })

        # survey_requiredフラグを有効にする
        project.survey_required = True
        project.save()

        # 現地調査用のProgressStepTemplateを確認・作成
        survey_template, created = ProgressStepTemplate.objects.get_or_create(
            name="現地調査",
            defaults={
                "description": "現地での状況確認と測定を行います",
                "order": 2,  # 見積もりの後
                "is_required": False
            }
        )

        # プロジェクトに現地調査ステップを追加
        survey_step, step_created = ProjectProgressStep.objects.get_or_create(
            project=project,
            template=survey_template,
            defaults={
                "is_completed": False,
                "order": 2
            }
        )

        # 既存ステップの順序を調整（現地調査より後のステップを1つずつ後ろにずらす）
        if step_created:
            later_steps = ProjectProgressStep.objects.filter(
                project=project,
                order__gte=2
            ).exclude(id=survey_step.id)

            for step in later_steps:
                step.order += 1
                step.save()

        return JsonResponse({
            "success": True,
            "message": "現地調査ステップを追加しました",
            "survey_step_id": survey_step.id,
            "new_step_count": project.progress_steps.count()
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
