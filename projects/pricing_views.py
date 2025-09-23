from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Avg, Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal

from .models import (
    Project,
    ProjectCost,
    ProjectPricing,
    PricingAuditLog,
    Assignment,
    MaterialOrder,
    ProjectType,
)
from .pricing_forms import (
    ProjectCostForm,
    ProjectPricingForm,
    PricingComparisonForm,
    ProfitabilitySearchForm,
    CostEstimationForm,
)


def pricing_dashboard(request):
    """マージン設定ダッシュボード"""
    # 統計データ
    stats = {
        "total_projects_with_pricing": ProjectPricing.objects.filter(is_active=True)
        .values("project")
        .distinct()
        .count(),
        "avg_margin_rate": ProjectPricing.objects.filter(is_active=True).aggregate(
            Avg("margin_rate")
        )["margin_rate__avg"]
        or 0,
        "total_revenue": ProjectPricing.objects.filter(is_active=True).aggregate(
            Sum("final_price")
        )["final_price__sum"]
        or 0,
        "total_profit": ProjectPricing.objects.filter(is_active=True).aggregate(
            Sum("margin_amount")
        )["margin_amount__sum"]
        or 0,
    }

    # 収益性上位案件
    top_profitable_projects = (
        ProjectPricing.objects.filter(is_active=True, pricing_stage="final")
        .select_related("project")
        .order_by("-margin_rate")[:10]
    )

    # 工種別収益性
    profitability_by_type = (
        ProjectPricing.objects.filter(is_active=True, pricing_stage="final")
        .values("project__project_type__name")
        .annotate(avg_margin_rate=Avg("margin_rate"), project_count=Count("project"))
        .order_by("-avg_margin_rate")
    )

    # 最近の価格設定
    recent_pricing = (
        ProjectPricing.objects.filter(is_active=True)
        .select_related("project", "set_by")
        .order_by("-created_at")[:10]
    )

    context = {
        "stats": stats,
        "top_profitable_projects": top_profitable_projects,
        "profitability_by_type": profitability_by_type,
        "recent_pricing": recent_pricing,
    }
    return render(request, "pricing/dashboard.html", context)


def project_cost_setup(request, project_id):
    """案件コスト積算画面"""
    project = get_object_or_404(Project, id=project_id)

    try:
        project_cost = ProjectCost.objects.get(project=project)
    except ProjectCost.DoesNotExist:
        project_cost = None

    if request.method == "POST":
        form = ProjectCostForm(request.POST, instance=project_cost, project=project)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.project = project
            cost.save()
            messages.success(request, f"案件「{project.title}」のコスト情報を更新しました。")
            return redirect("project_pricing_setup", project_id=project.id)
    else:
        form = ProjectCostForm(instance=project_cost, project=project)

    # 関連データを取得
    assignments = Assignment.objects.filter(project=project).select_related("craftsman")
    material_orders = MaterialOrder.objects.filter(project=project).select_related(
        "supplier"
    )

    # 見積もりツール用のフォーム
    estimation_form = CostEstimationForm()

    context = {
        "project": project,
        "form": form,
        "project_cost": project_cost,
        "assignments": assignments,
        "material_orders": material_orders,
        "estimation_form": estimation_form,
    }
    return render(request, "pricing/cost_setup.html", context)


def project_pricing_setup(request, project_id):
    """案件マージン設定画面"""
    project = get_object_or_404(Project, id=project_id)

    # 現在の価格設定を取得
    current_pricing = ProjectPricing.get_current_pricing(project)

    if request.method == "POST":
        form = ProjectPricingForm(request.POST, project=project, user=request.user)
        if form.is_valid():
            pricing = form.save(commit=False)
            pricing.project = project
            pricing.save()

            # 監査ログを作成
            PricingAuditLog.objects.create(
                pricing=pricing,
                changed_by=request.user,
                change_type="created",
                new_values={
                    "margin_rate": float(pricing.margin_rate),
                    "final_price": float(pricing.final_price),
                    "pricing_stage": pricing.pricing_stage,
                },
                reason=pricing.notes,
            )

            messages.success(request, f"案件「{project.title}」のマージン設定を更新しました。")
            return redirect("pricing_detail", project_id=project.id)
    else:
        form = ProjectPricingForm(project=project, user=request.user)

    # コスト情報を取得
    try:
        project_cost = ProjectCost.objects.get(project=project)
    except ProjectCost.DoesNotExist:
        project_cost = None
        messages.warning(request, "コスト情報が設定されていません。先にコスト積算を行ってください。")

    # 価格比較フォーム
    comparison_form = PricingComparisonForm()

    # 推奨マージン率を取得
    recommended = ProjectPricing.get_recommended_margin_range(project.project_type)

    context = {
        "project": project,
        "form": form,
        "project_cost": project_cost,
        "current_pricing": current_pricing,
        "comparison_form": comparison_form,
        "recommended": recommended,
    }
    return render(request, "pricing/pricing_setup.html", context)


