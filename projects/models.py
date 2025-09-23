from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name="顧客名")
    phone = models.CharField(max_length=20, verbose_name="電話番号")
    email = models.EmailField(blank=True, verbose_name="メールアドレス")
    address = models.TextField(blank=True, verbose_name="住所")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "顧客"
        verbose_name_plural = "顧客"

    def __str__(self):
        return self.name


class ProjectType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="工種名")
    description = models.TextField(blank=True, verbose_name="説明")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        verbose_name = "工種"
        verbose_name_plural = "工種"

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ("draft", "下書き"),
        ("confirmed", "確定"),
        ("in_progress", "作業中"),
        ("completed", "完了"),
        ("cancelled", "キャンセル"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="顧客")
    project_type = models.ForeignKey(
        ProjectType, on_delete=models.CASCADE, verbose_name="工種"
    )
    title = models.CharField(max_length=200, verbose_name="案件名")
    address = models.TextField(verbose_name="作業場所")
    start_date = models.DateField(verbose_name="開始予定日")
    end_date = models.DateField(verbose_name="終了予定日")
    amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="金額")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="ステータス"
    )
    requires_survey = models.BooleanField(default=False, verbose_name="現調必要")
    details = models.JSONField(default=dict, blank=True, verbose_name="詳細情報")
    notes = models.TextField(blank=True, verbose_name="備考")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "案件"
        verbose_name_plural = "案件"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.customer.name}"

    @property
    def formatted_amount(self):
        return f"{self.amount:,}円"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

    def get_workflow_progress(self):
        """
        ワークフロー進捗を計算
        1. 案件登録 → 2. 調査予定作成 → 3. 調査員アサイン → 4. 調査実行 → 5. 調査完了 → 6. 職人アサイン準備
        """
        stages = [
            {
                "name": "案件登録",
                "description": "案件の基本情報登録",
                "completed": True,  # プロジェクトが存在する時点で完了
                "icon": "fas fa-plus-circle",
                "color": "success",
            },
            {
                "name": "調査予定作成",
                "description": "現地調査の予定作成",
                "completed": self.requires_survey and hasattr(self, "survey"),
                "icon": "fas fa-calendar-plus",
                "color": "info",
            },
            {
                "name": "調査員アサイン",
                "description": "調査員の割り当て",
                "completed": (
                    self.requires_survey
                    and hasattr(self, "survey")
                    and self.survey.surveyor is not None
                )
                if self.requires_survey
                else True,  # 調査不要の場合はスキップ
                "icon": "fas fa-user-check",
                "color": "warning",
            },
            {
                "name": "調査実行",
                "description": "現地調査の実施",
                "completed": (
                    self.requires_survey
                    and hasattr(self, "survey")
                    and self.survey.status in ["in_progress", "completed"]
                )
                if self.requires_survey
                else True,  # 調査不要の場合はスキップ
                "icon": "fas fa-search",
                "color": "primary",
            },
            {
                "name": "調査完了",
                "description": "調査結果の確定",
                "completed": (
                    self.requires_survey
                    and hasattr(self, "survey")
                    and self.survey.status == "completed"
                    and self.survey.is_survey_completed
                )
                if self.requires_survey
                else True,  # 調査不要の場合はスキップ
                "icon": "fas fa-clipboard-check",
                "color": "success",
            },
            {
                "name": "職人アサイン準備",
                "description": "職人アサインの準備完了",
                "completed": self.status in ["confirmed", "in_progress", "completed"],
                "icon": "fas fa-hard-hat",
                "color": "dark",
            },
        ]

        # 進捗率計算
        completed_stages = sum(1 for stage in stages if stage["completed"])
        total_stages = len(stages)
        progress_percentage = int((completed_stages / total_stages) * 100)

        # 現在のステージ特定
        current_stage_index = (
            completed_stages if completed_stages < total_stages else total_stages - 1
        )

        return {
            "stages": stages,
            "completed_stages": completed_stages,
            "total_stages": total_stages,
            "progress_percentage": progress_percentage,
            "current_stage_index": current_stage_index,
            "current_stage": stages[current_stage_index]
            if current_stage_index < total_stages
            else stages[-1],
            "is_complete": completed_stages == total_stages,
        }


class Worker(models.Model):
    name = models.CharField(max_length=100, verbose_name="作業員名")
    phone = models.CharField(max_length=20, verbose_name="電話番号")
    email = models.EmailField(blank=True, verbose_name="メールアドレス")
    skills = models.ManyToManyField(ProjectType, blank=True, verbose_name="対応可能工種")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=0, verbose_name="時給")
    is_active = models.BooleanField(default=True, verbose_name="稼働可能")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        verbose_name = "作業員"
        verbose_name_plural = "作業員"

    def __str__(self):
        return self.name


class ProjectAssignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="案件")
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name="作業員")
    assigned_date = models.DateTimeField(default=timezone.now, verbose_name="アサイン日時")
    is_confirmed = models.BooleanField(default=False, verbose_name="確定")

    class Meta:
        verbose_name = "作業員アサイン"
        verbose_name_plural = "作業員アサイン"
        unique_together = ["project", "worker"]

    def __str__(self):
        return f"{self.project.title} - {self.worker.name}"


