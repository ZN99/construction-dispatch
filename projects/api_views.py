from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from .models import Project
from order_management.models import Project as OrderProject


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


# Removed: add_survey_step function (ProjectProgressStep system has been removed)
# This functionality should be reimplemented using ProjectProgress if needed
