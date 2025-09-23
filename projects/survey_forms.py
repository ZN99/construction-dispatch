from django import forms
from django.utils import timezone
from .models import Survey, Surveyor, Project


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            "project",
            "surveyor",
            "scheduled_date",
            "estimated_duration",
            "priority",
            "access_info",
            "notes",
        ]
        widgets = {
            "project": forms.Select(attrs={"class": "form-control"}),
            "surveyor": forms.Select(attrs={"class": "form-control"}),
            "scheduled_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "estimated_duration": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "分"}
            ),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "access_info": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "現場へのアクセス情報"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "備考"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["surveyor"].queryset = Surveyor.objects.filter(is_active=True)
        self.fields["surveyor"].empty_label = "調査員を選択"


class SurveyAssignForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            "surveyor",
            "scheduled_date",
            "estimated_duration",
            "priority",
            "access_info",
            "notes",
        ]
        widgets = {
            "surveyor": forms.Select(attrs={"class": "form-control"}),
            "scheduled_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "estimated_duration": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "分", "value": "120"}
            ),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "access_info": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "駐車場、入り口、注意事項など",
                }
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "特記事項があれば入力"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["surveyor"].queryset = Surveyor.objects.filter(is_active=True)
        self.fields["surveyor"].empty_label = "調査員を選択"

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data["scheduled_date"]
        if scheduled_date and scheduled_date < timezone.now():
            raise forms.ValidationError("過去の日時は選択できません。")
        return scheduled_date


class SurveyCompletionForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            "site_condition",
            "customer_requirements",
            "technical_notes",
            "additional_work_needed",
            "actual_start_time",
            "actual_end_time",
        ]
        widgets = {
            "site_condition": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "現場の状況、構造、材質など",
                }
            ),
            "customer_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "顧客からの要望、希望など",
                }
            ),
            "technical_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "技術的な注意点、特殊な施工方法など",
                }
            ),
            "additional_work_needed": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "actual_start_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "actual_end_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # デフォルト値の設定
        if not self.instance.actual_end_time:
            self.fields["actual_end_time"].initial = timezone.now()


class SurveyFilterForm(forms.Form):
    STATUS_CHOICES = [("", "全てのステータス")] + Survey.STATUS_CHOICES
    PRIORITY_CHOICES = [("", "全ての優先度")] + Survey.PRIORITY_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    surveyor = forms.ModelChoiceField(
        queryset=Surveyor.objects.filter(is_active=True),
        required=False,
        empty_label="全ての調査員",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )


class BulkSurveyAssignForm(forms.Form):
    """一括調査アサインフォーム"""

    surveys = forms.ModelMultipleChoiceField(
        queryset=Survey.objects.filter(surveyor__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        label="調査案件",
    )
    surveyor = forms.ModelChoiceField(
        queryset=Surveyor.objects.filter(is_active=True),
        empty_label="調査員を選択",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="アサイン先調査員",
    )
    base_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="基準日",
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
        initial="09:00",
        label="開始時刻",
    )
    interval_minutes = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=180,
        label="間隔（分）",
    )


class SurveyorCapacityForm(forms.Form):
    """調査員稼働状況確認フォーム"""

    surveyor = forms.ModelChoiceField(
        queryset=Surveyor.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="調査員",
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="日付",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].initial = timezone.now().date()