class Surveyor(models.Model):
    name = models.CharField(max_length=50, verbose_name="調査員名")
    phone = models.CharField(max_length=20, verbose_name="電話番号")
    email = models.EmailField(blank=True, verbose_name="メールアドレス")
    is_active = models.BooleanField(default=True, verbose_name="稼働可能")
    base_location = models.CharField(max_length=100, blank=True, verbose_name="拠点")
    daily_capacity = models.IntegerField(default=3, verbose_name="1日最大件数")
    work_start_time = models.TimeField(default="09:00", verbose_name="開始時刻")
    work_end_time = models.TimeField(default="17:00", verbose_name="終了時刻")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        verbose_name = "調査員"
        verbose_name_plural = "調査員"

    def __str__(self):
        return self.name

    @property
    def daily_work_hours(self):
        start = timezone.datetime.combine(
            timezone.datetime.today(), self.work_start_time
        )
        end = timezone.datetime.combine(timezone.datetime.today(), self.work_end_time)
        return (end - start).seconds // 3600


class Survey(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "予定"),
        ("in_progress", "調査中"),
        ("completed", "完了"),
        ("cancelled", "キャンセル"),
        ("rescheduled", "再調整"),
    ]

    PRIORITY_CHOICES = [
        ("low", "低"),
        ("normal", "通常"),
        ("high", "高"),
        ("urgent", "緊急"),
    ]

    project = models.OneToOneField(Project, on_delete=models.CASCADE, verbose_name="案件")
    surveyor = models.ForeignKey(
        Surveyor, on_delete=models.CASCADE, verbose_name="調査員", null=True, blank=True
    )
    scheduled_date = models.DateTimeField(verbose_name="予定日時", null=True, blank=True)
    actual_start_time = models.DateTimeField(
        verbose_name="実際の開始時刻", null=True, blank=True
    )
    actual_end_time = models.DateTimeField(
        verbose_name="実際の終了時刻", null=True, blank=True
    )
    estimated_duration = models.IntegerField(default=120, verbose_name="想定時間（分）")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled", verbose_name="ステータス"
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="normal", verbose_name="優先度"
    )
    notes = models.TextField(blank=True, verbose_name="備考")
    access_info = models.TextField(blank=True, verbose_name="現場アクセス情報")

    # 調査結果
    is_survey_completed = models.BooleanField(default=False, verbose_name="調査完了")
    site_condition = models.TextField(blank=True, verbose_name="現場状況")
    customer_requirements = models.TextField(blank=True, verbose_name="顧客要望")
    technical_notes = models.TextField(blank=True, verbose_name="技術メモ")
    additional_work_needed = models.BooleanField(default=False, verbose_name="追加作業要否")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "現地調査"
        verbose_name_plural = "現地調査"
        ordering = ["scheduled_date"]

    def __str__(self):
        return (
            f"{self.project.title} - {self.surveyor.name if self.surveyor else '未アサイン'}"
        )

    @property
    def is_scheduled(self):
        return self.scheduled_date is not None and self.surveyor is not None

    @property
    def duration_actual(self):
        if self.actual_start_time and self.actual_end_time:
            return (self.actual_end_time - self.actual_start_time).seconds // 60
        return None

    @property
    def is_overdue(self):
        if self.scheduled_date and self.status == "scheduled":
            return timezone.now() > self.scheduled_date
        return False

    def save(self, *args, **kwargs):
        # 調査完了時に案件ステータスを更新
        if self.is_survey_completed and self.project.status == "confirmed":
            self.project.status = "in_progress"
            self.project.save()
        super().save(*args, **kwargs)


class SurveyAvailability(models.Model):
    """調査員の稼働可能時間"""

    surveyor = models.ForeignKey(Surveyor, on_delete=models.CASCADE, verbose_name="調査員")
    date = models.DateField(verbose_name="日付")
    start_time = models.TimeField(verbose_name="開始時刻")
    end_time = models.TimeField(verbose_name="終了時刻")
    is_available = models.BooleanField(default=True, verbose_name="稼働可能")
    notes = models.TextField(blank=True, verbose_name="備考")

    class Meta:
        verbose_name = "調査員稼働時間"
        verbose_name_plural = "調査員稼働時間"
        unique_together = ["surveyor", "date"]

    def __str__(self):
        return f"{self.surveyor.name} - {self.date}"


class SurveyRoute(models.Model):
    """調査ルート最適化"""

    date = models.DateField(verbose_name="日付")
    surveyor = models.ForeignKey(Surveyor, on_delete=models.CASCADE, verbose_name="調査員")
    surveys = models.ManyToManyField(Survey, verbose_name="調査案件")
    optimized_order = models.JSONField(default=list, verbose_name="最適化順序")
    total_travel_time = models.IntegerField(default=0, verbose_name="総移動時間（分）")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "調査ルート"
        verbose_name_plural = "調査ルート"
        unique_together = ["date", "surveyor"]

    def __str__(self):
        return f"{self.surveyor.name} - {self.date}"


