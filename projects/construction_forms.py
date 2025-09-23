from django import forms
from django.core.exceptions import ValidationError
from .models import (
    ConstructionProgress,
    ProgressPhoto,
    ProjectIssue,
    ProjectCompletion,
    Project,
    Craftsman,
)


class ConstructionProgressForm(forms.ModelForm):
    """施工進捗報告フォーム"""

    class Meta:
        model = ConstructionProgress
        fields = [
            "progress_rate",
            "work_description",
            "issues",
            "next_plan",
            "reported_by",
            "weather",
            "worker_count",
            "start_time",
            "end_time",
        ]
        widgets = {
            "progress_rate": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "max": "100", "step": "5"}
            ),
            "work_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "本日の作業内容を記入してください",
                }
            ),
            "issues": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "問題・課題があれば記入してください",
                }
            ),
            "next_plan": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "翌日の作業予定を記入してください",
                }
            ),
            "reported_by": forms.Select(attrs={"class": "form-select"}),
            "weather": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "晴れ、曇り、雨など"}
            ),
            "worker_count": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "max": "20"}
            ),
            "start_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "end_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        self.craftsman = kwargs.pop("craftsman", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        progress = super().save(commit=False)
        if self.project:
            progress.project = self.project
        if self.craftsman:
            progress.craftsman = self.craftsman
        if commit:
            progress.save()
        return progress

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            raise ValidationError("終了時刻は開始時刻より後にしてください。")

        return cleaned_data


class ProgressPhotoForm(forms.ModelForm):
    """進捗写真アップロードフォーム"""

    class Meta:
        model = ProgressPhoto
        fields = ["photo", "description", "photo_type"]
        widgets = {
            "photo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "description": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "写真の説明を入力してください"}
            ),
            "photo_type": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.progress = kwargs.pop("progress", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        photo = super().save(commit=False)
        if self.progress:
            photo.progress = self.progress
        if commit:
            photo.save()
        return photo


class ProjectIssueForm(forms.ModelForm):
    """プロジェクト問題報告フォーム"""

    class Meta:
        model = ProjectIssue
        fields = [
            "issue_type",
            "title",
            "description",
            "priority",
            "assigned_to",
            "estimated_cost",
        ]
        widgets = {
            "issue_type": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "問題のタイトルを入力してください"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "問題の詳細を記入してください",
                }
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "estimated_cost": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "追加費用見込み（円）"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        issue = super().save(commit=False)
        if self.project:
            issue.project = self.project
        if self.user:
            issue.reported_by = self.user
        if commit:
            issue.save()
        return issue


class IssueUpdateForm(forms.ModelForm):
    """問題更新フォーム"""

    class Meta:
        model = ProjectIssue
        fields = ["status", "assigned_to", "resolution", "estimated_cost"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "resolution": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "解決内容を記入してください",
                }
            ),
            "estimated_cost": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "追加費用見込み（円）"}
            ),
        }


class ProjectCompletionForm(forms.ModelForm):
    """プロジェクト完了フォーム"""

    class Meta:
        model = ProjectCompletion
        fields = [
            "completion_date",
            "customer_check_date",
            "approval_date",
            "final_photos_submitted",
            "customer_signature",
            "payment_processed",
            "completion_notes",
        ]
        widgets = {
            "completion_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "customer_check_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "approval_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "final_photos_submitted": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "customer_signature": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "payment_processed": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "completion_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "完了に関する備考を記入してください",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        completion = super().save(commit=False)
        if self.project:
            completion.project = self.project
        if commit:
            completion.save()
        return completion


class ProgressSearchForm(forms.Form):
    """進捗検索フォーム"""

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="全ての案件",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    craftsman = forms.ModelChoiceField(
        queryset=Craftsman.objects.all(),
        required=False,
        empty_label="全ての職人",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    progress_rate_min = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "最小進捗率"}
        ),
    )

    progress_rate_max = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "最大進捗率"}
        ),
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    has_issues = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )


class QuickProgressForm(forms.Form):
    """クイック進捗入力フォーム"""

    progress_rate = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-lg", "placeholder": "進捗率（%）"}
        ),
    )

    work_description = forms.CharField(
        max_length=500,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "placeholder": "簡潔な作業内容"}
        ),
    )

    issues = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "placeholder": "問題があれば記入"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        self.craftsman = kwargs.pop("craftsman", None)
        super().__init__(*args, **kwargs)

    def save(self):
        """クイック進捗として保存"""
        if self.is_valid() and self.project and self.craftsman:
            progress = ConstructionProgress.objects.create(
                project=self.project,
                craftsman=self.craftsman,
                progress_rate=self.cleaned_data["progress_rate"],
                work_description=self.cleaned_data["work_description"],
                issues=self.cleaned_data["issues"],
                reported_by="direct",
                worker_count=1,
            )
            return progress
        return None
