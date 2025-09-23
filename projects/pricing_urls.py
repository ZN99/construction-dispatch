from django.urls import path
from . import pricing_views

pricing_urlpatterns = [
    # ダッシュボード
    path("pricing/", pricing_views.pricing_dashboard, name="pricing_dashboard"),
    # コスト設定
    path(
        "pricing/projects/<int:project_id>/cost-setup/",
        pricing_views.project_cost_setup,
        name="project_cost_setup",
    ),
    # マージン設定
    path(
        "pricing/projects/<int:project_id>/pricing-setup/",
        pricing_views.project_pricing_setup,
        name="project_pricing_setup",
    ),
    # 価格詳細
    path(
        "pricing/projects/<int:project_id>/detail/",
        pricing_views.pricing_detail,
        name="pricing_detail",
    ),
    # 収益性分析
    path(
        "pricing/analysis/",
        pricing_views.profitability_analysis,
        name="profitability_analysis",
    ),
    # API エンドポイント
    path(
        "pricing/api/cost-estimation/",
        pricing_views.cost_estimation_api,
        name="cost_estimation_api",
    ),
    path(
        "pricing/api/comparison/",
        pricing_views.pricing_comparison_api,
        name="pricing_comparison_api",
    ),
    path(
        "pricing/api/margin-calculation/",
        pricing_views.margin_calculation_api,
        name="margin_calculation_api",
    ),
    path(
        "pricing/projects/<int:project_id>/cost-from-related/",
        pricing_views.project_cost_from_related_data,
        name="project_cost_from_related_data",
    ),
]
