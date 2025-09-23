from django.db import models
from django.utils import timezone
from datetime import datetime
from decimal import Decimal


class Project(models.Model):
    ORDER_STATUS_CHOICES = [
        ('受注', '受注'),
        ('NG', 'NG'),
        ('A', 'A'),
        ('検討中', '検討中')
    ]

    # 基本情報
    management_no = models.CharField(max_length=20, unique=True, verbose_name='管理No')
    site_name = models.CharField(max_length=200, verbose_name='現場名')
    site_address = models.TextField(verbose_name='現場住所')
    work_type = models.CharField(max_length=50, verbose_name='種別')

    # 受注・見積情報
    order_status = models.CharField(
        max_length=10,
        choices=ORDER_STATUS_CHOICES,
        default='検討中',
        verbose_name='受注ヨミ'
    )
    estimate_issued_date = models.DateField(
        null=True, blank=True, verbose_name='見積書発行日'
    )
    estimate_not_required = models.BooleanField(
        default=False, verbose_name='見積書不要'
    )
    estimate_amount = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, verbose_name='見積金額(税込)'
    )
    parking_fee = models.DecimalField(
        max_digits=8, decimal_places=0, default=0, verbose_name='駐車場代(税込)'
    )

    # 業者・担当情報
    contractor_name = models.CharField(max_length=100, verbose_name='請負業者名')
    contractor_address = models.TextField(verbose_name='請負業者住所')
    project_manager = models.CharField(max_length=50, verbose_name='案件担当')

    # スケジュール
    payment_due_date = models.DateField(
        null=True, blank=True, verbose_name='入金予定日'
    )
    work_start_date = models.DateField(
        null=True, blank=True, verbose_name='工事開始日'
    )
    work_start_completed = models.BooleanField(
        default=False, verbose_name='工事開始完了'
    )
    work_end_date = models.DateField(
        null=True, blank=True, verbose_name='工事終了日'
    )
    work_end_completed = models.BooleanField(
        default=False, verbose_name='工事終了完了'
    )
    contract_date = models.DateField(
        null=True, blank=True, verbose_name='契約日'
    )

    # 請求・経費管理
    invoice_issued = models.BooleanField(default=False, verbose_name='請求書発行')
    expense_item_1 = models.CharField(
        max_length=100, blank=True, verbose_name='諸経費項目①'
    )
    expense_amount_1 = models.DecimalField(
        max_digits=8, decimal_places=0, default=0, verbose_name='諸経費代(税込)①'
    )
    expense_item_2 = models.CharField(
        max_length=100, blank=True, verbose_name='諸経費項目②'
    )
    expense_amount_2 = models.DecimalField(
        max_digits=8, decimal_places=0, default=0, verbose_name='諸経費代(税込)②'
    )

    # 自動計算項目
    billing_amount = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, verbose_name='請求額実請求'
    )
    amount_difference = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, verbose_name='増減'
    )

    # 現地調査関連
    survey_required = models.BooleanField(default=False, verbose_name='現地調査必要')
    survey_status = models.CharField(
        max_length=20,
        choices=[
            ('not_required', '不要'),
            ('required', '必要'),
            ('scheduled', '予定済み'),
            ('in_progress', '調査中'),
            ('completed', '完了'),
        ],
        default='not_required',
        verbose_name='現地調査ステータス'
    )

    # 支払管理
    payment_scheduled_date = models.DateField(
        null=True, blank=True,
        verbose_name='支払予定日',
        help_text='業者への支払予定日'
    )
    payment_executed_date = models.DateField(
        null=True, blank=True,
        verbose_name='支払実行日',
        help_text='実際に支払を行った日'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', '予定'),
            ('executed', '支払済み'),
            ('overdue', '遅延'),
            ('cancelled', 'キャンセル'),
        ],
        default='scheduled',
        verbose_name='支払状況'
    )
    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=0,
        null=True, blank=True,
        verbose_name='支払金額',
        help_text='実際の支払金額（請求額と異なる場合に使用）'
    )
    payment_memo = models.TextField(
        blank=True,
        verbose_name='支払メモ',
        help_text='支払に関する特記事項'
    )

    # その他
    notes = models.TextField(blank=True, verbose_name='備考')
    additional_items = models.JSONField(default=dict, blank=True, verbose_name="追加項目")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        verbose_name = '案件'
        verbose_name_plural = '案件一覧'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.management_no} - {self.site_name}"

    def generate_management_no(self):
        """管理No自動採番"""
        current_year = timezone.now().year
        year_suffix = str(current_year)[-2:]  # 下2桁

        # 今年の最新番号を取得
        latest = Project.objects.filter(
            management_no__startswith=f'P{year_suffix}'
        ).order_by('-management_no').first()

        if latest:
            # 最新番号から連番部分を取得してインクリメント
            latest_num = int(latest.management_no[3:])
            new_num = latest_num + 1
        else:
            new_num = 1

        return f'P{year_suffix}{new_num:04d}'

    def save(self, *args, **kwargs):
        # 管理No自動採番
        if not self.management_no:
            self.management_no = self.generate_management_no()

        # 自動計算処理
        self.billing_amount = (
            Decimal(str(self.estimate_amount)) +
            Decimal(str(self.parking_fee)) +
            Decimal(str(self.expense_amount_1)) +
            Decimal(str(self.expense_amount_2))
        )
        self.amount_difference = (
            Decimal(str(self.billing_amount)) -
            Decimal(str(self.estimate_amount))
        )

        super().save(*args, **kwargs)

    def get_status_color(self):
        """ステータスに応じた背景色を返す"""
        color_map = {
            '受注': 'bg-success',  # 緑
            'NG': 'bg-secondary',  # グレー
            'A': 'bg-danger',      # ピンク/赤
            '検討中': 'bg-warning' # 黄色
        }
        return color_map.get(self.order_status, '')

    def get_status_color_hex(self):
        """ステータスに応じた背景色（Hex）を返す"""
        color_map = {
            '受注': '#28a745',     # 緑
            'NG': '#6c757d',      # グレー
            'A': '#dc3545',       # ピンク/赤
            '検討中': '#ffc107'    # 黄色
        }
        return color_map.get(self.order_status, '#ffffff')

    def get_work_progress_percentage(self):
        """工事進捗率を計算して返す（実際の進捗ステップベース）"""
        # 実際の進捗ステップから計算
        active_steps = self.progress_steps.filter(is_active=True)
        if not active_steps.exists():
            # 進捗ステップがない場合は日付ベースで計算
            return self._get_date_based_progress()

        total_steps = active_steps.count()
        completed_steps = active_steps.filter(is_completed=True).count()

        if total_steps == 0:
            return 0

        return int((completed_steps / total_steps) * 100)

    def _get_date_based_progress(self):
        """日付ベースの進捗計算（フォールバック）"""
        if not self.work_start_date or not self.work_end_date:
            return 0

        today = timezone.now().date()

        # 工事期間の計算
        total_days = (self.work_end_date - self.work_start_date).days
        if total_days <= 0:
            return 100

        # 経過日数の計算
        if today < self.work_start_date:
            return 0  # 開始前
        elif today > self.work_end_date:
            return 100  # 完了
        else:
            elapsed_days = (today - self.work_start_date).days
            return min(100, max(0, int((elapsed_days / total_days) * 100)))

    def get_work_phase(self):
        """現在の工事フェーズを返す（実際の進捗ステップベース）"""
        # 実際の進捗ステップから判定
        active_steps = self.progress_steps.filter(is_active=True)
        if active_steps.exists():
            progress = self.get_work_progress_percentage()
            completed_steps_query = active_steps.filter(is_completed=True)
            completed_steps_count = completed_steps_query.count()

            # 完了したステップの内容に基づく判定
            if progress == 0:
                return '開始前'
            elif progress == 100:
                return '完了'
            else:
                # 完了したステップの種類を確認
                completed_step_names = list(completed_steps_query.values_list('template__name', flat=True))

                # 請求書発行が完了している場合
                if '請求書発行' in completed_step_names:
                    return '完了間近'
                # 工事終了が完了している場合
                elif '工事終了' in completed_step_names:
                    return '完了間近'
                # 工事開始が完了している場合
                elif '工事開始' in completed_step_names:
                    if progress >= 60:
                        return '施工中'
                    else:
                        return '着工'
                # 契約が完了している場合
                elif '契約' in completed_step_names:
                    return '契約済み'
                # 見積書発行のみ完了している場合
                elif '見積書発行' in completed_step_names:
                    return '見積済み'
                # その他の場合
                else:
                    if progress < 30:
                        return '初期段階'
                    elif progress < 80:
                        return '施工中'
                    else:
                        return '完了間近'

        # フォールバック：日付ベース
        if not self.work_start_date or not self.work_end_date:
            if self.order_status == '受注':
                return '準備中'
            return '未定'

        today = timezone.now().date()

        if today < self.work_start_date:
            return '開始前'
        elif today > self.work_end_date:
            return '完了'
        else:
            progress = self._get_date_based_progress()
            if progress < 25:
                return '着工'
            elif progress < 75:
                return '施工中'
            else:
                return '完了間近'

    def get_progress_status(self):
        """進捗状況の総合判定を返す"""
        if self.order_status == 'NG':
            return {'phase': 'NG', 'color': 'secondary', 'percentage': 0}
        elif self.order_status == '検討中':
            return {'phase': '検討中', 'color': 'warning', 'percentage': 0}

        # 受注案件の進捗判定
        phase = self.get_work_phase()
        percentage = self.get_work_progress_percentage()

        if phase == '準備中':
            color = 'info'
        elif phase == '開始前':
            color = 'primary'
        elif phase == '見積済み':
            color = 'info'
        elif phase == '契約済み':
            color = 'primary'
        elif phase == '着工':
            color = 'success'
        elif phase == '初期段階':
            color = 'info'
        elif phase == '施工中':
            color = 'success'
        elif phase == '完了間近':
            color = 'warning'
        elif phase == '完了':
            color = 'dark'
        else:
            color = 'secondary'

        return {'phase': phase, 'color': color, 'percentage': percentage}

    def get_progress_details(self):
        """進捗の詳細情報を返す（動的ステップを含む）"""
        active_steps = self.progress_steps.filter(is_active=True).order_by('order', 'template__order')
        completed_steps = active_steps.filter(is_completed=True)

        # 実際のステップ数を使用する
        # additional_itemsのstep_orderはUIの表示順序を定義しているが、
        # 実際のステップがすべて作成されているとは限らない
        total_steps = active_steps.count()

        # step_orderに現場調査があるが、実際のステップが作成されていない場合の対応
        if self.additional_items and 'step_order' in self.additional_items:
            step_order = self.additional_items.get('step_order', [])

            # step_orderに現場調査が含まれているか確認
            has_site_survey_in_order = any(s.get('step') == 'site_survey' for s in step_order)

            # 実際のステップに現場調査が含まれているか確認
            has_site_survey_step = active_steps.filter(template__name='現場調査').exists()

            # step_orderに現場調査があるが、実際のステップにない場合
            if has_site_survey_in_order and not has_site_survey_step:
                # UIの整合性のため、仮想的に1ステップ追加
                total_steps += 1

        completed_steps_count = completed_steps.count()

        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps_count,
            'remaining_steps': total_steps - completed_steps_count,
            'steps': [
                {
                    'name': step.template.name,
                    'completed': step.is_completed,
                    'completed_date': step.completed_date,
                    'icon': step.template.icon
                }
                for step in active_steps
            ]
        }

    def get_days_until_deadline(self):
        """締切までの日数を返す"""
        if not self.work_end_date:
            return None

        today = timezone.now().date()
        delta = self.work_end_date - today
        return delta.days

    def is_deadline_approaching(self):
        """締切が迫っているかどうか"""
        days = self.get_days_until_deadline()
        return days is not None and 0 <= days <= 7  # 1週間以内

    def get_subcontract_status(self):
        """発注連携状況を返す"""
        from subcontract_management.models import Subcontract

        subcontract_count = Subcontract.objects.filter(project=self).count()

        if subcontract_count == 0:
            return {
                'status': '未連携',
                'count': 0,
                'color': 'secondary',
                'icon': 'fa-times-circle'
            }
        else:
            return {
                'status': '連携済み',
                'count': subcontract_count,
                'color': 'success',
                'icon': 'fa-check-circle'
            }

    def get_material_status(self):
        """資材連携状況を返す"""
        material_count = self.material_orders.count()

        if material_count == 0:
            return {
                'status': '未連携',
                'count': 0,
                'color': 'secondary',
                'icon': 'fa-times-circle'
            }
        else:
            # 完了していない発注があるかチェック
            pending_count = self.material_orders.exclude(status='completed').count()
            if pending_count > 0:
                return {
                    'status': f'連携済み({pending_count}件進行中)',
                    'count': material_count,
                    'color': 'warning',
                    'icon': 'fa-clock'
                }
            else:
                return {
                    'status': '完了',
                    'count': material_count,
                    'color': 'success',
                    'icon': 'fa-check-circle'
                }

    def get_additional_items_summary(self):
        """追加項目の概要を返す"""
        if not self.additional_items:
            return {
                'has_items': False,
                'dynamic_steps_count': 0,
                'summary': '標準設定'
            }

        dynamic_steps = self.additional_items.get('dynamic_steps', {})
        step_order = self.additional_items.get('step_order', [])

        # 実際に追加された動的ステップをカウント（標準以外のステップ）
        standard_steps = {'estimate', 'contract', 'work_start', 'work_end', 'invoice'}
        custom_steps_in_order = [step for step in step_order if step.get('step') not in standard_steps]

        # dynamic_stepsのsite_surveyフィールドは、step_orderのsite_surveyステップの詳細設定
        # そのため、重複カウントしないようにする
        # step_orderにsite_surveyがある場合は、dynamic_stepsのsite_survey関連はカウントしない
        has_site_survey_in_order = any(s.get('step') == 'site_survey' for s in step_order)

        if has_site_survey_in_order:
            # step_orderに現場調査がある場合、dynamic_stepsからは除外
            custom_dynamic_steps = 0
        else:
            # step_orderに現場調査がない場合のみ、dynamic_stepsからカウント
            custom_dynamic_steps = len([k for k in dynamic_steps.keys() if 'site_survey' in k])
            # site_survey_scheduledとsite_survey_actualは同じステップの2つのフィールドなので1としてカウント
            if custom_dynamic_steps > 0:
                custom_dynamic_steps = 1

        total_custom_items = len(custom_steps_in_order)

        if total_custom_items == 0:
            return {
                'has_items': False,
                'dynamic_steps_count': 0,
                'summary': '標準設定'
            }

        summary_parts = []
        if custom_dynamic_steps > 0:
            summary_parts.append(f'追加ステップ: {custom_dynamic_steps}件')
        if len(custom_steps_in_order) > 0:
            summary_parts.append(f'カスタム順序: {len(custom_steps_in_order)}件')

        summary = ', '.join(summary_parts) if summary_parts else 'カスタム設定'

        return {
            'has_items': True,
            'dynamic_steps_count': total_custom_items,
            'custom_fields_count': len(custom_steps_in_order),
            'summary': summary
        }

    def get_revenue_breakdown(self):
        """売上・原価・利益の内訳を返す"""
        # 売上 = 請求額実請求
        revenue = self.billing_amount or Decimal('0')

        # 売上原価の計算（例：見積金額の70%と仮定、実際の業務に合わせて調整）
        cost_of_sales = (self.estimate_amount or Decimal('0')) * Decimal('0.7')

        # 売上総利益 = 売上 - 売上原価
        gross_profit = revenue - cost_of_sales

        # 利益率
        profit_margin = (gross_profit / revenue * 100) if revenue > 0 else Decimal('0')

        return {
            'revenue': revenue,           # 売上
            'cost_of_sales': cost_of_sales,  # 売上原価
            'gross_profit': gross_profit,    # 売上総利益
            'profit_margin': profit_margin   # 利益率
        }

    def get_survey_status_display_with_color(self):
        """現地調査ステータスの表示名と色を返す"""
        status_info = {
            'not_required': {'display': '不要', 'color': 'secondary'},
            'required': {'display': '必要', 'color': 'warning'},
            'scheduled': {'display': '予定済み', 'color': 'info'},
            'in_progress': {'display': '調査中', 'color': 'primary'},
            'completed': {'display': '完了', 'color': 'success'},
        }
        return status_info.get(self.survey_status, {'display': '不明', 'color': 'secondary'})

    def get_latest_survey(self):
        """最新の現地調査を取得"""
        try:
            from surveys.models import Survey
            return Survey.objects.filter(project=self).order_by('-scheduled_date', '-created_at').first()
        except ImportError:
            return None

    def get_survey_summary(self):
        """現地調査のサマリー情報を取得"""
        try:
            from surveys.models import Survey
            surveys = Survey.objects.filter(project=self)

            if not surveys.exists():
                return None

            total_count = surveys.count()
            completed_count = surveys.filter(status='completed').count()
            in_progress_count = surveys.filter(status='in_progress').count()
            scheduled_count = surveys.filter(status='scheduled').count()

            # 次回予定の調査
            next_survey = surveys.filter(
                status__in=['scheduled', 'in_progress'],
                scheduled_date__gte=timezone.now().date()
            ).order_by('scheduled_date', 'scheduled_start_time').first()

            return {
                'total_count': total_count,
                'completed_count': completed_count,
                'in_progress_count': in_progress_count,
                'scheduled_count': scheduled_count,
                'next_survey': next_survey,
                'has_surveys': total_count > 0
            }
        except ImportError:
            return None


