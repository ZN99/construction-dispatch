from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from order_management.models import Project
from django.utils import timezone


class Surveyor(models.Model):
    """調査員マスター"""
    name = models.CharField(max_length=100, verbose_name='調査員名')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='社員番号')
    email = models.EmailField(blank=True, verbose_name='メールアドレス')
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話番号')
    department = models.CharField(max_length=50, blank=True, verbose_name='所属部署')

    # 専門分野
    specialties = models.TextField(blank=True, verbose_name='専門分野')

    # 資格情報
    certifications = models.TextField(blank=True, verbose_name='保有資格')

    # 勤務状況
    is_active = models.BooleanField(default=True, verbose_name='稼働中')
    hire_date = models.DateField(null=True, blank=True, verbose_name='入社日')

    # 経験年数
    experience_years = models.IntegerField(default=0, verbose_name='調査経験年数')

    # 関連付けられたユーザー（オプション）
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='surveyor_profile', verbose_name='ユーザーアカウント')

    # メタ情報
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='登録日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    notes = models.TextField(blank=True, verbose_name='備考')

    class Meta:
        verbose_name = '調査員'
        verbose_name_plural = '調査員一覧'
        ordering = ['-is_active', 'name']

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    def get_full_display_name(self):
        """フルネーム表示"""
        return f"{self.name} ({self.employee_id})"

    def get_status_display(self):
        """稼働状況の表示"""
        return "稼働中" if self.is_active else "休止中"

    def get_specialties_list(self):
        """専門分野をリスト形式で取得"""
        if self.specialties:
            return [s.strip() for s in self.specialties.split(',') if s.strip()]
        return []

    def get_certifications_list(self):
        """資格をリスト形式で取得"""
        if self.certifications:
            return [c.strip() for c in self.certifications.split(',') if c.strip()]
        return []

    def get_current_surveys_count(self):
        """現在進行中の調査数"""
        return self.assigned_surveys.filter(status__in=['scheduled', 'in_progress']).count()

    def get_completed_surveys_count(self):
        """完了した調査数"""
        return self.assigned_surveys.filter(status='completed').count()

    def get_experience_level(self):
        """経験レベルの判定"""
        if self.experience_years >= 10:
            return "シニア"
        elif self.experience_years >= 5:
            return "中級"
        elif self.experience_years >= 2:
            return "初級"
        else:
            return "新人"


class Survey(models.Model):
    """現地調査のメインモデル"""
    STATUS_CHOICES = [
        ('scheduled', '予定'),
        ('in_progress', '進行中'),
        ('completed', '完了'),
        ('pending_approval', '承認待ち'),
        ('approved', '承認済み'),
        ('rejected', '差し戻し'),
        ('cancelled', 'キャンセル'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='案件')
    surveyor = models.ForeignKey(Surveyor, on_delete=models.CASCADE, verbose_name='調査員', related_name='assigned_surveys')
    scheduled_date = models.DateField(verbose_name='予定日')
    scheduled_start_time = models.TimeField(verbose_name='開始予定時刻')
    estimated_duration = models.IntegerField(verbose_name='予定所要時間（分）', default=120)

    # 実際の調査時間
    actual_start_time = models.DateTimeField(null=True, blank=True, verbose_name='実際の開始時刻')
    actual_end_time = models.DateTimeField(null=True, blank=True, verbose_name='実際の終了時刻')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name='ステータス')

    # 承認関連
    approved_by = models.CharField(max_length=100, blank=True, verbose_name='承認者')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='承認日時')
    approval_notes = models.TextField(blank=True, verbose_name='承認コメント')

    # メタ情報
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    notes = models.TextField(blank=True, verbose_name='備考')

    class Meta:
        verbose_name = '現地調査'
        verbose_name_plural = '現地調査'
        ordering = ['-scheduled_date', '-scheduled_start_time']

    def __str__(self):
        return f"{self.project.site_name} - {self.surveyor.name}"

    def get_absolute_url(self):
        return reverse('surveys:survey_detail', kwargs={'pk': self.pk})

    def get_progress_percentage(self):
        """進捗率を計算"""
        if self.status == 'approved':
            return 100
        elif self.status == 'pending_approval':
            return 90
        elif self.status == 'completed':
            return 80
        elif self.status == 'in_progress':
            return 60
        elif self.status == 'rejected':
            return 50
        return 0

    def get_actual_duration_minutes(self):
        """実際の所要時間（分）を計算"""
        if self.actual_start_time and self.actual_end_time:
            delta = self.actual_end_time - self.actual_start_time
            return int(delta.total_seconds() / 60)

    def needs_approval(self):
        """承認が必要かどうか"""
        return self.status == 'pending_approval'

    def is_approved(self):
        """承認済みかどうか"""
        return self.status == 'approved'

    def is_rejected(self):
        """差し戻しかどうか"""
        return self.status == 'rejected'

    def can_be_approved(self):
        """承認可能かどうか"""
        return self.status in ['pending_approval', 'completed']

    def approve(self, approved_by, approval_notes=''):
        """調査を承認する"""
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.approval_notes = approval_notes
        self.save()

    def reject(self, approved_by, approval_notes=''):
        """調査を差し戻す"""
        self.status = 'rejected'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.approval_notes = approval_notes
        self.save()

    def submit_for_approval(self):
        """承認待ちステータスにする"""
        if self.status == 'completed':
            self.status = 'pending_approval'
            self.save()
        return None

    def get_estimated_end_time(self):
        """予定終了時刻を計算"""
        from datetime import datetime, timedelta
        start_datetime = datetime.combine(self.scheduled_date, self.scheduled_start_time)
        end_datetime = start_datetime + timedelta(minutes=self.estimated_duration)
        return end_datetime.time()

    def get_total_wall_count(self):
        """全体の壁面数を計算"""
        total = 0
        for room in self.rooms.all():
            total += room.walls.count()
        return total

    def get_damage_summary(self):
        """損傷種別ごとの集計を取得"""
        damages = self.damages.all()
        summary = {}
        for damage in damages:
            damage_type_display = damage.get_damage_type_display()
            if damage_type_display in summary:
                summary[damage_type_display] += 1
            else:
                summary[damage_type_display] = 1
        return summary