class SurveyReport(models.Model):
    """調査記録・報告書"""

    CONDITION_CHOICES = [
        ("excellent", "優良"),
        ("good", "良好"),
        ("fair", "普通"),
        ("poor", "不良"),
        ("unknown", "未確認"),
    ]

    survey = models.OneToOneField(Survey, on_delete=models.CASCADE, verbose_name="調査")
    actual_area = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="実測面積（㎡）"
    )
    access_notes = models.TextField(verbose_name="アクセス情報", help_text="駐車場、搬入経路、エレベーター等")
    special_requirements = models.TextField(
        blank=True, verbose_name="特殊要件", help_text="家具移動、養生、時間制約等"
    )
    wall_condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default="good", verbose_name="壁面状態"
    )
    floor_condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default="good", verbose_name="床面状態"
    )
    ceiling_condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default="good", verbose_name="天井状態"
    )
    electrical_condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default="good", verbose_name="電気設備"
    )

    # 作業環境
    room_temperature = models.IntegerField(null=True, blank=True, verbose_name="室温（℃）")
    humidity_level = models.CharField(
        max_length=20,
        choices=[("low", "低"), ("normal", "普通"), ("high", "高")],
        default="normal",
        verbose_name="湿度",
    )
    ventilation_quality = models.CharField(
        max_length=20,
        choices=[("poor", "悪い"), ("fair", "普通"), ("good", "良い")],
        default="fair",
        verbose_name="換気状況",
    )

    # 調査員記録
    surveyor_notes = models.TextField(verbose_name="調査員メモ")
    voice_memo_url = models.URLField(blank=True, verbose_name="音声メモURL")
    estimated_work_days = models.IntegerField(default=1, verbose_name="想定作業日数")
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ("easy", "易"),
            ("normal", "普通"),
            ("hard", "困難"),
            ("very_hard", "非常に困難"),
        ],
        default="normal",
        verbose_name="作業難易度",
    )

    # ステータス
    is_ready_for_assignment = models.BooleanField(
        default=False, verbose_name="職人アサイン準備完了"
    )
    assignment_notes = models.TextField(blank=True, verbose_name="職人選定向けメモ")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "調査記録"
        verbose_name_plural = "調査記録"

    def __str__(self):
        return f"{self.survey.project.title} - 調査記録"

    @property
    def total_photos(self):
        return self.photos.count()

    @property
    def completion_rate(self):
        """調査記録の完成度（%）"""
        completed_fields = 0
        total_fields = 8

        if self.actual_area:
            completed_fields += 1
        if self.access_notes:
            completed_fields += 1
        if self.surveyor_notes:
            completed_fields += 1
        if self.wall_condition != "unknown":
            completed_fields += 1
        if self.floor_condition != "unknown":
            completed_fields += 1
        if self.ceiling_condition != "unknown":
            completed_fields += 1
        if self.electrical_condition != "unknown":
            completed_fields += 1
        if self.total_photos >= 3:
            completed_fields += 1

        return round((completed_fields / total_fields) * 100)


class SurveyPhoto(models.Model):
    """調査写真"""

    LOCATION_CHOICES = [
        ("overview", "全景"),
        ("living", "リビング"),
        ("kitchen", "キッチン"),
        ("bedroom", "寝室"),
        ("bathroom", "バスルーム"),
        ("toilet", "トイレ"),
        ("entrance", "玄関"),
        ("balcony", "ベランダ"),
        ("wall", "壁面詳細"),
        ("ceiling", "天井詳細"),
        ("floor", "床面詳細"),
        ("damage", "損傷箇所"),
        ("electrical", "電気設備"),
        ("plumbing", "配管"),
        ("other", "その他"),
    ]

    survey_report = models.ForeignKey(
        SurveyReport,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="調査記録",
    )
    photo = models.ImageField(upload_to="survey_photos/%Y/%m/%d/", verbose_name="写真")
    description = models.CharField(max_length=200, verbose_name="説明")
    location = models.CharField(
        max_length=20, choices=LOCATION_CHOICES, verbose_name="撮影場所"
    )
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True, verbose_name="緯度"
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="経度"
    )
    is_before = models.BooleanField(default=True, verbose_name="施工前写真")
    upload_order = models.IntegerField(default=0, verbose_name="アップロード順序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="撮影日時")

    class Meta:
        verbose_name = "調査写真"
        verbose_name_plural = "調査写真"
        ordering = ["upload_order", "created_at"]

    def __str__(self):
        return (
            f"{self.survey_report.survey.project.title} - {self.get_location_display()}"
        )

    @property
    def thumbnail_url(self):
        """サムネイルURL（実装時に画像処理ライブラリを使用）"""
        return self.photo.url


class WorkerNotification(models.Model):
    """職人選定担当者への通知"""

    NOTIFICATION_TYPE_CHOICES = [
        ("survey_completed", "調査完了"),
        ("report_ready", "レポート準備完了"),
        ("urgent_assignment", "緊急アサイン要請"),
        ("schedule_change", "スケジュール変更"),
    ]

    STATUS_CHOICES = [
        ("pending", "未読"),
        ("read", "既読"),
        ("responded", "対応済み"),
    ]

    survey_report = models.ForeignKey(
        SurveyReport, on_delete=models.CASCADE, verbose_name="調査記録"
    )
    notification_type = models.CharField(
        max_length=30, choices=NOTIFICATION_TYPE_CHOICES, verbose_name="通知種別"
    )
    title = models.CharField(max_length=200, verbose_name="タイトル")
    message = models.TextField(verbose_name="メッセージ")
    recipient_email = models.EmailField(verbose_name="宛先メール")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="ステータス"
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="送信日時")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="既読日時")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "職人選定通知"
        verbose_name_plural = "職人選定通知"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.survey_report.survey.project.title}"


