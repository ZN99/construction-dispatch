from django import forms
from django.contrib.auth.models import User
from .models import Supplier, MaterialOrder, Project, ProjectType


class SupplierSearchForm(forms.Form):
    """業者検索フォーム"""

    name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "業者名"}),
    )
    project_type = forms.ModelChoiceField(
        required=False,
        queryset=ProjectType.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class SupplierForm(forms.ModelForm):
    """業者登録・編集フォーム"""

    class Meta:
        model = Supplier
        fields = [
            "name",
            "contact_person",
            "phone",
            "email",
            "address",
            "specialties",
            "payment_terms",
            "delivery_area",
            "notes",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "specialties": forms.CheckboxSelectMultiple(),
            "payment_terms": forms.TextInput(attrs={"class": "form-control"}),
            "delivery_area": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MaterialOrderForm(forms.ModelForm):
    """資材発注フォーム"""

    class Meta:
        model = MaterialOrder
        fields = [
            "project",
            "supplier",
            "order_details",
            "estimated_cost",
            "delivery_date",
            "delivery_address",
            "contact_person",
            "contact_phone",
            "notes",
        ]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "order_details": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "必要な資材・数量・仕様などを詳しく記載してください。\n\n例：\n- 壁紙（クロス）: 50m²\n- 床材（フローリング）: 30m²\n- ペイント（白色）: 10L\n- その他必要工具・消耗品",
                }
            ),
            "estimated_cost": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "delivery_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "delivery_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        project_id = kwargs.pop("project_id", None)
        super().__init__(*args, **kwargs)

        # プロジェクトが指定されている場合は自動選択
        if project_id:
            self.fields["project"].initial = project_id

        # プロジェクトに基づいて業者をフィルタリング
        project = None
        if hasattr(self.instance, "project") and self.instance.project:
            project = self.instance.project
        elif project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                pass

        if project:
            self.fields["supplier"].queryset = Supplier.objects.filter(
                specialties=project.project_type, is_active=True
            )

            # 納品先住所をプロジェクト住所で初期化
            if not self.instance.delivery_address:
                self.fields["delivery_address"].initial = project.address

        # ユーザーを自動設定
        if user and not getattr(self.instance, "ordered_by", None):
            self.initial["ordered_by"] = user


class MaterialOrderStatusForm(forms.ModelForm):
    """発注ステータス更新フォーム"""

    class Meta:
        model = MaterialOrder
        fields = ["status", "actual_cost", "actual_delivery_date", "notes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "actual_cost": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "actual_delivery_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class MaterialOrderSearchForm(forms.Form):
    """発注検索フォーム"""

    project = forms.ModelChoiceField(
        required=False,
        queryset=Project.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    supplier = forms.ModelChoiceField(
        required=False,
        queryset=Supplier.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "すべて")] + MaterialOrder.ORDER_STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    order_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    order_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    overdue_only = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
