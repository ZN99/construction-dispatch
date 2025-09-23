from django.urls import path
from . import views
from .views_auth import HeadquartersLoginView, HeadquartersLogoutView
from .views_permission import PermissionDeniedView
from .views_landing import LandingView
from .views_contractor import ContractorDashboardView, ContractorProjectsView, ContractorEditView
from .views_ordering import OrderingDashboardView, ExternalContractorManagementView, SupplierManagementView
from .views_contractor_create import ContractorCreateView
from .views_payment import PaymentDashboardView
from .views_receipt import ReceiptDashboardView
from .views_accounting import AccountingDashboardView
from .views_cost import (
    FixedCostListView, FixedCostCreateView, FixedCostUpdateView, FixedCostDeleteView,
    VariableCostListView, VariableCostCreateView, VariableCostUpdateView, VariableCostDeleteView,
    cost_dashboard
)
from .views_ultimate import UltimateDashboardView
from . import views_material

app_name = 'order_management'

urlpatterns = [
    # ランディング・認証・権限
    path('landing/', LandingView.as_view(), name='landing'),
    path('login/', HeadquartersLoginView.as_view(), name='login'),
    path('logout/', HeadquartersLogoutView.as_view(), name='logout'),
    path('permission-denied/', PermissionDeniedView.as_view(), name='permission_denied'),

    # ダッシュボード・案件管理
    path('', UltimateDashboardView.as_view(), name='dashboard'),
    path('legacy/', views.dashboard, name='legacy_dashboard'),
    path('contractor-dashboard/', ContractorDashboardView.as_view(), name='contractor_dashboard'),
    path('ordering-dashboard/', OrderingDashboardView.as_view(), name='ordering_dashboard'),
    path('external-contractors/', ExternalContractorManagementView.as_view(), name='external_contractor_management'),
    path('suppliers/', SupplierManagementView.as_view(), name='supplier_management'),
    path('accounting/', AccountingDashboardView.as_view(), name='accounting_dashboard'),
    path('ultimate/', UltimateDashboardView.as_view(), name='ultimate_dashboard'),
    path('payment/', PaymentDashboardView.as_view(), name='payment_dashboard'),
    path('receipt/', ReceiptDashboardView.as_view(), name='receipt_dashboard'),
    path('contractor/<int:contractor_id>/projects/', ContractorProjectsView.as_view(), name='contractor_projects'),
    path('contractors/<int:pk>/edit/', ContractorEditView.as_view(), name='contractor_edit'),
    path('contractors/new/', ContractorCreateView.as_view(), name='contractor_create'),
    path('list/', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/update/', views.project_update, name='project_update'),
    path('<int:pk>/update-progress/', views.update_progress, name='update_progress'),
    path('<int:pk>/add-subcontract/', views.add_subcontract, name='add_subcontract'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('api/list/', views.project_api_list, name='project_api_list'),
    path('api/staff/', views.staff_api, name='staff_api'),
    path('api/staff/<int:staff_id>/', views.staff_api, name='staff_api_detail'),
    path('api/contractor/', views.contractor_api, name='contractor_api'),
    path('api/contractor/<int:contractor_id>/', views.contractor_api, name='contractor_api_detail'),

    # 請求書API
    path('api/invoice/generate/', views.generate_client_invoice_api, name='generate_client_invoice_api'),
    path('api/invoice/preview/<int:project_id>/', views.get_invoice_preview_api, name='get_invoice_preview_api'),
    path('api/invoice/preview/client/', views.get_client_invoice_preview_api, name='client_invoice_preview_api'),

    # コスト管理
    path('cost/', cost_dashboard, name='cost_dashboard'),
    path('cost/fixed/', FixedCostListView.as_view(), name='fixed_cost_list'),
    path('cost/fixed/create/', FixedCostCreateView.as_view(), name='fixed_cost_create'),
    path('cost/fixed/<int:pk>/edit/', FixedCostUpdateView.as_view(), name='fixed_cost_update'),
    path('cost/fixed/<int:pk>/delete/', FixedCostDeleteView.as_view(), name='fixed_cost_delete'),
    path('cost/variable/', VariableCostListView.as_view(), name='variable_cost_list'),
    path('cost/variable/create/', VariableCostCreateView.as_view(), name='variable_cost_create'),
    path('cost/variable/<int:pk>/edit/', VariableCostUpdateView.as_view(), name='variable_cost_update'),
    path('cost/variable/<int:pk>/delete/', VariableCostDeleteView.as_view(), name='variable_cost_delete'),

    # 資材管理
    path('<int:project_id>/materials/', views_material.material_order_list, name='material_order_list'),
    path('<int:project_id>/materials/create/', views_material.material_order_create, name='material_order_create'),
    path('<int:project_id>/materials/<int:order_id>/', views_material.material_order_detail, name='material_order_detail'),
    path('<int:project_id>/materials/<int:order_id>/edit/', views_material.material_order_edit, name='material_order_edit'),
    path('<int:project_id>/materials/<int:order_id>/status/', views_material.material_order_status_update, name='material_order_status_update'),
]