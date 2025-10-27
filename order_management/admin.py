from django.contrib import admin
from .models import (
    Project, CashFlowTransaction, ForecastScenario,
    ProjectProgress, Report, SeasonalityIndex, UserProfile,
    Comment, Notification
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'management_no',
        'site_name',
        'work_type',
        'project_status',      # 旧: order_status
        'client_name',         # 旧: contractor_name
        'project_manager',
        'order_amount',        # 旧: estimate_amount
        'billing_amount',
        'amount_difference',
        'work_start_date',
        'work_end_date',
        'invoice_issued',
        'created_at'
    ]

    list_filter = [
        'project_status',  # 旧: order_status
        'work_type',
        'invoice_issued',
        'project_manager',
        'work_start_date',
        'created_at'
    ]

    search_fields = [
        'management_no',
        'site_name',
        'site_address',
        'client_name',     # 旧: contractor_name
        'project_manager',
        'notes'
    ]

    readonly_fields = [
        'management_no',
        'billing_amount',
        'amount_difference',
        'created_at',
        'updated_at'
    ]

    fieldsets = (
        ('基本情報', {
            'fields': (
                'management_no',
                'site_name',
                'site_address',
                'work_type'
            )
        }),
        ('受注・見積情報', {
            'fields': (
                'project_status',        # 旧: order_status
                'estimate_issued_date',
                'order_amount',          # 旧: estimate_amount
                'parking_fee'
            )
        }),
        ('元請・担当情報', {  # 旧: 業者・担当情報
            'fields': (
                'client_name',           # 旧: contractor_name
                'client_address',        # 旧: contractor_address
                'project_manager'
            )
        }),
        ('スケジュール', {
            'fields': (
                'work_start_date',
                'work_end_date',
                'contract_date',
                'completion_date'  # Phase 1 追加
            )
        }),
        ('請求・経費管理', {
            'fields': (
                'invoice_issued',
                'invoice_issue_datetime',  # Phase 1 追加
                'expense_item_1',
                'expense_amount_1',
                'expense_item_2',
                'expense_amount_2',
                'billing_amount',
                'amount_difference'
            )
        }),
        ('入金管理', {  # Phase 1 追加
            'fields': (
                'payment_due_date',
                'payment_received_date',
                'payment_received_amount'
            )
        }),
        ('支払管理', {  # Phase 1 追加
            'fields': (
                'payment_scheduled_date',
                'payment_executed_date',
                'payment_amount',
                'payment_status',
                'payment_memo'
            )
        }),
        ('その他', {
            'fields': (
                'notes',
                'created_at',
                'updated_at'
            )
        })
    )

    list_editable = [
        'project_status',  # 旧: order_status
        'invoice_issued'
    ]

    list_per_page = 20

    date_hierarchy = 'created_at'

    def get_list_display_links(self, request, list_display):
        return ['management_no', 'site_name']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context['status_color'] = obj.get_status_color()
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(CashFlowTransaction)
class CashFlowTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_date',
        'project',
        'transaction_type',
        'amount',
        'is_planned',
        'description',
        'created_at'
    ]

    list_filter = [
        'transaction_type',
        'is_planned',
        'transaction_date',
        'created_at'
    ]

    search_fields = [
        'project__management_no',
        'project__site_name',
        'description'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本情報', {
            'fields': (
                'project',
                'transaction_type',
                'transaction_date',
                'amount',
                'is_planned'
            )
        }),
        ('詳細情報', {
            'fields': (
                'description',
                'related_subcontract'
            )
        }),
        ('システム情報', {
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )

    date_hierarchy = 'transaction_date'
    list_per_page = 50


@admin.register(ForecastScenario)
class ForecastScenarioAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'scenario_type',
        'conversion_rate_neta',
        'conversion_rate_waiting',
        'cost_rate',
        'forecast_months',
        'is_active',
        'is_default',
        'created_by',
        'created_at'
    ]

    list_filter = [
        'scenario_type',
        'is_active',
        'is_default',
        'seasonality_enabled',
        'created_at'
    ]

    search_fields = [
        'name',
        'description'
    ]

    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('基本情報', {
            'fields': (
                'name',
                'description',
                'scenario_type',
                'is_active',
                'is_default'
            )
        }),
        ('成約率設定', {
            'fields': (
                'conversion_rate_neta',
                'conversion_rate_waiting'
            )
        }),
        ('コスト設定', {
            'fields': (
                'cost_rate',
                'fixed_cost_multiplier',
                'variable_cost_multiplier'
            )
        }),
        ('予測設定', {
            'fields': (
                'forecast_months',
                'seasonality_enabled'
            )
        }),
        ('予測結果', {
            'fields': (
                'forecast_results',
            ),
            'classes': ('collapse',)
        }),
        ('システム情報', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            )
        })
    )

    list_editable = ['is_active', 'is_default']
    list_per_page = 20
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        if not change:  # 新規作成時
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# =============================================================================
# Phase 3: 進捗管理・レポート機能
# =============================================================================