class SurveyTemplate(models.Model):
    """調査テンプレート"""

    name = models.CharField(max_length=100, verbose_name="テンプレート名")
    project_type = models.ForeignKey(
        ProjectType, on_delete=models.CASCADE, verbose_name="工種"
    )
    default_photos = models.JSONField(default=list, verbose_name="標準撮影箇所")
    checklist_items = models.JSONField(default=list, verbose_name="チェック項目")
    estimated_duration = models.IntegerField(default=120, verbose_name="標準調査時間（分）")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "調査テンプレート"
        verbose_name_plural = "調査テンプレート"

    def __str__(self):
        return f"{self.name} ({self.project_type.name})"


class Craftsman(models.Model):
    """職人"""

    SKILL_LEVEL_CHOICES = [
        (1, "初級"),
        (2, "中級"),
        (3, "上級"),
        (4, "熟練"),
        (5, "マスター"),
    ]

    name = models.CharField(max_length=50, verbose_name="職人名")
    phone = models.CharField(max_length=20, verbose_name="電話番号")
    email = models.EmailField(blank=True, verbose_name="メールアドレス")
    line_id = models.CharField(max_length=50, blank=True, verbose_name="LINE ID")
    specialties = models.ManyToManyField(ProjectType, verbose_name="得意工種")
    skill_level = models.IntegerField(
        choices=SKILL_LEVEL_CHOICES, default=2, verbose_name="技能レベル"
    )
    hourly_rate = models.DecimalField(
        max_digits=6, decimal_places=0, verbose_name="時給（円）"
    )
    coverage_areas = models.TextField(verbose_name="対応エリア", help_text="カンマ区切りで入力")
    is_active = models.BooleanField(default=True, verbose_name="稼働可能")
    bio = models.TextField(blank=True, verbose_name="自己紹介・実績")

    # 評価関連
    total_jobs = models.IntegerField(default=0, verbose_name="総作業件数")
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00, verbose_name="平均評価"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "職人"
        verbose_name_plural = "職人"
        ordering = ["-average_rating", "hourly_rate"]

    def __str__(self):
        return f"{self.name} ({self.get_skill_level_display()})"

    @property
    def coverage_area_list(self):
        """対応エリアをリストで取得"""
        return [area.strip() for area in self.coverage_areas.split(",") if area.strip()]

    @property
    def specialty_names(self):
        """得意工種名をリストで取得"""
        return list(self.specialties.values_list("name", flat=True))

    @property
    def current_workload(self):
        """現在の作業負荷を計算"""
        from django.utils import timezone

        today = timezone.now().date()
        next_week = today + timezone.timedelta(days=7)

        assigned_days = Assignment.objects.filter(
            craftsman=self,
            status__in=["confirmed", "in_progress"],
            project__start_date__range=[today, next_week],
        ).count()

        return min(assigned_days * 20, 100)  # 最大100%

    def can_work_on(self, date, project_type=None):
        """指定日に作業可能かチェック"""
        if not self.is_active:
            return False

        # スケジュール確認
        schedule = CraftsmanSchedule.objects.filter(craftsman=self, date=date).first()

        if schedule and not schedule.is_available:
            return False

        # 既にアサインされているかチェック
        if schedule and schedule.assigned_project:
            return False

        # 工種が指定されている場合、対応可能かチェック
        if project_type and project_type not in self.specialties.all():
            return False

        return True


class CraftsmanSchedule(models.Model):
    """職人スケジュール"""

    craftsman = models.ForeignKey(
        Craftsman, on_delete=models.CASCADE, verbose_name="職人"
    )
    date = models.DateField(verbose_name="日付")
    is_available = models.BooleanField(default=True, verbose_name="稼働可能")
    assigned_project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="アサイン済み案件",
    )
    notes = models.TextField(blank=True, verbose_name="備考")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")

    class Meta:
        verbose_name = "職人スケジュール"
        verbose_name_plural = "職人スケジュール"
        unique_together = ["craftsman", "date"]
        ordering = ["date", "craftsman"]

    def __str__(self):
        status = "稼働可能" if self.is_available else "休み"
        if self.assigned_project:
            status = f"アサイン済み: {self.assigned_project.title}"
        return f"{self.craftsman.name} - {self.date} ({status})"