class SurveyRoom(models.Model):
    """調査対象の部屋"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='rooms', verbose_name='調査')
    room_name = models.CharField(max_length=100, verbose_name='部屋名')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '調査部屋'
        verbose_name_plural = '調査部屋'

    def __str__(self):
        return f"{self.survey} - {self.room_name}"


class SurveyWall(models.Model):
    """壁面調査データ"""
    WALL_DIRECTION_CHOICES = [
        ('north', '北壁'),
        ('south', '南壁'),
        ('east', '東壁'),
        ('west', '西壁'),
        ('ceiling', '天井'),
    ]

    FOUNDATION_TYPE_CHOICES = [
        ('gypsum_board', '石膏ボード'),
        ('concrete', 'コンクリート'),
        ('plywood', '合板'),
        ('other', 'その他'),
    ]

    FOUNDATION_CONDITION_CHOICES = [
        ('good', '良好'),
        ('needs_repair', '補修必要'),
    ]

    room = models.ForeignKey(SurveyRoom, on_delete=models.CASCADE, related_name='walls', verbose_name='部屋')
    direction = models.CharField(max_length=20, choices=WALL_DIRECTION_CHOICES, verbose_name='壁面方向')
    length = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='長さ(m)')
    height = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='高さ(m)')
    opening_area = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='開口部面積(㎡)')
    foundation_type = models.CharField(max_length=20, choices=FOUNDATION_TYPE_CHOICES, verbose_name='下地種別')
    foundation_condition = models.CharField(max_length=20, choices=FOUNDATION_CONDITION_CHOICES, verbose_name='下地状態')

    class Meta:
        verbose_name = '壁面調査'
        verbose_name_plural = '壁面調査'

    def __str__(self):
        return f"{self.room} - {self.get_direction_display()}"

    def calculate_area(self):
        """壁面面積を計算（開口部を除く）"""
        total_area = float(self.length) * float(self.height)
        return max(0, total_area - float(self.opening_area))


class SurveyDamage(models.Model):
    """損傷状況調査"""
    DAMAGE_TYPES = [
        ('stain_discoloration', '汚れ・変色'),
        ('tear_peel', '破れ・剥がれ'),
        ('nail_holes', '釘穴・画鋲穴'),
        ('large_holes', '大きな穴・ネジ穴'),
        ('mold_stain', 'カビ・水染み'),
        ('tobacco_stain', 'タバコヤニ'),
        ('oil_stain', '油汚れ'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='damages', verbose_name='調査')
    damage_type = models.CharField(max_length=30, choices=DAMAGE_TYPES, verbose_name='損傷種別')
    has_dents = models.BooleanField(default=False, verbose_name='凹みあり')
    dent_count = models.IntegerField(default=0, verbose_name='凹み個数')
    description = models.TextField(blank=True, verbose_name='詳細説明')

    class Meta:
        verbose_name = '損傷調査'
        verbose_name_plural = '損傷調査'

    def __str__(self):
        return f"{self.survey} - {self.get_damage_type_display()}"


class SurveyPhoto(models.Model):
    """調査写真"""
    PHOTO_TYPES = [
        ('room_overview', '部屋全景'),
        ('damage_detail', '損傷箇所'),
        ('dent_detail', '凹み詳細'),
        ('wall_condition', '壁面状態'),
        ('measurement_reference', '測定参考'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='photos', verbose_name='調査')
    wall = models.ForeignKey(SurveyWall, on_delete=models.CASCADE, null=True, blank=True, verbose_name='対象壁面')
    photo_type = models.CharField(max_length=30, choices=PHOTO_TYPES, verbose_name='写真種別')
    image = models.ImageField(upload_to='survey_photos/%Y/%m/%d/', verbose_name='写真')
    caption = models.CharField(max_length=200, blank=True, verbose_name='キャプション')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='アップロード日時')

    class Meta:
        verbose_name = '調査写真'
        verbose_name_plural = '調査写真'

    def __str__(self):
        return f"{self.survey} - {self.get_photo_type_display()}"


class SurveyWorkflowStep(models.Model):
    """調査ワークフローステップ定義"""
    STEP_TYPES = [
        ('survey_overview', '調査概要'),
        ('room_setup', '部屋・壁面管理'),
        ('wall_measurement', '壁面測定'),
        ('condition_check', '状態確認'),
        ('photo_capture', '写真撮影'),
        ('damage_assessment', '損傷評価'),
        ('completion_check', '完了確認'),
    ]

    step_type = models.CharField(max_length=20, choices=STEP_TYPES, verbose_name='ステップ種別')
    step_number = models.IntegerField(verbose_name='ステップ番号')
    title = models.CharField(max_length=100, verbose_name='ステップタイトル')
    description = models.TextField(verbose_name='説明')
    instruction_html = models.TextField(blank=True, verbose_name='詳細手順（HTML）')
    required_photos = models.IntegerField(default=0, verbose_name='必要写真枚数')
    estimated_minutes = models.IntegerField(default=5, verbose_name='予想所要時間（分）')
    is_mandatory = models.BooleanField(default=True, verbose_name='必須ステップ')

    class Meta:
        verbose_name = 'ワークフローステップ'
        verbose_name_plural = 'ワークフローステップ'
        ordering = ['step_number']

    def __str__(self):
        return f"ステップ{self.step_number}: {self.title}"


class SurveyStepProgress(models.Model):
    """調査ステップ進捗管理"""
    STATUS_CHOICES = [
        ('not_started', '未開始'),
        ('in_progress', '進行中'),
        ('completed', '完了'),
        ('skipped', 'スキップ'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='step_progress', verbose_name='調査')
    workflow_step = models.ForeignKey(SurveyWorkflowStep, on_delete=models.CASCADE, verbose_name='ワークフローステップ')
    room = models.ForeignKey(SurveyRoom, on_delete=models.CASCADE, null=True, blank=True, verbose_name='対象部屋')
    wall = models.ForeignKey(SurveyWall, on_delete=models.CASCADE, null=True, blank=True, verbose_name='対象壁面')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name='ステータス')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='開始時刻')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完了時刻')
    notes = models.TextField(blank=True, verbose_name='メモ')
    data = models.JSONField(default=dict, blank=True, verbose_name='ステップデータ')

    class Meta:
        verbose_name = 'ステップ進捗'
        verbose_name_plural = 'ステップ進捗'
        unique_together = ['survey', 'workflow_step', 'room', 'wall']

    def __str__(self):
        return f"{self.survey} - {self.workflow_step.title}"

    def mark_completed(self):
        """ステップを完了としてマーク"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def get_duration_minutes(self):
        """実際の所要時間を計算"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() / 60)
        return None
