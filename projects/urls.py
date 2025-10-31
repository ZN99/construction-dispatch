from django.urls import path, include
from . import views, api_views
from .survey_urls import survey_urlpatterns
from .survey_record_urls import survey_record_urlpatterns
from .craftsman_urls import craftsman_urlpatterns
from .material_urls import material_urlpatterns
from .pricing_urls import pricing_urlpatterns
from .construction_urls import construction_urlpatterns

urlpatterns = (
    [
        path("", views.landing_redirect, name="dashboard"),
        path("projects/", views.ProjectListView.as_view(), name="project_list"),
        path(
            "projects/<int:pk>/",
            views.ProjectDetailView.as_view(),
            name="project_detail",
        ),
        path(
            "projects/<int:pk>/update/",
            views.ProjectUpdateView.as_view(),
            name="project_update",
        ),
        path(
            "projects/create/",
            views.project_create_select_type,
            name="project_create_select_type",
        ),
        path(
            "projects/create/cross/",
            views.project_create_cross,
            name="project_create_cross",
        ),
        path(
            "projects/create/cleaning/",
            views.project_create_cleaning,
            name="project_create_cleaning",
        ),
        path(
            "projects/create/general/<int:project_type_id>/",
            views.project_create_general,
            name="project_create_general",
        ),
        path(
            "customers/create/",
            views.CustomerCreateView.as_view(),
            name="customer_create",
        ),
        path(
            "api/customers/search/",
            views.customer_search_ajax,
            name="customer_search_ajax",
        ),
        path(
            "api/projects/<int:project_id>/confirm/",
            api_views.confirm_project,
            name="api_confirm_project",
        ),
        path(
            "api/projects/<int:project_id>/workflow/",
            api_views.project_workflow_status,
            name="api_project_workflow",
        ),
        path(
            "api/projects/<int:project_id>/add-survey-step/",
            api_views.add_survey_step,
            name="api_add_survey_step",
        ),
    ]
    + survey_urlpatterns
    + survey_record_urlpatterns
    + craftsman_urlpatterns
    + material_urlpatterns
    + pricing_urlpatterns
    + construction_urlpatterns
)