class Assignment(models.Model):
    """案件アサイン"""

    STATUS_CHOICES = [
        ("inquiry", "打診中"),
        ("confirmed", "確定"),
        ("declined", "辞退"),
        ("in_progress", "作業中"),
        ("completed", "完了"),
        ("cancelled", "キャンセル"),
    ]

    PRIORITY_CHOICES = [
        ("low", "低"),
        ("normal", "通常"),
        ("high", "高"),
        ("urgent", "緊急"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="案件")
    craftsman = models.ForeignKey(
        Craftsman, on_delete=models.CASCADE, verbose_name="職人"
    )
    assigned_by = models.ForeignKey(
        Surveyor, on_delete=models.CASCADE, verbose_name="アサイン担当者"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="inquiry", verbose_name="ステータス"
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="normal", verbose_name="優先度"
    )

    # スケジュール情報
    scheduled_start_date = models.DateField(verbose_name="予定開始日")
    scheduled_end_date = models.DateField(verbose_name="予定終了日")
    estimated_hours = models.IntegerField(verbose_name="想定作業時間")

    # 金額情報
    offered_rate = models.DecimalField(
        max_digits=8, decimal_places=0, verbose_name="提示単価（円）"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="総額（円）"
    )

    # コミュニケーション
    inquiry_message = models.TextField(verbose_name="打診メッセージ")
    response_message = models.TextField(blank=True, verbose_name="返答メッセージ")
    response_date = models.DateTimeField(null=True, blank=True, verbose_name="返答日時")

    # 連絡手段
    contact_method = models.CharField(
        max_length=20,
        choices=[
            ("phone", "電話"),
            ("line", "LINE"),
            ("email", "メール"),
        ],
        default="phone",
        verbose_name="連絡手段",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="打診日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "案件アサイン"
        verbose_name_plural = "案件アサイン"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.title} → {self.craftsman.name} ({self.get_status_display()})"

    @property
    def is_pending(self):
        """打診中かどうか"""
        return self.status == "inquiry"

    @property
    def is_active(self):
        """アクティブな案件かどうか"""
        return self.status in ["confirmed", "in_progress"]

    def calculate_total_amount(self):
        """総額を計算"""
        return self.offered_rate * self.estimated_hours

    def save(self, *args, **kwargs):
        # 総額を自動計算
        if self.offered_rate and self.estimated_hours:
            self.total_amount = self.calculate_total_amount()

        super().save(*args, **kwargs)

        # 確定時にスケジュールを更新
        if self.status == "confirmed":
            self.update_craftsman_schedule()

    def update_craftsman_schedule(self):
        """職人のスケジュールを更新"""
        from django.utils import timezone

        # 予定期間中の日付でスケジュールを作成/更新
        current_date = self.scheduled_start_date
        while current_date <= self.scheduled_end_date:
            schedule, created = CraftsmanSchedule.objects.get_or_create(
                craftsman=self.craftsman,
                date=current_date,
                defaults={"is_available": False, "assigned_project": self.project},
            )
            if not created:
                schedule.is_available = False
                schedule.assigned_project = self.project
                schedule.save()

            current_date += timezone.timedelta(days=1)


class CraftsmanRating(models.Model):
    """職人評価"""

    assignment = models.OneToOneField(
        Assignment, on_delete=models.CASCADE, verbose_name="案件"
    )
    craftsman = models.ForeignKey(
        Craftsman, on_delete=models.CASCADE, verbose_name="職人"
    )
    surveyor = models.ForeignKey(Surveyor, on_delete=models.CASCADE, verbose_name="評価者")

    # 評価項目
    technical_skill = models.IntegerField(
        choices=[(i, f"{i}点") for i in range(1, 6)], verbose_name="技術力"
    )
    punctuality = models.IntegerField(
        choices=[(i, f"{i}点") for i in range(1, 6)], verbose_name="時間厳守"
    )
    communication = models.IntegerField(
        choices=[(i, f"{i}点") for i in range(1, 6)], verbose_name="コミュニケーション"
    )
    work_quality = models.IntegerField(
        choices=[(i, f"{i}点") for i in range(1, 6)], verbose_name="作業品質"
    )

    overall_rating = models.DecimalField(
        max_digits=3, decimal_places=2, verbose_name="総合評価"
    )

    comments = models.TextField(blank=True, verbose_name="コメント")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="評価日時")

    class Meta:
        verbose_name = "職人評価"
        verbose_name_plural = "職人評価"

    def save(self, *args, **kwargs):
        # 総合評価を自動計算
        self.overall_rating = (
            self.technical_skill
            + self.punctuality
            + self.communication
            + self.work_quality
        ) / 4.0

        super().save(*args, **kwargs)

        # 職人の平均評価を更新
        self.update_craftsman_rating()

    def update_craftsman_rating(self):
        """職人の平均評価を更新"""
        from django.db.models import Avg

        avg_rating = CraftsmanRating.objects.filter(craftsman=self.craftsman).aggregate(
            Avg("overall_rating")
        )["overall_rating__avg"]

        self.craftsman.average_rating = avg_rating or 0.00
        self.craftsman.save()


# 資材購入モジュール
class Supplier(models.Model):
    """資材業者"""

    name = models.CharField(max_length=100, verbose_name="業者名")
    contact_person = models.CharField(max_length=50, verbose_name="担当者名")
    phone = models.CharField(max_length=20, verbose_name="電話番号")
    email = models.EmailField(blank=True, verbose_name="メールアドレス")
    address = models.TextField(blank=True, verbose_name="住所")
    specialties = models.ManyToManyField(ProjectType, verbose_name="取扱工種")
    payment_terms = models.CharField(max_length=100, blank=True, verbose_name="支払条件")
    delivery_area = models.TextField(blank=True, verbose_name="配送エリア")
    notes = models.TextField(blank=True, verbose_name="備考")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "資材業者"
        verbose_name_plural = "資材業者"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def specialties_list(self):
        return [specialty.name for specialty in self.specialties.all()]