class ProgressStepTemplate(models.Model):
    """進捗ステップテンプレート"""
    name = models.CharField(max_length=100, verbose_name='ステップ名')
    icon = models.CharField(max_length=50, default='fas fa-circle', verbose_name='アイコン')
    order = models.IntegerField(default=0, verbose_name='表示順')
    is_default = models.BooleanField(default=False, verbose_name='デフォルト表示')
    is_system = models.BooleanField(default=False, verbose_name='システム項目')
    field_type = models.CharField(
        max_length=20,
        choices=[
            ('date', '日付'),
            ('checkbox', 'チェックボックス'),
            ('select', '選択肢'),
            ('text', 'テキスト')
        ],
        default='date',
        verbose_name='フィールドタイプ'
    )
    field_options = models.JSONField(blank=True, null=True, verbose_name='フィールドオプション')

    class Meta:
        verbose_name = '進捗ステップテンプレート'
        verbose_name_plural = '進捗ステップテンプレート一覧'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ProjectProgressStep(models.Model):
    """プロジェクト進捗ステップ"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='progress_steps')
    template = models.ForeignKey(ProgressStepTemplate, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, verbose_name='表示順')
    is_active = models.BooleanField(default=True, verbose_name='アクティブ')
    is_completed = models.BooleanField(default=False, verbose_name='完了')
    value = models.JSONField(blank=True, null=True, verbose_name='値')
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name='完了日時')

    class Meta:
        verbose_name = 'プロジェクト進捗ステップ'
        verbose_name_plural = 'プロジェクト進捗ステップ一覧'
        ordering = ['order', 'template__order']
        unique_together = ['project', 'template']

    def __str__(self):
        return f"{self.project.management_no} - {self.template.name}"


class Contractor(models.Model):
    """業者マスター"""
    name = models.CharField(max_length=200, verbose_name='業者名')
    address = models.TextField(blank=True, verbose_name='住所')
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話番号')
    email = models.EmailField(blank=True, verbose_name='メールアドレス')
    contact_person = models.CharField(max_length=100, blank=True, verbose_name='担当者名')
    specialties = models.TextField(blank=True, verbose_name='専門分野')

    # 業者分類（複数選択対応）
    is_ordering = models.BooleanField(default=False, verbose_name='発注業者')
    is_receiving = models.BooleanField(default=False, verbose_name='受注業者')
    is_supplier = models.BooleanField(default=False, verbose_name='資材屋')
    is_other = models.BooleanField(default=False, verbose_name='その他')
    other_description = models.CharField(max_length=100, blank=True, verbose_name='その他内容')

    is_active = models.BooleanField(default=True, verbose_name='アクティブ')

    # 支払情報
    payment_day = models.IntegerField(
        null=True, blank=True,
        verbose_name='支払日',
        help_text='毎月の支払日（1-31）。例：25日払いの場合は25'
    )
    payment_cycle = models.CharField(
        max_length=20,
        choices=[
            ('monthly', '月1回'),
            ('bimonthly', '月2回'),
            ('weekly', '週1回'),
            ('project_end', '案件完了時'),
        ],
        default='monthly',
        verbose_name='支払サイクル'
    )
    closing_day = models.IntegerField(
        null=True, blank=True,
        verbose_name='締め日',
        help_text='月末締めの場合は31、20日締めの場合は20'
    )
    bank_name = models.CharField(max_length=100, blank=True, verbose_name='銀行名')
    branch_name = models.CharField(max_length=100, blank=True, verbose_name='支店名')
    account_type = models.CharField(
        max_length=10,
        choices=[
            ('ordinary', '普通'),
            ('current', '当座'),
        ],
        default='ordinary',
        blank=True,
        verbose_name='口座種別'
    )
    account_number = models.CharField(max_length=20, blank=True, verbose_name='口座番号')
    account_holder = models.CharField(max_length=100, blank=True, verbose_name='口座名義')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        verbose_name = '業者'
        verbose_name_plural = '業者一覧'
        ordering = ['-is_ordering', '-is_active', 'name']

    def __str__(self):
        return self.name

    def get_classification_display(self):
        """業者分類の表示用文字列を返す"""
        classifications = []
        if self.is_ordering:
            classifications.append('発注業者')
        if self.is_receiving:
            classifications.append('受注業者')
        if self.is_supplier:
            classifications.append('資材屋')
        if self.is_other and self.other_description:
            classifications.append(f'その他({self.other_description})')
        elif self.is_other:
            classifications.append('その他')

        return ', '.join(classifications) if classifications else '未分類'


class FixedCost(models.Model):
    """固定費管理"""
    COST_TYPE_CHOICES = [
        ('business_outsourcing', '業務委託費'),
        ('insurance', '保険'),
        ('legal_fee', '弁護士費用'),
        ('accounting_fee', '税理士費用'),
        ('executive_compensation', '役員報酬'),
        ('rent', '家賃'),
        ('utilities', '光熱費'),
        ('other', 'その他'),
    ]

    name = models.CharField(max_length=100, verbose_name='費目名')
    cost_type = models.CharField(
        max_length=30,
        choices=COST_TYPE_CHOICES,
        verbose_name='費目種別'
    )
    monthly_amount = models.DecimalField(
        max_digits=10, decimal_places=0,
        verbose_name='月額'
    )
    start_date = models.DateField(verbose_name='開始日')
    end_date = models.DateField(null=True, blank=True, verbose_name='終了日')
    is_active = models.BooleanField(default=True, verbose_name='アクティブ')
    notes = models.TextField(blank=True, verbose_name='備考')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        verbose_name = '固定費'
        verbose_name_plural = '固定費一覧'
        ordering = ['cost_type', 'name']

    def __str__(self):
        return f"{self.name} (¥{self.monthly_amount:,})"

    def is_active_in_month(self, year, month):
        """指定月にアクティブかどうか"""
        from datetime import date
        target_date = date(year, month, 1)

        if not self.is_active:
            return False

        if self.start_date > target_date:
            return False

        if self.end_date and self.end_date < target_date:
            return False

        return True


class VariableCost(models.Model):
    """変動費管理（販管費等）"""
    COST_TYPE_CHOICES = [
        ('sales_expense', '営業費'),
        ('marketing_expense', 'マーケティング費'),
        ('admin_expense', '管理費'),
        ('travel_expense', '交通費'),
        ('entertainment_expense', '接待費'),
        ('other', 'その他'),
    ]

    name = models.CharField(max_length=100, verbose_name='費目名')
    cost_type = models.CharField(
        max_length=30,
        choices=COST_TYPE_CHOICES,
        verbose_name='費目種別'
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=0,
        verbose_name='金額'
    )
    incurred_date = models.DateField(verbose_name='発生日')
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='関連案件'
    )
    notes = models.TextField(blank=True, verbose_name='備考')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        verbose_name = '変動費'
        verbose_name_plural = '変動費一覧'
        ordering = ['-incurred_date']

    def __str__(self):
        return f"{self.name} (¥{self.amount:,}) - {self.incurred_date}"


class MaterialOrder(models.Model):
    """資材発注管理"""
    ORDER_STATUS_CHOICES = [
        ('draft', '下書き'),
        ('ordered', '発注済み'),
        ('delivered', '納品済み'),
        ('completed', '完了'),
        ('cancelled', 'キャンセル'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='material_orders',
        verbose_name='案件'
    )
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.CASCADE,
        verbose_name='資材業者'
    )
    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='発注番号'
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='draft',
        verbose_name='ステータス'
    )
    order_date = models.DateField(verbose_name='発注日')
    delivery_date = models.DateField(
        null=True, blank=True,
        verbose_name='納期'
    )
    actual_delivery_date = models.DateField(
        null=True, blank=True,
        verbose_name='実際の納品日'
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=0,
        default=0,
        verbose_name='総額'
    )
    notes = models.TextField(blank=True, verbose_name='備考')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        verbose_name = '資材発注'
        verbose_name_plural = '資材発注一覧'
        ordering = ['-order_date', '-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.contractor.name}"

    def generate_order_number(self):
        """発注番号自動採番"""
        current_year = timezone.now().year
        year_suffix = str(current_year)[-2:]

        # 今年の最新番号を取得
        latest = MaterialOrder.objects.filter(
            order_number__startswith=f'M{year_suffix}'
        ).order_by('-order_number').first()

        if latest:
            latest_num = int(latest.order_number[3:])
            new_num = latest_num + 1
        else:
            new_num = 1

        return f'M{year_suffix}{new_num:04d}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def get_status_color(self):
        """ステータスに応じた色を返す"""
        color_map = {
            'draft': 'secondary',
            'ordered': 'warning',
            'delivered': 'info',
            'completed': 'success',
            'cancelled': 'danger',
        }
        return color_map.get(self.status, 'secondary')

    def get_status_color_hex(self):
        """ステータスに応じた背景色（Hex）を返す"""
        color_map = {
            'draft': '#6c757d',
            'ordered': '#f59e0b',
            'delivered': '#3b82f6',
            'completed': '#10b981',
            'cancelled': '#ef4444',
        }
        return color_map.get(self.status, '#6c757d')


class MaterialOrderItem(models.Model):
    """資材発注項目"""
    order = models.ForeignKey(
        MaterialOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='発注'
    )
    material_name = models.CharField(max_length=200, verbose_name='資材名')
    specification = models.TextField(blank=True, verbose_name='仕様・規格')
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='数量'
    )
    unit = models.CharField(max_length=20, verbose_name='単位')
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='単価'
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='小計'
    )
    notes = models.TextField(blank=True, verbose_name='備考')

    class Meta:
        verbose_name = '資材発注項目'
        verbose_name_plural = '資材発注項目一覧'

    def __str__(self):
        return f"{self.material_name} - {self.quantity}{self.unit}"

    def save(self, *args, **kwargs):
        # 小計の自動計算
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        # 発注の総額を更新
        self.order.total_amount = sum(
            item.total_price for item in self.order.items.all()
        )
        self.order.save()


class Invoice(models.Model):
    """請求書モデル"""
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('issued', '発行済み'),
        ('sent', '送付済み'),
        ('paid', '入金済み'),
        ('overdue', '延滞'),
        ('cancelled', 'キャンセル'),
    ]

    TAX_TYPE_CHOICES = [
        ('included', '税込'),
        ('excluded', '税抜'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, verbose_name='請求書番号')
    client_name = models.CharField(max_length=200, verbose_name='受注先名')
    client_address = models.TextField(blank=True, verbose_name='受注先住所')

    # 請求書情報
    issue_date = models.DateField(verbose_name='発行日')
    due_date = models.DateField(verbose_name='支払期限')
    billing_period_start = models.DateField(verbose_name='請求期間開始')
    billing_period_end = models.DateField(verbose_name='請求期間終了')

    # 金額情報
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='小計（税抜）')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name='消費税率')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='消費税額')
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='合計金額')

    # ステータス
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='ステータス')

    # 備考
    notes = models.TextField(blank=True, verbose_name='備考')

    # システム情報
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    created_by = models.CharField(max_length=100, blank=True, verbose_name='作成者')

    class Meta:
        verbose_name = '請求書'
        verbose_name_plural = '請求書一覧'
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.client_name}"

    def generate_invoice_number(self):
        """請求書番号自動採番"""
        current_year = timezone.now().year
        current_month = timezone.now().month
        year_month = f'{current_year}{current_month:02d}'

        # 今月の最新番号を取得
        latest = Invoice.objects.filter(
            invoice_number__startswith=f'INV-{year_month}'
        ).order_by('-invoice_number').first()

        if latest:
            # 最新番号から連番部分を取得してインクリメント
            latest_num = int(latest.invoice_number.split('-')[-1])
            new_num = latest_num + 1
        else:
            new_num = 1

        return f'INV-{year_month}-{new_num:03d}'

    def calculate_tax_amount(self):
        """消費税額を計算"""
        return int(self.subtotal * (self.tax_rate / 100))

    def calculate_total_amount(self):
        """合計金額を計算"""
        return self.subtotal + self.tax_amount

    def save(self, *args, **kwargs):
        # 請求書番号自動採番
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()

        # 税額・合計額自動計算
        self.tax_amount = self.calculate_tax_amount()
        self.total_amount = self.calculate_total_amount()

        super().save(*args, **kwargs)

    def get_status_color(self):
        """ステータスに応じた色を返す"""
        color_map = {
            'draft': 'secondary',
            'issued': 'primary',
            'sent': 'info',
            'paid': 'success',
            'overdue': 'danger',
            'cancelled': 'warning',
        }
        return color_map.get(self.status, 'secondary')


class InvoiceItem(models.Model):
    """請求書明細"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name='請求書')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='案件')

    # 明細情報
    description = models.CharField(max_length=500, verbose_name='項目名')
    work_period_start = models.DateField(null=True, blank=True, verbose_name='作業期間開始')
    work_period_end = models.DateField(null=True, blank=True, verbose_name='作業期間終了')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='数量')
    unit = models.CharField(max_length=20, default='式', verbose_name='単位')
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='単価')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='金額')

    # 表示順
    order = models.IntegerField(default=0, verbose_name='表示順')

    class Meta:
        verbose_name = '請求書明細'
        verbose_name_plural = '請求書明細一覧'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"

    def save(self, *args, **kwargs):
        # 金額自動計算
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        # 請求書の小計を更新
        self.invoice.subtotal = sum(item.amount for item in self.invoice.items.all())
        self.invoice.save()
