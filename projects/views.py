from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Project, Customer, ProjectType, Survey
from .forms import (
    ProjectTypeSelectForm,
    CrossProjectForm,
    CleaningProjectForm,
    GeneralProjectForm,
    CustomerForm,
)


def create_survey_if_needed(project):
    """現調必要な案件に対して自動的に調査を作成"""
    if project.requires_survey:
        # 予定調査日を案件開始日の3日前に設定
        survey_date = timezone.datetime.combine(
            project.start_date - timedelta(days=3), timezone.datetime.min.time()
        )
        survey_date = timezone.make_aware(survey_date)

        survey = Survey.objects.create(
            project=project,
            scheduled_date=survey_date,
            status="scheduled",
            priority="normal",
            notes=f"{project.title}の現地調査",
        )
        return survey
    return None


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 20

    def get_queryset(self):
        queryset = Project.objects.select_related("customer", "project_type")

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(customer__name__icontains=search)
                | Q(address__icontains=search)
            )

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        project_type = self.request.GET.get("project_type")
        if project_type:
            queryset = queryset.filter(project_type_id=project_type)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_types"] = ProjectType.objects.filter(is_active=True)
        context["status_choices"] = Project.STATUS_CHOICES
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workflow_progress"] = self.object.get_workflow_progress()
        return context


def project_create_select_type(request):
    if request.method == "POST":
        form = ProjectTypeSelectForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data["customer"]
            project_type = form.cleaned_data["project_type"]

            # セッションに顧客IDを保存
            request.session["selected_customer_id"] = customer.id

            if project_type.name == "クロス":
                return redirect("project_create_cross")
            elif project_type.name == "クリーニング":
                return redirect("project_create_cleaning")
            else:
                return redirect(
                    "project_create_general", project_type_id=project_type.id
                )
    else:
        form = ProjectTypeSelectForm()

    return render(request, "projects/project_create_select_type.html", {"form": form})


def project_create_cross(request):
    selected_customer_id = request.session.get("selected_customer_id")

    if request.method == "POST":
        form = CrossProjectForm(request.POST, selected_customer_id=selected_customer_id)
        if form.is_valid():
            project = form.save()

            # 現調必要な場合は自動的に調査を作成
            survey = create_survey_if_needed(project)

            # セッションから顧客IDをクリア
            if "selected_customer_id" in request.session:
                del request.session["selected_customer_id"]

            success_msg = "クロス案件を登録しました。"
            if survey:
                success_msg += f" 現地調査({survey.scheduled_date})が自動登録されました。"
            messages.success(request, success_msg)
            return redirect("project_detail", pk=project.pk)
    else:
        form = CrossProjectForm(selected_customer_id=selected_customer_id)

    return render(request, "projects/project_create_cross.html", {"form": form})


def project_create_cleaning(request):
    selected_customer_id = request.session.get("selected_customer_id")

    if request.method == "POST":
        form = CleaningProjectForm(
            request.POST, selected_customer_id=selected_customer_id
        )
        if form.is_valid():
            project = form.save()

            # 現調必要な場合は自動的に調査を作成
            survey = create_survey_if_needed(project)

            # セッションから顧客IDをクリア
            if "selected_customer_id" in request.session:
                del request.session["selected_customer_id"]

            success_msg = "クリーニング案件を登録しました。"
            if survey:
                success_msg += (
                    f' 現地調査({survey.scheduled_date.strftime("%Y年%m月%d日")})が自動登録されました。'
                )
            messages.success(request, success_msg)
            return redirect("project_detail", pk=project.pk)
        else:
            # フォームエラーがある場合、エラーメッセージを表示
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = CleaningProjectForm(selected_customer_id=selected_customer_id)

    context = {
        "form": form,
        "has_selected_customer": selected_customer_id is not None,
        "show_workflow_warning": selected_customer_id is None,
    }
    return render(request, "projects/project_create_cleaning.html", context)


def project_create_general(request, project_type_id):
    project_type = get_object_or_404(ProjectType, id=project_type_id)
    selected_customer_id = request.session.get("selected_customer_id")

    if request.method == "POST":
        form = GeneralProjectForm(
            request.POST,
            project_type=project_type,
            selected_customer_id=selected_customer_id,
        )
        if form.is_valid():
            project = form.save()

            # 現調必要な場合は自動的に調査を作成
            survey = create_survey_if_needed(project)

            # セッションから顧客IDをクリア
            if "selected_customer_id" in request.session:
                del request.session["selected_customer_id"]

            success_msg = f"{project_type.name}案件を登録しました。"
            if survey:
                success_msg += f" 現地調査({survey.scheduled_date})が自動登録されました。"
            messages.success(request, success_msg)
            return redirect("project_detail", pk=project.pk)
    else:
        form = GeneralProjectForm(
            project_type=project_type, selected_customer_id=selected_customer_id
        )

    return render(
        request,
        "projects/project_create_general.html",
        {"form": form, "project_type": project_type},
    )


class ProjectUpdateView(UpdateView):
    model = Project
    template_name = "projects/project_update.html"
    fields = [
        "customer",
        "title",
        "address",
        "start_date",
        "end_date",
        "amount",
        "status",
        "notes",
    ]
    success_url = reverse_lazy("project_list")

    def form_valid(self, form):
        messages.success(self.request, "案件を更新しました。")
        return super().form_valid(form)


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "projects/customer_create.html"
    success_url = reverse_lazy("project_create_select_type")

    def form_valid(self, form):
        messages.success(self.request, "顧客を登録しました。")
        return super().form_valid(form)


def customer_search_ajax(request):
    term = request.GET.get("term", "")
    customers = Customer.objects.filter(name__icontains=term)[:10]

    data = []
    for customer in customers:
        data.append(
            {
                "id": customer.id,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
            }
        )

    return JsonResponse(data, safe=False)


def landing_redirect(request):
    """メインURL（/）からランディングページへリダイレクト"""
    return redirect('order_management:landing')


def dashboard(request):
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(
        status__in=["confirmed", "in_progress"]
    ).count()
    recent_projects = Project.objects.select_related(
        "customer", "project_type"
    ).order_by("-created_at")[:5]

    context = {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "recent_projects": recent_projects,
    }

    return render(request, "projects/dashboard.html", context)
