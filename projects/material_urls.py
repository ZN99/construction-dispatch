from django.urls import path
from . import material_views

# 資材管理のURL設定
material_urlpatterns = [
    # ダッシュボード
    path("material/", material_views.material_dashboard, name="material_dashboard"),
    # 業者管理
    path("material/suppliers/", material_views.supplier_list, name="supplier_list"),
    path(
        "material/suppliers/create/",
        material_views.supplier_create,
        name="supplier_create",
    ),
    path(
        "material/suppliers/<int:supplier_id>/",
        material_views.supplier_detail,
        name="supplier_detail",
    ),
    path(
        "material/suppliers/<int:supplier_id>/edit/",
        material_views.supplier_edit,
        name="supplier_edit",
    ),
    # 発注管理
    path(
        "material/orders/",
        material_views.material_order_list,
        name="material_order_list",
    ),
    path(
        "material/orders/create/",
        material_views.material_order_create,
        name="material_order_create",
    ),
    path(
        "material/orders/create/<int:project_id>/",
        material_views.material_order_create,
        name="material_order_create",
    ),
    path(
        "material/orders/<int:order_id>/",
        material_views.material_order_detail,
        name="material_order_detail",
    ),
    path(
        "material/orders/<int:order_id>/edit/",
        material_views.material_order_edit,
        name="material_order_edit",
    ),
    path(
        "material/orders/<int:order_id>/status/",
        material_views.material_order_status_update,
        name="material_order_status_update",
    ),
    # 案件別資材管理
    path(
        "projects/<int:project_id>/materials/",
        material_views.project_materials_view,
        name="project_materials_view",
    ),
    # API
    path(
        "material/api/suppliers-by-project-type/",
        material_views.get_suppliers_by_project_type,
        name="get_suppliers_by_project_type",
    ),
]