class MaterialOrder(models.Model):
    """資材発注"""

    ORDER_STATUS_CHOICES = [
        ("draft", "下書き"),
        ("ordered", "発注済"),
        ("delivered", "納品済"),
        ("cancelled", "キャンセル"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name="案件",
        related_name="material_orders",
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="業者")
    ordered_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="発注者")
    order_number = models.CharField(max_length=20, unique=True, verbose_name="発注番号")
    order_details = models.TextField(verbose_name="発注内容")
    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="見積金額"
    )
    actual_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="実際金額"
    )
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="発注日")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="納期")
    actual_delivery_date = models.DateField(null=True, blank=True, verbose_name="実際納期")
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="draft",
        verbose_name="ステータス",
    )
    delivery_address = models.TextField(blank=True, verbose_name="納品先住所")
    contact_person = models.CharField(max_length=50, blank=True, verbose_name="現場担当者")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="現場連絡先")
    notes = models.TextField(blank=True, verbose_name="備考")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "資材発注"
        verbose_name_plural = "資材発注"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_number} - {self.project.title}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            from datetime import datetime

            today = datetime.now()
            count = (
                MaterialOrder.objects.filter(order_date__date=today.date()).count() + 1
            )
            self.order_number = f"ORD{today.strftime('%Y%m%d')}{count:03d}"
        super().save(*args, **kwargs)

    @property
    def formatted_estimated_cost(self):
        if self.estimated_cost:
            return f"¥{self.estimated_cost:,.0f}"
        return "未設定"

    @property
    def formatted_actual_cost(self):
        if self.actual_cost:
            return f"¥{self.actual_cost:,.0f}"
        return "未確定"

    @property
    def is_overdue(self):
        if self.delivery_date and self.status in ["draft", "ordered"]:
            from datetime import date

            return self.delivery_date < date.today()
        return False

    @property
    def days_until_delivery(self):
        if self.delivery_date and self.status in ["draft", "ordered"]:
            from datetime import date

            delta = self.delivery_date - date.today()
            return delta.days
        return None


# マージン設定モジュール
class ProjectCost(models.Model):
    """案件コスト管理"""

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        verbose_name="案件",
        related_name="project_cost",
    )
    craftsman_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="職人費用"
    )
    material_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="資材費"
    )
    transportation_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="交通費"
    )
    survey_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="調査費"
    )
    other_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="その他経費"
    )
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="総コスト"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "案件コスト"
        verbose_name_plural = "案件コスト"

    def __str__(self):
        return f"{self.project.title} - コスト"

    def calculate_total_cost(self):
        """総コストを計算"""
        return (
            self.craftsman_cost
            + self.material_cost
            + self.transportation_cost
            + self.survey_cost
            + self.other_cost
        )

    def save(self, *args, **kwargs):
        # 総コストを自動計算
        self.total_cost = self.calculate_total_cost()
        super().save(*args, **kwargs)

    @property
    def formatted_total_cost(self):
        return f"¥{self.total_cost:,.0f}"

    @property
    def cost_breakdown(self):
        """コスト内訳を辞書で返す"""
        total = self.total_cost
        if total == 0:
            return {}

        return {
            "craftsman": {
                "amount": self.craftsman_cost,
                "percentage": round((self.craftsman_cost / total) * 100, 1),
            },
            "material": {
                "amount": self.material_cost,
                "percentage": round((self.material_cost / total) * 100, 1),
            },
            "transportation": {
                "amount": self.transportation_cost,
                "percentage": round((self.transportation_cost / total) * 100, 1),
            },
            "survey": {
                "amount": self.survey_cost,
                "percentage": round((self.survey_cost / total) * 100, 1),
            },
            "other": {
                "amount": self.other_cost,
                "percentage": round((self.other_cost / total) * 100, 1),
            },
        }


class ProjectPricing(models.Model):
    """案件価格設定"""

    PRICING_STAGE_CHOICES = [
        ("estimate", "見積もり段階"),
        ("contract", "受注段階"),
        ("final", "確定"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name="案件",
        related_name="pricing_history",
    )
    base_cost = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="基準コスト"
    )
    margin_rate = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="マージン率(%)"
    )
    margin_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="マージン金額"
    )
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="最終請求額"
    )
    pricing_stage = models.CharField(
        max_length=20, choices=PRICING_STAGE_CHOICES, verbose_name="価格設定段階"
    )
    set_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="設定者")
    notes = models.TextField(blank=True, verbose_name="備考")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "案件価格設定"
        verbose_name_plural = "案件価格設定"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.title} - {self.get_pricing_stage_display()} ({self.margin_rate}%)"

    def calculate_margin_amount(self):
        """マージン金額を計算"""
        return self.base_cost * (self.margin_rate / 100)

    def calculate_final_price(self):
        """最終価格を計算"""
        return self.base_cost + self.calculate_margin_amount()

    def save(self, *args, **kwargs):
        # マージン金額と最終価格を自動計算
        self.margin_amount = self.calculate_margin_amount()
        self.final_price = self.calculate_final_price()

        # 新しい価格設定が作成される場合、同じ段階の他の設定を無効化
        if self.is_active:
            ProjectPricing.objects.filter(
                project=self.project, pricing_stage=self.pricing_stage, is_active=True
            ).exclude(id=self.id).update(is_active=False)

        super().save(*args, **kwargs)

    @property
    def formatted_base_cost(self):
        return f"¥{self.base_cost:,.0f}"

    @property
    def formatted_margin_amount(self):
        return f"¥{self.margin_amount:,.0f}"

    @property
    def formatted_final_price(self):
        return f"¥{self.final_price:,.0f}"

    @property
    def profit_amount(self):
        """利益額を計算"""
        return self.final_price - self.base_cost

    @property
    def profit_rate(self):
        """利益率を計算"""
        if self.final_price == 0:
            return 0
        return round((self.profit_amount / self.final_price) * 100, 2)

    @classmethod
    def get_current_pricing(cls, project, stage="final"):
        """現在有効な価格設定を取得"""
        return cls.objects.filter(
            project=project, pricing_stage=stage, is_active=True
        ).first()

    @classmethod
    def get_recommended_margin_range(cls, project_type=None):
        """推奨マージン率の範囲を取得"""
        # プロジェクトタイプ別の推奨マージン率
        recommendations = {
            "cleaning": {"min": 25, "max": 35, "standard": 30},
            "renovation": {"min": 20, "max": 30, "standard": 25},
            "cross": {"min": 15, "max": 25, "standard": 20},
            "default": {"min": 20, "max": 30, "standard": 25},
        }

        if project_type and hasattr(project_type, "name"):
            type_name = project_type.name.lower()
            for key in recommendations:
                if key in type_name:
                    return recommendations[key]

        return recommendations["default"]