@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    """プロジェクト進捗管理"""
    list_display = [
        'project', 'recorded_date', 'progress_rate', 'status',
        'milestone_name', 'has_risk', 'recorded_by'
    ]
    list_filter = ['status', 'has_risk', 'recorded_date', 'milestone_completed']
    search_fields = ['project__name', 'project__management_no', 'notes', 'risk_description']
    date_hierarchy = 'recorded_date'

    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'recorded_date', 'recorded_by')
        }),
        ('進捗情報', {
            'fields': ('progress_rate', 'status', 'notes')
        }),
        ('マイルストーン', {
            'fields': ('milestone_name', 'milestone_date', 'milestone_completed')
        }),
        ('リスク・課題', {
            'fields': ('has_risk', 'risk_level', 'risk_description')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:  # 新規作成時
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """レポート管理"""
    list_display = [
        'title', 'report_type', 'period_start', 'period_end',
        'is_published', 'generated_by', 'generated_date'
    ]
    list_filter = ['report_type', 'is_published', 'generated_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'generated_date'

    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'report_type', 'description')
        }),
        ('対象期間', {
            'fields': ('period_start', 'period_end')
        }),
        ('レポートデータ', {
            'fields': ('report_data',),
            'classes': ('collapse',)
        }),
        ('PDF', {
            'fields': ('pdf_file',)
        }),
        ('公開設定', {
            'fields': ('is_published',)
        }),
        ('システム情報', {
            'fields': ('generated_by', 'generated_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['generated_date', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:  # 新規作成時
            obj.generated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SeasonalityIndex)
class SeasonalityIndexAdmin(admin.ModelAdmin):
    """季節性指数管理"""
    list_display = [
        'forecast_scenario', 'use_auto_calculation',
        'january_index', 'february_index', 'march_index',
        'created_at'
    ]
    list_filter = ['use_auto_calculation']
    search_fields = ['forecast_scenario__name']

    fieldsets = (
        ('シナリオ', {
            'fields': ('forecast_scenario', 'use_auto_calculation')
        }),
        ('1月～3月', {
            'fields': ('january_index', 'february_index', 'march_index')
        }),
        ('4月～6月', {
            'fields': ('april_index', 'may_index', 'june_index')
        }),
        ('7月～9月', {
            'fields': ('july_index', 'august_index', 'september_index')
        }),
        ('10月～12月', {
            'fields': ('october_index', 'november_index', 'december_index')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    actions = ['recalculate_from_historical_data']

    def recalculate_from_historical_data(self, request, queryset):
        """過去データから再計算"""
        count = 0
        for obj in queryset:
            obj.calculate_from_historical_data()
            count += 1
        self.message_user(request, f'{count}件の季節性指数を再計算しました。')
    recalculate_from_historical_data.short_description = '過去データから再計算'



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """ユーザープロファイル管理"""
    list_display = ["user", "get_roles_display", "created_at", "updated_at"]
    list_filter = []
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    
    fieldsets = (
        ("基本情報", {
            "fields": ("user", "roles")
        }),
        ("タイムスタンプ", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["created_at", "updated_at"]
    
    def get_roles_display(self, obj):
        """ロールの表示"""
        return ", ".join(obj.get_roles_display()) if obj.roles else "ロールなし"
    get_roles_display.short_description = "ロール"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """コメント管理"""
    list_display = ["project", "author", "get_content_preview", "is_important", "created_at"]
    list_filter = ["is_important", "created_at", "author"]
    search_fields = ["project__site_name", "project__management_no", "content", "author__username"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("基本情報", {
            "fields": ("project", "author", "content", "is_important")
        }),
        ("メンション", {
            "fields": ("mentioned_users",)
        }),
        ("タイムスタンプ", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def get_content_preview(self, obj):
        """コメント内容のプレビュー"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    get_content_preview.short_description = "コメント"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """通知管理"""
    list_display = ["recipient", "notification_type", "title", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["recipient__username", "title", "message"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]

    fieldsets = (
        ("基本情報", {
            "fields": ("recipient", "notification_type", "title", "message", "link", "is_read")
        }),
        ("関連情報", {
            "fields": ("related_comment", "related_project")
        }),
        ("タイムスタンプ", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )

