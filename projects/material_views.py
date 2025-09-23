from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

from .models import (
    Supplier,
    MaterialOrder,
    Project,
    ProjectType,
    Survey,
    SurveyReport,
    Assignment,
)
from .material_forms import (
    SupplierSearchForm,
    SupplierForm,
    MaterialOrderForm,
    MaterialOrderStatusForm,
    MaterialOrderSearchForm,
)


def material_dashboard(request):
    """資材管理ダッシュボード"""
    today = timezone.now().date()

    # 統計データ
    stats = {
        "total_suppliers": Supplier.objects.filter(is_active=True).count(),
        "pending_orders": MaterialOrder.objects.filter(status="draft").count(),
        "ordered_today": MaterialOrder.objects.filter(order_date__date=today).count(),
        "overdue_deliveries": MaterialOrder.objects.filter(
            delivery_date__lt=today, status__in=["draft", "ordered"]
        ).count(),
    }

    # 最近の発注
    recent_orders = MaterialOrder.objects.select_related(
        "project", "supplier", "ordered_by"
    ).order_by("-created_at")[:10]

    # 納期が近い発注
    upcoming_deliveries = (
        MaterialOrder.objects.filter(
            delivery_date__range=[today, today + timedelta(days=7)],
            status__in=["draft", "ordered"],
        )
        .select_related("project", "supplier")
        .order_by("delivery_date")[:10]
    )

    # 月別統計
    monthly_stats = MaterialOrder.objects.filter(
        order_date__month=today.month, order_date__year=today.year
    ).aggregate(total_amount=Sum("estimated_cost"), order_count=Count("id"))

    context = {
        "stats": stats,
        "recent_orders": recent_orders,
        "upcoming_deliveries": upcoming_deliveries,
        "monthly_stats": monthly_stats,
    }
    return render(request, "material/dashboard.html", context)


def supplier_list(request):
    """業者一覧"""
    form = SupplierSearchForm(request.GET)
    suppliers = Supplier.objects.prefetch_related("specialties").all()

    if form.is_valid():
        if form.cleaned_data["name"]:
            suppliers = suppliers.filter(name__icontains=form.cleaned_data["name"])
        if form.cleaned_data["project_type"]:
            suppliers = suppliers.filter(specialties=form.cleaned_data["project_type"])
        if form.cleaned_data["is_active"] is not None:
            suppliers = suppliers.filter(is_active=form.cleaned_data["is_active"])

    suppliers = suppliers.order_by("name")

    context = {
        "suppliers": suppliers,
        "form": form,
    }
    return render(request, "material/supplier_list.html", context)


def supplier_detail(request, supplier_id):
    """業者詳細"""
    supplier = get_object_or_404(Supplier, id=supplier_id)

    # 発注履歴
    orders = (
        MaterialOrder.objects.filter(supplier=supplier)
        .select_related("project", "ordered_by")
        .order_by("-created_at")
    )

    # 統計
    stats = {
        "total_orders": orders.count(),
        "total_amount": orders.aggregate(Sum("estimated_cost"))["estimated_cost__sum"]
        or 0,
        "avg_delivery_days": orders.filter(actual_delivery_date__isnull=False)
        .extra(select={"delivery_days": "DATEDIFF(actual_delivery_date, order_date)"})
        .aggregate(Avg("delivery_days"))["delivery_days__avg"]
        or 0,
    }

    context = {
        "supplier": supplier,
        "orders": orders[:20],  # 最新20件
        "stats": stats,
    }
    return render(request, "material/supplier_detail.html", context)


def supplier_create(request):
    """業者登録"""
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"業者「{supplier.name}」を登録しました。")
            return redirect("supplier_detail", supplier_id=supplier.id)
    else:
        form = SupplierForm()

    context = {"form": form}
    return render(request, "material/supplier_form.html", context)


def supplier_edit(request, supplier_id):
    """業者編集"""
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"業者「{supplier.name}」を更新しました。")
            return redirect("supplier_detail", supplier_id=supplier.id)
    else:
        form = SupplierForm(instance=supplier)

    context = {"form": form, "supplier": supplier}
    return render(request, "material/supplier_form.html", context)


def material_order_list(request):
    """発注一覧"""
    form = MaterialOrderSearchForm(request.GET)
    orders = MaterialOrder.objects.select_related(
        "project", "supplier", "ordered_by"
    ).all()

    if form.is_valid():
        if form.cleaned_data["project"]:
            orders = orders.filter(project=form.cleaned_data["project"])
        if form.cleaned_data["supplier"]:
            orders = orders.filter(supplier=form.cleaned_data["supplier"])
        if form.cleaned_data["status"]:
            orders = orders.filter(status=form.cleaned_data["status"])
        if form.cleaned_data["order_date_from"]:
            orders = orders.filter(
                order_date__date__gte=form.cleaned_data["order_date_from"]
            )
        if form.cleaned_data["order_date_to"]:
            orders = orders.filter(
                order_date__date__lte=form.cleaned_data["order_date_to"]
            )
        if form.cleaned_data["overdue_only"]:
            today = timezone.now().date()
            orders = orders.filter(
                delivery_date__lt=today, status__in=["draft", "ordered"]
            )

    orders = orders.order_by("-created_at")

    context = {
        "orders": orders,
        "form": form,
    }
    return render(request, "material/order_list.html", context)


def material_order_detail(request, order_id):
    """発注詳細"""
    order = get_object_or_404(MaterialOrder, id=order_id)

    # 案件の関連情報を取得
    project_info = {
        "survey": Survey.objects.filter(project=order.project).first(),
        "survey_report": SurveyReport.objects.filter(
            survey__project=order.project
        ).first(),
        "assignments": Assignment.objects.filter(project=order.project).select_related(
            "craftsman"
        ),
    }

    context = {
        "order": order,
        "project_info": project_info,
    }
    return render(request, "material/order_detail.html", context)


def material_order_create(request, project_id=None):
    """資材発注作成"""
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = MaterialOrderForm(request.POST, user=request.user, project_id=project_id)
        if form.is_valid():
            order = form.save(commit=False)
            order.ordered_by = request.user
            order.save()
            messages.success(request, f"発注「{order.order_number}」を作成しました。")
            return redirect("material_order_detail", order_id=order.id)
    else:
        form = MaterialOrderForm(user=request.user, project_id=project_id)

    # 案件情報を取得
    project_info = None
    if project:
        survey = Survey.objects.filter(project=project).first()
        survey_report = (
            SurveyReport.objects.filter(survey=survey).first() if survey else None
        )
        assignments = Assignment.objects.filter(project=project).select_related(
            "craftsman"
        )

        project_info = {
            "project": project,
            "survey": survey,
            "survey_report": survey_report,
            "assignments": assignments,
        }

    context = {
        "form": form,
        "project": project,
        "project_info": project_info,
    }
    return render(request, "material/order_form.html", context)


def material_order_edit(request, order_id):
    """発注編集"""
    order = get_object_or_404(MaterialOrder, id=order_id)

    if request.method == "POST":
        form = MaterialOrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"発注「{order.order_number}」を更新しました。")
            return redirect("material_order_detail", order_id=order.id)
    else:
        form = MaterialOrderForm(instance=order, user=request.user)

    context = {
        "form": form,
        "order": order,
    }
    return render(request, "material/order_form.html", context)


def material_order_status_update(request, order_id):
    """発注ステータス更新"""
    order = get_object_or_404(MaterialOrder, id=order_id)

    if request.method == "POST":
        form = MaterialOrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"発注「{order.order_number}」のステータスを更新しました。")
            return redirect("material_order_detail", order_id=order.id)
    else:
        form = MaterialOrderStatusForm(instance=order)

    context = {
        "form": form,
        "order": order,
    }
    return render(request, "material/order_status_form.html", context)


def project_materials_view(request, project_id):
    """案件別資材管理画面"""
    project = get_object_or_404(Project, id=project_id)

    # 案件の関連情報
    survey = Survey.objects.filter(project=project).first()
    survey_report = (
        SurveyReport.objects.filter(survey=survey).first() if survey else None
    )
    assignments = Assignment.objects.filter(project=project).select_related("craftsman")
    material_orders = MaterialOrder.objects.filter(project=project).select_related(
        "supplier"
    )

    # 工種に対応した業者リスト
    suitable_suppliers = Supplier.objects.filter(
        specialties=project.project_type, is_active=True
    ).prefetch_related("specialties")

    context = {
        "project": project,
        "survey": survey,
        "survey_report": survey_report,
        "assignments": assignments,
        "material_orders": material_orders,
        "suitable_suppliers": suitable_suppliers,
    }
    return render(request, "material/project_materials.html", context)


def get_suppliers_by_project_type(request):
    """工種による業者フィルタリング（AJAX）"""
    project_type_id = request.GET.get("project_type_id")
    suppliers = []

    if project_type_id:
        suppliers_qs = Supplier.objects.filter(
            specialties__id=project_type_id, is_active=True
        ).distinct()

        suppliers = [
            {"id": s.id, "name": s.name, "contact_person": s.contact_person}
            for s in suppliers_qs
        ]

    return JsonResponse({"suppliers": suppliers})
