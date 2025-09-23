from django.contrib import admin
from .models import (
    Customer,
    ProjectType,
    Project,
    Worker,
    ProjectAssignment,
    Surveyor,
    Survey,
    SurveyAvailability,
    SurveyRoute,
    SurveyReport,
    SurveyPhoto,
    WorkerNotification,
    SurveyTemplate,
    Craftsman,
    CraftsmanSchedule,
    Assignment,
    CraftsmanRating,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "created_at"]
    search_fields = ["name", "phone", "email"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "customer",
        "project_type",
        "status",
        "start_date",
        "end_date",
        "formatted_amount",
    ]
    list_filter = ["status", "project_type", "start_date", "created_at"]
    search_fields = ["title", "customer__name", "address"]
    raw_id_fields = ["customer"]
    readonly_fields = ["created_at", "updated_at", "formatted_amount", "duration_days"]
    fieldsets = (
        ("基本情報", {"fields": ("customer", "project_type", "title", "status")}),
        ("期間・場所", {"fields": ("start_date", "end_date", "address")}),
        ("金額", {"fields": ("amount", "formatted_amount")}),
        ("詳細", {"fields": ("details", "notes"), "classes": ("collapse",)}),
        (
            "システム情報",
            {
                "fields": ("duration_days", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "hourly_rate", "is_active", "created_at"]
    list_filter = ["is_active", "skills", "created_at"]
    search_fields = ["name", "phone", "email"]
    filter_horizontal = ["skills"]
    readonly_fields = ["created_at"]


@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ["project", "worker", "assigned_date", "is_confirmed"]
    list_filter = ["is_confirmed", "assigned_date", "project__project_type"]
    search_fields = ["project__title", "worker__name"]
    raw_id_fields = ["project", "worker"]


@admin.register(Surveyor)
class SurveyorAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone",
        "base_location",
        "daily_capacity",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "base_location", "created_at"]
    search_fields = ["name", "phone", "email"]
    readonly_fields = ["created_at", "daily_work_hours"]
    fieldsets = (
        ("基本情報", {"fields": ("name", "phone", "email", "is_active")}),
        (
            "勤務設定",
            {
                "fields": (
                    "base_location",
                    "daily_capacity",
                    "work_start_time",
                    "work_end_time",
                    "daily_work_hours",
                )
            },
        ),
        ("システム情報", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = [
        "project",
        "surveyor",
        "scheduled_date",
        "status",
        "priority",
        "is_survey_completed",
    ]
    list_filter = [
        "status",
        "priority",
        "is_survey_completed",
        "scheduled_date",
        "surveyor",
    ]
    search_fields = ["project__title", "project__customer__name", "surveyor__name"]
    raw_id_fields = ["project"]
    readonly_fields = ["created_at", "updated_at", "duration_actual", "is_overdue"]
    date_hierarchy = "scheduled_date"

    fieldsets = (
        ("基本情報", {"fields": ("project", "surveyor", "status", "priority")}),
        (
            "スケジュール",
            {
                "fields": (
                    "scheduled_date",
                    "estimated_duration",
                    "actual_start_time",
                    "actual_end_time",
                    "duration_actual",
                )
            },
        ),
        ("調査詳細", {"fields": ("access_info", "notes")}),
        (
            "調査結果",
            {
                "fields": (
                    "is_survey_completed",
                    "site_condition",
                    "customer_requirements",
                    "technical_notes",
                    "additional_work_needed",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "システム情報",
            {
                "fields": ("is_overdue", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("project", "surveyor", "project__customer")
        )


@admin.register(SurveyAvailability)
class SurveyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ["surveyor", "date", "start_time", "end_time", "is_available"]
    list_filter = ["is_available", "date", "surveyor"]
    search_fields = ["surveyor__name"]
    date_hierarchy = "date"


@admin.register(SurveyRoute)
class SurveyRouteAdmin(admin.ModelAdmin):
    list_display = ["surveyor", "date", "total_travel_time", "created_at"]
    list_filter = ["date", "surveyor", "created_at"]
    search_fields = ["surveyor__name"]
    filter_horizontal = ["surveys"]
    readonly_fields = ["created_at"]
    date_hierarchy = "date"


@admin.register(SurveyReport)
class SurveyReportAdmin(admin.ModelAdmin):
    list_display = [
        "survey",
        "actual_area",
        "difficulty_level",
        "is_ready_for_assignment",
        "created_at",
    ]
    list_filter = ["difficulty_level", "is_ready_for_assignment", "created_at"]
    search_fields = ["survey__project__title", "survey__project__customer__name"]
    raw_id_fields = ["survey"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "基本情報",
            {
                "fields": (
                    "survey",
                    "actual_area",
                    "estimated_work_days",
                    "difficulty_level",
                )
            },
        ),
        (
            "現場状態",
            {
                "fields": (
                    "wall_condition",
                    "floor_condition",
                    "ceiling_condition",
                    "electrical_condition",
                )
            },
        ),
        (
            "環境情報",
            {"fields": ("room_temperature", "humidity_level", "ventilation_quality")},
        ),
        ("アクセス・要件", {"fields": ("access_notes", "special_requirements")}),
        ("メモ", {"fields": ("surveyor_notes", "assignment_notes", "voice_memo_url")}),
        ("完了状況", {"fields": ("is_ready_for_assignment",), "classes": ("collapse",)}),
        ("システム情報", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("survey", "survey__project", "survey__project__customer")
        )


@admin.register(SurveyPhoto)
class SurveyPhotoAdmin(admin.ModelAdmin):
    list_display = ["survey_report", "location", "description", "created_at"]
    list_filter = ["location", "created_at", "is_before"]
    search_fields = ["survey_report__survey__project__title", "description"]
    readonly_fields = ["created_at"]

    fieldsets = (
        ("基本情報", {"fields": ("survey_report", "photo", "location", "is_before")}),
        ("詳細", {"fields": ("description", "upload_order")}),
        ("位置情報", {"fields": ("latitude", "longitude"), "classes": ("collapse",)}),
        ("システム情報", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(WorkerNotification)
class WorkerNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "survey_report",
        "notification_type",
        "status",
        "sent_at",
        "created_at",
    ]
    list_filter = ["notification_type", "status", "sent_at", "created_at"]
    search_fields = [
        "survey_report__survey__project__title",
        "title",
        "recipient_email",
    ]
    raw_id_fields = ["survey_report"]
    readonly_fields = ["sent_at", "read_at", "created_at"]

    fieldsets = (
        ("基本情報", {"fields": ("survey_report", "notification_type", "recipient_email")}),
        ("メッセージ", {"fields": ("title", "message")}),
        ("送信状況", {"fields": ("status", "sent_at", "read_at")}),
        ("システム情報", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(SurveyTemplate)
class SurveyTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "project_type", "is_active", "created_at"]
    list_filter = ["project_type", "is_active", "created_at"]
    search_fields = ["name"]

    fieldsets = (
        ("基本情報", {"fields": ("name", "project_type", "is_active")}),
        (
            "テンプレート設定",
            {"fields": ("default_photos", "checklist_items", "estimated_duration")},
        ),
        ("システム情報", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


# 資材管理のAdmin登録
from .models import Supplier, MaterialOrder


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "contact_person",
        "phone",
        "email",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "specialties", "created_at"]
    search_fields = ["name", "contact_person", "phone", "email"]
    filter_horizontal = ["specialties"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(MaterialOrder)
class MaterialOrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "project",
        "supplier",
        "ordered_by",
        "estimated_cost",
        "status",
        "delivery_date",
        "order_date",
    ]
    list_filter = ["status", "order_date", "delivery_date", "supplier"]
    search_fields = [
        "order_number",
        "project__title",
        "supplier__name",
        "ordered_by__username",
    ]
    raw_id_fields = ["project", "supplier", "ordered_by"]
    readonly_fields = ["order_number", "created_at", "updated_at"]
    date_hierarchy = "order_date"
