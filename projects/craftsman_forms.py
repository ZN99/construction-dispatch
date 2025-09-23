from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import (
    Craftsman,
    Assignment,
    CraftsmanSchedule,
    Project,
    ProjectType,
    Surveyor,
)


class CraftsmanSearchForm(forms.Form):
    """職人検索フォーム"""

    project_type = forms.ModelChoiceField(
        queryset=ProjectType.objects.filter(is_active=True),
        required=False,
        empty_label="工種を選択",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    skill_level = forms.ChoiceField(
        choices=[("", "技能レベル（最低）")] + Craftsman.SKILL_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    area = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "対応エリア（例：東京都、新宿区）"}
        ),
    )

    max_hourly_rate = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "最大時給（円）"}
        ),
    )

    min_rating = forms.DecimalField(
        max_digits=3,
        decimal_places=1,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "最低評価（1.0-5.0）",
                "step": "0.1",
                "min": "1.0",
                "max": "5.0",
            }
        ),
    )

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        initial=lambda: timezone.now().date(),
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        initial=lambda: timezone.now().date() + timedelta(days=7),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初期値設定
        if not self.data:
            self.fields["start_date"].initial = timezone.now().date()
            self.fields["end_date"].initial = timezone.now().date() + timedelta(days=7)


class AssignmentForm(forms.ModelForm):
    """案件アサインフォーム"""

    class Meta:
        model = Assignment
        fields = [
            "project",
            "craftsman",
            "priority",
            "scheduled_start_date",
            "scheduled_end_date",
            "estimated_hours",
            "offered_rate",
            "inquiry_message",
            "contact_method",
        ]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select"}),
            "craftsman": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "scheduled_start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "scheduled_end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "estimated_hours": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "想定作業時間"}
            ),
            "offered_rate": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "提示時給（円）"}
            ),
            "inquiry_message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "打診メッセージを入力してください",
                }
            ),
            "contact_method": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        craftsman = kwargs.pop("craftsman", None)
        super().__init__(*args, **kwargs)

        if project:
            self.fields["project"].initial = project
            self.fields["project"].widget.attrs["readonly"] = True

        if craftsman:
            self.fields["craftsman"].initial = craftsman
            self.fields["offered_rate"].initial = craftsman.hourly_rate

            # デフォルトメッセージを生成
            if project:
                default_message = f"""
{craftsman.name}さん

お疲れ様です。以下の案件についてご相談があります。

案件名: {project.title}
顧客: {project.customer.name}
場所: {project.address}
工種: {project.project_type.name}

ご都合はいかがでしょうか？
詳細についてお打ち合わせさせていただければと思います。

よろしくお願いいたします。
"""
                self.fields["inquiry_message"].initial = default_message.strip()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("scheduled_start_date")
        end_date = cleaned_data.get("scheduled_end_date")
        craftsman = cleaned_data.get("craftsman")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("開始日は終了日より前である必要があります。")

            # 職人の稼働可能性をチェック
            if craftsman:
                current_date = start_date
                while current_date <= end_date:
                    if not craftsman.can_work_on(current_date):
                        raise forms.ValidationError(
                            f"{craftsman.name}さんは{current_date}に稼働できません。"
                        )
                    current_date += timedelta(days=1)

        return cleaned_data


class AssignmentResponseForm(forms.ModelForm):
    """案件返答フォーム"""

    class Meta:
        model = Assignment
        fields = ["status", "response_message"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "response_message": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "返答メッセージ"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ステータス選択肢を制限
        self.fields["status"].choices = [
            ("confirmed", "確定"),
            ("declined", "辞退"),
        ]


class CraftsmanScheduleForm(forms.ModelForm):
    """職人スケジュール管理フォーム"""

    class Meta:
        model = CraftsmanSchedule
        fields = ["craftsman", "date", "is_available", "notes"]
        widgets = {
            "craftsman": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": "備考"}
            ),
        }


class BulkScheduleForm(forms.Form):
    """一括スケジュール設定フォーム"""

    craftsman = forms.ModelChoiceField(
        queryset=Craftsman.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    is_available = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    exclude_weekends = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "placeholder": "備考（一括適用）"}
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("開始日は終了日より前である必要があります。")

            # 期間チェック（最大3ヶ月）
            if (end_date - start_date).days > 90:
                raise forms.ValidationError("一括設定は最大3ヶ月までです。")

        return cleaned_data


class ProjectMatchingForm(forms.Form):
    """プロジェクトマッチング用フォーム"""

    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(status__in=["pending", "scheduled"]),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    max_results = forms.IntegerField(
        initial=10,
        min_value=1,
        max_value=50,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "最大表示件数"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # デフォルト値設定
        if not self.data:
            self.fields["start_date"].initial = timezone.now().date() + timedelta(
                days=1
            )
            self.fields["end_date"].initial = timezone.now().date() + timedelta(days=7)


class QuickAssignmentForm(forms.Form):
    """クイックアサインフォーム"""

    craftsman_id = forms.IntegerField(widget=forms.HiddenInput())
    project_id = forms.IntegerField(widget=forms.HiddenInput())

    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm", "type": "date"}
        )
    )

    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm", "type": "date"}
        )
    )

    estimated_hours = forms.IntegerField(
        initial=8,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm", "min": "1", "max": "24"}
        ),
    )

    contact_method = forms.ChoiceField(
        choices=Assignment._meta.get_field("contact_method").choices,
        initial="phone",
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