class PricingAuditLog(models.Model):
    """価格設定変更履歴"""

    pricing = models.ForeignKey(
        ProjectPricing,
        on_delete=models.CASCADE,
        verbose_name="価格設定",
        related_name="audit_logs",
    )
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="変更者")
    change_type = models.CharField(
        max_length=20,
        choices=[
            ("created", "作成"),
            ("updated", "更新"),
            ("deactivated", "無効化"),
        ],
        verbose_name="変更種別",
    )
    old_values = models.JSONField(default=dict, verbose_name="変更前値")
    new_values = models.JSONField(default=dict, verbose_name="変更後値")
    reason = models.TextField(blank=True, verbose_name="変更理由")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="変更日時")

    class Meta:
        verbose_name = "価格設定変更履歴"
        verbose_name_plural = "価格設定変更履歴"

    def __str__(self):
        return f"{self.pricing.project.title} - {self.get_change_type_display()}"


# 施工管理モデル
class ConstructionProgress(models.Model):
    """施工進捗"""

    REPORT_METHOD_CHOICES = [
        ("line", "LINE"),
        ("phone", "電話"),
        ("direct", "直接入力"),
        ("email", "メール"),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="construction_progress"
    )
    craftsman = models.ForeignKey(
        Craftsman, on_delete=models.CASCADE, related_name="progress_reports"
    )
    report_date = models.DateTimeField(auto_now_add=True)
    progress_rate = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="進捗率（0-100%）",
    )
    work_description = models.TextField(verbose_name="作業内容")
    issues = models.TextField(blank=True, verbose_name="問題・課題")
    next_plan = models.TextField(blank=True, verbose_name="翌日予定")
    reported_by = models.CharField(
        max_length=20,
        choices=REPORT_METHOD_CHOICES,
        default="direct",
        verbose_name="報告手段",
    )
    weather = models.CharField(max_length=50, blank=True, verbose_name="天候")
    worker_count = models.IntegerField(default=1, verbose_name="作業人数")
    start_time = models.TimeField(null=True, blank=True, verbose_name="開始時刻")
    end_time = models.TimeField(null=True, blank=True, verbose_name="終了時刻")
    additional_items = models.JSONField(default=dict, blank=True, verbose_name="追加項目")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date"]
        verbose_name = "施工進捗"
        verbose_name_plural = "施工進捗"

    def __str__(self):
        return f"{self.project.title} - {self.progress_rate}% ({self.report_date.strftime('%m/%d')})"

    @property
    def is_delayed(self):
        """進捗遅れかどうかを判定"""
        from datetime import date

        if not self.project.start_date or not self.project.end_date:
            return False

        total_days = (self.project.end_date - self.project.start_date).days
        if total_days <= 0:
            return False

        elapsed_days = (date.today() - self.project.start_date).days
        expected_progress = min(100, (elapsed_days / total_days) * 100)

        return self.progress_rate < expected_progress - 10  # 10%以上の遅れ

    @property
    def has_issues(self):
        """問題があるかどうか"""
        return bool(self.issues.strip())

    @property
    def working_hours(self):
        """作業時間を計算"""
        if self.start_time and self.end_time:
            from datetime import datetime, timedelta

            start = datetime.combine(datetime.today().date(), self.start_time)
            end = datetime.combine(datetime.today().date(), self.end_time)
            if end < start:
                end += timedelta(days=1)
            return (end - start).total_seconds() / 3600
        return None


class ProgressPhoto(models.Model):
    """進捗写真"""

    PHOTO_TYPE_CHOICES = [
        ("before", "施工前"),
        ("during", "施工中"),
        ("after", "完了"),
        ("issue", "問題箇所"),
        ("safety", "安全対策"),
        ("materials", "資材状況"),
    ]

    progress = models.ForeignKey(
        ConstructionProgress, on_delete=models.CASCADE, related_name="photos"
    )
    photo = models.ImageField(upload_to="construction_photos/%Y/%m/")
    description = models.CharField(max_length=100, verbose_name="写真説明")
    photo_type = models.CharField(
        max_length=20, choices=PHOTO_TYPE_CHOICES, default="during", verbose_name="写真種別"
    )
    taken_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-taken_at"]
        verbose_name = "進捗写真"
        verbose_name_plural = "進捗写真"

    def __str__(self):
        return f"{self.progress.project.title} - {self.get_photo_type_display()}"


