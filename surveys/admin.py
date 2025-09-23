from django.contrib import admin
from .models import Survey, SurveyRoom, SurveyWall, SurveyDamage, SurveyPhoto, Surveyor


class SurveyRoomInline(admin.TabularInline):
    model = SurveyRoom
    extra = 1


class SurveyWallInline(admin.TabularInline):
    model = SurveyWall
    extra = 1


class SurveyDamageInline(admin.TabularInline):
    model = SurveyDamage
    extra = 1


class SurveyPhotoInline(admin.TabularInline):
    model = SurveyPhoto
    extra = 1


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['project', 'surveyor', 'scheduled_date', 'scheduled_start_time', 'status', 'get_progress_percentage']
    list_filter = ['status', 'scheduled_date', 'surveyor']
    search_fields = ['project__name', 'surveyor__username', 'surveyor__first_name', 'surveyor__last_name']
    date_hierarchy = 'scheduled_date'
    inlines = [SurveyRoomInline, SurveyDamageInline, SurveyPhotoInline]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'surveyor', 'status')
        }),
        ('スケジュール', {
            'fields': ('scheduled_date', 'scheduled_start_time', 'estimated_duration')
        }),
        ('実績', {
            'fields': ('actual_start_time', 'actual_end_time'),
            'classes': ('collapse',)
        }),
        ('備考', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('メタ情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(SurveyRoom)
class SurveyRoomAdmin(admin.ModelAdmin):
    list_display = ['survey', 'room_name', 'created_at']
    list_filter = ['survey__status', 'created_at']
    search_fields = ['room_name', 'survey__project__name']
    inlines = [SurveyWallInline]


@admin.register(SurveyWall)
class SurveyWallAdmin(admin.ModelAdmin):
    list_display = ['room', 'direction', 'length', 'height', 'foundation_type', 'foundation_condition']
    list_filter = ['direction', 'foundation_type', 'foundation_condition']
    search_fields = ['room__room_name', 'room__survey__project__name']


@admin.register(SurveyDamage)
class SurveyDamageAdmin(admin.ModelAdmin):
    list_display = ['survey', 'damage_type', 'has_dents', 'dent_count']
    list_filter = ['damage_type', 'has_dents']
    search_fields = ['survey__project__name', 'description']


@admin.register(SurveyPhoto)
class SurveyPhotoAdmin(admin.ModelAdmin):
    list_display = ['survey', 'photo_type', 'caption', 'uploaded_at']
    list_filter = ['photo_type', 'uploaded_at']
    search_fields = ['survey__project__name', 'caption']
    readonly_fields = ['uploaded_at']


@admin.register(Surveyor)
class SurveyorAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_id', 'user', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'employee_id', 'email', 'phone', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'employee_id', 'user')
        }),
        ('連絡先情報', {
            'fields': ('email', 'phone')
        }),
        ('ステータス', {
            'fields': ('is_active',)
        }),
        ('メタ情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 調査員の変更があった場合のログ
        if not change:
            self.message_user(request, f'調査員「{obj.name}」を作成しました。')
        else:
            self.message_user(request, f'調査員「{obj.name}」を更新しました。')
