from django import forms
from django.contrib.auth.models import User
from .models import (
    ProjectCost,
    ProjectPricing,
    PricingAuditLog,
    Project,
    Assignment,
    MaterialOrder,
)


class ProjectCostForm(forms.ModelForm):
    """案件コスト入力フォーム"""

    class Meta:
        model = ProjectCost
        fields = [
            "craftsman_cost",
            "material_cost",
            "transportation_cost",
            "survey_cost",
            "other_cost",
        ]
        widgets = {
            "craftsman_cost": forms.NumberInput(
                attrs={
                    "class": "form-control cost-input",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0",
                }
            ),
            "material_cost": forms.NumberInput(
                attrs={
                    "class": "form-control cost-input",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0",
                }
            ),
            "transportation_cost": forms.NumberInput(
                attrs={
                    "class": "form-control cost-input",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0",
                }
            ),
            "survey_cost": forms.NumberInput(
                attrs={
                    "class": "form-control cost-input",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0",
                }
            ),
            "other_cost": forms.NumberInput(
                attrs={
                    "class": "form-control cost-input",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        # 既存データがある場合、関連データから自動取得
        if project and not self.instance.pk:
            self.fields["craftsman_cost"].initial = self.get_estimated_craftsman_cost(
                project
            )
            self.fields["material_cost"].initial = self.get_estimated_material_cost(
                project
            )

    def get_estimated_craftsman_cost(self, project):
        """職人費用の見積もりを取得"""
        assignments = Assignment.objects.filter(project=project)
        total_cost = sum(assignment.total_amount or 0 for assignment in assignments)
        return total_cost

    def get_estimated_material_cost(self, project):
        """資材費の見積もりを取得"""
        material_orders = MaterialOrder.objects.filter(project=project)
        total_cost = sum(order.estimated_cost or 0 for order in material_orders)
        return total_cost


class ProjectPricingForm(forms.ModelForm):
    """案件価格設定フォーム"""

    class Meta:
        model = ProjectPricing
        fields = ["base_cost", "margin_rate", "pricing_stage", "notes"]
        widgets = {
            "base_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "margin_rate": forms.NumberInput(
                attrs={
                    "class": "form-control margin-rate-input",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                    "placeholder": "25.0",
                }
            ),
            "pricing_stage": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "マージン設定の理由や特記事項を記入してください",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if project:
            # プロジェクトコストから基準コストを設定
            try:
                project_cost = ProjectCost.objects.get(project=project)
                self.fields["base_cost"].initial = project_cost.total_cost
            except ProjectCost.DoesNotExist:
                self.fields["base_cost"].initial = 0

            # 推奨マージン率を取得
            recommended = ProjectPricing.get_recommended_margin_range(
                project.project_type
            )
            self.fields[
                "margin_rate"
            ].help_text = f"推奨範囲: {recommended['min']}% - {recommended['max']}% (標準: {recommended['standard']}%)"
            self.fields["margin_rate"].initial = recommended["standard"]

        if user:
            self.user = user

    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(self, "user"):
            instance.set_by = self.user
        if commit:
            instance.save()
        return instance


class PricingComparisonForm(forms.Form):
    """価格比較フォーム"""

    base_cost = forms.DecimalField(
        label="基準コスト",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "min": "0"}
        ),
    )
    margin_rates = forms.CharField(
        label="比較マージン率",
        initial="20,25,30",
        help_text="カンマ区切りで複数のマージン率を入力（例: 20,25,30）",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "20,25,30"}
        ),
    )

    def clean_margin_rates(self):
        rates_str = self.cleaned_data["margin_rates"]
        try:
            rates = [float(rate.strip()) for rate in rates_str.split(",")]
            if any(rate < 0 or rate > 100 for rate in rates):
                raise forms.ValidationError("マージン率は0-100%の範囲で入力してください")
            return rates
        except ValueError:
            raise forms.ValidationError("無効なマージン率の形式です")


class ProfitabilitySearchForm(forms.Form):
    """収益性検索フォーム"""

    project_type = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="すべての工種",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    profit_rate_min = forms.DecimalField(
        required=False,
        label="最小利益率(%)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.1",
                "min": "0",
                "placeholder": "0",
            }
        ),
    )
    profit_rate_max = forms.DecimalField(
        required=False,
        label="最大利益率(%)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.1",
                "min": "0",
                "placeholder": "100",
            }
        ),
    )
    pricing_stage = forms.ChoiceField(
        required=False,
        choices=[("", "すべての段階")] + ProjectPricing.PRICING_STAGE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ProjectType

        self.fields["project_type"].queryset = ProjectType.objects.filter(
            is_active=True
        )


class CostEstimationForm(forms.Form):
    """コスト見積もりフォーム"""

    work_area = forms.DecimalField(
        label="作業面積（m²）",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.1",
                "min": "0",
                "placeholder": "0",
            }
        ),
    )
    work_days = forms.IntegerField(
        label="作業日数",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "1", "placeholder": "1"}
        ),
    )
    craftsman_count = forms.IntegerField(
        label="職人数",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "1", "placeholder": "1"}
        ),
    )
    hourly_rate = forms.DecimalField(
        label="時給（円）",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "1",
                "min": "0",
                "placeholder": "3000",
            }
        ),
    )
    daily_hours = forms.IntegerField(
        label="1日作業時間",
        initial=8,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "1", "max": "12", "placeholder": "8"}
        ),
    )
    material_cost_per_sqm = forms.DecimalField(
        label="材料費（円/m²）",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "1",
                "min": "0",
                "placeholder": "1000",
            }
        ),
    )

    def calculate_estimated_cost(self):
        """見積もりコストを計算"""
        if not self.is_valid():
            return None

        data = self.cleaned_data
        craftsman_cost = (
            data["work_days"]
            * data["craftsman_count"]
            * data["daily_hours"]
            * data["hourly_rate"]
        )

        material_cost = 0
        if data["material_cost_per_sqm"]:
            material_cost = data["work_area"] * data["material_cost_per_sqm"]

        return {
            "craftsman_cost": craftsman_cost,
            "material_cost": material_cost,
            "total_cost": craftsman_cost + material_cost,
        }