class ProjectIssue(models.Model):
    """プロジェクト問題管理"""

    ISSUE_TYPE_CHOICES = [
        ("additional_work", "追加工事"),
        ("quality", "品質問題"),
        ("complaint", "顧客クレーム"),
        ("delay", "工期遅れ"),
        ("safety", "安全問題"),
        ("materials", "資材問題"),
        ("weather", "天候問題"),
        ("other", "その他"),
    ]

    STATUS_CHOICES = [
        ("open", "対応中"),
        ("in_progress", "作業中"),
        ("resolved", "解決済"),
        ("escalated", "エスカレーション"),
        ("closed", "クローズ"),
    ]

    PRIORITY_CHOICES = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
        ("critical", "緊急"),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues"
    )
    issue_type = models.CharField(
        max_length=20, choices=ISSUE_TYPE_CHOICES, verbose_name="問題種別"
    )
    title = models.CharField(max_length=100, verbose_name="問題タイトル")
    description = models.TextField(verbose_name="詳細説明")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium", verbose_name="優先度"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open", verbose_name="対応状況"
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reported_issues",
        verbose_name="報告者",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
        verbose_name="担当者",
    )
    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="追加費用見込み"
    )
    resolution = models.TextField(blank=True, verbose_name="解決内容")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "プロジェクト問題"
        verbose_name_plural = "プロジェクト問題"

    def __str__(self):
        return f"{self.project.title} - {self.title}"

    @property
    def is_overdue(self):
        """対応期限を過ぎているかどうか"""
        from datetime import datetime, timedelta

        if self.status in ["resolved", "closed"]:
            return False

        days_open = (datetime.now().date() - self.created_at.date()).days

        if self.priority == "critical":
            return days_open > 1
        elif self.priority == "high":
            return days_open > 3
        elif self.priority == "medium":
            return days_open > 7
        else:
            return days_open > 14

    def save(self, *args, **kwargs):
        if self.status == "resolved" and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)


class ProjectCompletion(models.Model):
    """プロジェクト完了管理"""

    COMPLETION_STATUS_CHOICES = [
        ("in_progress", "施工中"),
        ("completed", "完了"),
        ("customer_check", "顧客確認中"),
        ("approved", "承認済"),
        ("payment_pending", "支払い待ち"),
        ("closed", "クローズ"),
    ]

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="completion"
    )
    completion_date = models.DateField(null=True, blank=True, verbose_name="完了日")
    customer_check_date = models.DateField(null=True, blank=True, verbose_name="顧客確認日")
    approval_date = models.DateField(null=True, blank=True, verbose_name="承認日")
    final_photos_submitted = models.BooleanField(default=False, verbose_name="完了写真提出済み")
    customer_signature = models.BooleanField(default=False, verbose_name="顧客サイン済み")
    payment_processed = models.BooleanField(default=False, verbose_name="支払い処理済み")
    completion_notes = models.TextField(blank=True, verbose_name="完了備考")
    status = models.CharField(
        max_length=20,
        choices=COMPLETION_STATUS_CHOICES,
        default="in_progress",
        verbose_name="完了ステータス",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "プロジェクト完了"
        verbose_name_plural = "プロジェクト完了"

    def __str__(self):
        return f"{self.project.title} - {self.get_status_display()}"

    @property
    def completion_percentage(self):
        """完了チェック項目の達成率"""
        total_items = 5
        completed_items = sum(
            [
                self.final_photos_submitted,
                self.customer_signature,
                self.payment_processed,
                bool(self.completion_date),
                bool(self.customer_check_date),
            ]
        )
        return (completed_items / total_items) * 100


class ProjectEditSession(models.Model):
    """プロジェクト編集セッション（一時保存）"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="edit_sessions"
    )
    session_id = models.CharField(max_length=64, verbose_name="セッションID")
    user_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="ユーザーID")
    additional_items = models.JSONField(default=dict, blank=True, verbose_name="追加項目")
    edit_mode = models.BooleanField(default=False, verbose_name="編集モード")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="最終アクティビティ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "プロジェクト編集セッション"
        verbose_name_plural = "プロジェクト編集セッション"
        unique_together = ["project", "session_id"]
        ordering = ["-last_activity"]

    def __str__(self):
        return f"{self.project.title} - セッション{self.session_id[:8]}"

    @property
    def is_expired(self):
        """セッション期限切れかどうか（1時間）"""
        from datetime import timedelta
        return timezone.now() - self.last_activity > timedelta(hours=1)

    @classmethod
    def cleanup_expired_sessions(cls):
        """期限切れセッションをクリーンアップ"""
        from datetime import timedelta
        cutoff_time = timezone.now() - timedelta(hours=1)
        return cls.objects.filter(last_activity__lt=cutoff_time).delete()

    def save_additional_item(self, key, value):
        """追加項目を保存"""
        if not self.additional_items:
            self.additional_items = {}
        self.additional_items[key] = value
        self.save()

    def remove_additional_item(self, key):
        """追加項目を削除"""
        if self.additional_items and key in self.additional_items:
            del self.additional_items[key]
            self.save()

    def get_additional_items_list(self):
        """追加項目をリスト形式で取得"""
        return [{"key": k, "value": v} for k, v in (self.additional_items or {}).items()]