def pricing_detail(request, project_id):
    """案件価格詳細画面"""
    project = get_object_or_404(Project, id=project_id)

    # コスト情報
    try:
        project_cost = ProjectCost.objects.get(project=project)
    except ProjectCost.DoesNotExist:
        project_cost = None

    # 価格設定履歴
    pricing_history = (
        ProjectPricing.objects.filter(project=project)
        .select_related("set_by")
        .order_by("-created_at")
    )

    # 現在の価格設定
    current_pricing = ProjectPricing.get_current_pricing(project)

    # 監査ログ
    audit_logs = (
        PricingAuditLog.objects.filter(pricing__project=project)
        .select_related("pricing", "changed_by")
        .order_by("-created_at")[:20]
    )

    context = {
        "project": project,
        "project_cost": project_cost,
        "pricing_history": pricing_history,
        "current_pricing": current_pricing,
        "audit_logs": audit_logs,
    }
    return render(request, "pricing/detail.html", context)


def profitability_analysis(request):
    """収益性分析画面"""
    form = ProfitabilitySearchForm(request.GET)
    pricings = ProjectPricing.objects.filter(is_active=True).select_related(
        "project", "project__project_type"
    )

    if form.is_valid():
        data = form.cleaned_data
        if data["project_type"]:
            pricings = pricings.filter(project__project_type=data["project_type"])
        if data["profit_rate_min"]:
            pricings = pricings.filter(margin_rate__gte=data["profit_rate_min"])
        if data["profit_rate_max"]:
            pricings = pricings.filter(margin_rate__lte=data["profit_rate_max"])
        if data["pricing_stage"]:
            pricings = pricings.filter(pricing_stage=data["pricing_stage"])
        if data["date_from"]:
            pricings = pricings.filter(created_at__date__gte=data["date_from"])
        if data["date_to"]:
            pricings = pricings.filter(created_at__date__lte=data["date_to"])

    pricings = pricings.order_by("-margin_rate")

    # 統計情報
    analysis_stats = pricings.aggregate(
        avg_margin_rate=Avg("margin_rate"),
        total_revenue=Sum("final_price"),
        total_profit=Sum("margin_amount"),
    )

    context = {
        "form": form,
        "pricings": pricings,
        "analysis_stats": analysis_stats,
    }
    return render(request, "pricing/profitability_analysis.html", context)


def cost_estimation_api(request):
    """コスト見積もりAPI"""
    if request.method == "POST":
        form = CostEstimationForm(request.POST)
        if form.is_valid():
            estimated_cost = form.calculate_estimated_cost()
            return JsonResponse({"success": True, "estimated_cost": estimated_cost})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request method"})


def pricing_comparison_api(request):
    """価格比較API"""
    if request.method == "POST":
        form = PricingComparisonForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            base_cost = data["base_cost"]
            margin_rates = data["margin_rates"]

            comparisons = []
            for rate in margin_rates:
                margin_amount = base_cost * (Decimal(rate) / 100)
                final_price = base_cost + margin_amount
                margin_rate = (
                    round((margin_amount / final_price) * 100, 2)
                    if final_price > 0
                    else 0
                )

                comparisons.append(
                    {
                        "margin_rate": rate,
                        "margin_amount": float(margin_amount),
                        "final_price": float(final_price),
                        "margin_rate": margin_rate,
                        "formatted_margin_amount": f"¥{margin_amount:,.0f}",
                        "formatted_final_price": f"¥{final_price:,.0f}",
                    }
                )

            return JsonResponse({"success": True, "comparisons": comparisons})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request method"})


def margin_calculation_api(request):
    """マージン計算API"""
    if request.method == "GET":
        base_cost = request.GET.get("base_cost", 0)
        margin_rate = request.GET.get("margin_rate", 0)

        try:
            base_cost = Decimal(base_cost)
            margin_rate = Decimal(margin_rate)

            margin_amount = base_cost * (margin_rate / 100)
            final_price = base_cost + margin_amount
            margin_rate = (
                round((margin_amount / final_price) * 100, 2) if final_price > 0 else 0
            )

            return JsonResponse(
                {
                    "success": True,
                    "margin_amount": float(margin_amount),
                    "final_price": float(final_price),
                    "margin_rate": margin_rate,
                    "formatted_margin_amount": f"¥{margin_amount:,.0f}",
                    "formatted_final_price": f"¥{final_price:,.0f}",
                }
            )
        except (ValueError, TypeError):
            return JsonResponse({"success": False, "error": "Invalid input values"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


def project_cost_from_related_data(request, project_id):
    """関連データからコスト自動取得API"""
    project = get_object_or_404(Project, id=project_id)

    # 職人費用を計算
    assignments = Assignment.objects.filter(project=project)
    craftsman_cost = sum(assignment.total_amount or 0 for assignment in assignments)

    # 資材費を計算
    material_orders = MaterialOrder.objects.filter(project=project)
    material_cost = sum(order.estimated_cost or 0 for order in material_orders)

    # 調査費を計算（固定値または調査時間ベース）
    survey_cost = 5000  # 固定値

    return JsonResponse(
        {
            "success": True,
            "craftsman_cost": float(craftsman_cost),
            "material_cost": float(material_cost),
            "survey_cost": float(survey_cost),
            "total_estimated_cost": float(craftsman_cost + material_cost + survey_cost),
        }
    )
