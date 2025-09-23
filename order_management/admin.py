from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'management_no',
        'site_name',
        'work_type',
        'order_status',
        'contractor_name',
        'project_manager',
        'estimate_amount',
        'billing_amount',
        'amount_difference',
        'work_start_date',
        'work_end_date',
        'invoice_issued',
        'created_at'
    ]

    list_filter = [
        'order_status',
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
        'contractor_name',
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
                'order_status',
                'estimate_issued_date',
                'estimate_amount',
                'parking_fee'
            )
        }),
        ('業者・担当情報', {
            'fields': (
                'contractor_name',
                'contractor_address',
                'project_manager'
            )
        }),
        ('スケジュール', {
            'fields': (
                'payment_due_date',
                'work_start_date',
                'work_end_date',
                'contract_date'
            )
        }),
        ('請求・経費管理', {
            'fields': (
                'invoice_issued',
                'expense_item_1',
                'expense_amount_1',
                'expense_item_2',
                'expense_amount_2',
                'billing_amount',
                'amount_difference'
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
        'order_status',
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
