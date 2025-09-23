from django import forms
from django.forms import widgets
from .models import Customer, Project, ProjectType
from .survey_forms import SurveyForm, SurveyAssignForm, SurveyCompletionForm
import json


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "顧客名を入力"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "電話番号を入力"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "メールアドレス（任意）"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "住所（任意）"}
            ),
        }


class ProjectTypeSelectForm(forms.Form):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all().order_by("name"),
        empty_label="顧客を選択してください",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="顧客",
    )
    project_type = forms.ModelChoiceField(
        queryset=ProjectType.objects.filter(is_active=True),
        empty_label="工種を選択してください",
        widget=forms.Select(
            attrs={"class": "form-control", "id": "project-type-select"}
        ),
        label="工種",
    )


class BaseProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "customer",
            "title",
            "address",
            "start_date",
            "end_date",
            "amount",
            "requires_survey",
            "notes",
        ]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "案件名を入力"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "作業場所を入力"}
            ),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "金額を入力"}
            ),
            "requires_survey": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "備考（任意）"}
            ),
        }

    def __init__(self, *args, **kwargs):
        selected_customer_id = kwargs.pop("selected_customer_id", None)
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.all().order_by("name")
        self.fields["customer"].empty_label = "顧客を選択してください"

        # 事前選択された顧客がある場合は初期値に設定
        if selected_customer_id:
            self.fields["customer"].initial = selected_customer_id


class CrossProjectForm(BaseProjectForm):
    area_sqm = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "面積（㎡）"}
        ),
        label="施工面積（㎡）",
    )
    wall_type = forms.ChoiceField(
        choices=[
            ("", "壁の種類を選択"),
            ("drywall", "石膏ボード"),
            ("concrete", "コンクリート"),
            ("wood", "木材"),
            ("other", "その他"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="壁の種類",
    )
    paper_type = forms.ChoiceField(
        choices=[
            ("", "クロスの種類を選択"),
            ("vinyl", "ビニルクロス"),
            ("paper", "紙クロス"),
            ("fabric", "織物クロス"),
            ("other", "その他"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="クロスの種類",
    )

    def save(self, commit=True):
        project = super().save(commit=False)
        project.project_type = ProjectType.objects.get(name="クロス")
        project.details = {
            "area_sqm": float(self.cleaned_data["area_sqm"]),
            "wall_type": self.cleaned_data["wall_type"],
            "paper_type": self.cleaned_data["paper_type"],
        }
        if commit:
            project.save()
        return project


class CleaningProjectForm(BaseProjectForm):
    area_sqm = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "面積（㎡）"}
        ),
        label="清掃面積（㎡）",
    )
    cleaning_type = forms.MultipleChoiceField(
        choices=[
            ("floor", "床清掃"),
            ("window", "窓清掃"),
            ("toilet", "トイレ清掃"),
            ("kitchen", "キッチン清掃"),
            ("general", "一般清掃"),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="清掃種類",
    )
    equipment_needed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="特殊機材必要",
    )

    def save(self, commit=True):
        project = super().save(commit=False)
        project.project_type = ProjectType.objects.get(name="クリーニング")
        project.details = {
            "area_sqm": float(self.cleaned_data["area_sqm"]),
            "cleaning_type": self.cleaned_data["cleaning_type"],
            "equipment_needed": self.cleaned_data["equipment_needed"],
        }
        if commit:
            project.save()
        return project


class GeneralProjectForm(BaseProjectForm):
    work_description = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 4, "placeholder": "作業内容を詳しく入力"}
        ),
        label="作業内容",
    )
    required_skills = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "必要なスキル（任意）"}
        ),
        label="必要スキル",
    )

    def __init__(self, *args, project_type=None, selected_customer_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_type = project_type

        # 事前選択された顧客がある場合は初期値に設定
        if selected_customer_id:
            self.fields["customer"].initial = selected_customer_id

    def save(self, commit=True):
        project = super().save(commit=False)
        if self.project_type:
            project.project_type = self.project_type
        project.details = {
            "work_description": self.cleaned_data["work_description"],
            "required_skills": self.cleaned_data["required_skills"],
        }
        if commit:
            project.save()
        return project
