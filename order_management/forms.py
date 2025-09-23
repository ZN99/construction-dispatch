from django import forms
from django.utils import timezone
from .models import Project, FixedCost, VariableCost


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['management_no', 'billing_amount', 'amount_difference', 'created_at', 'updated_at']
        widgets = {
            'site_address': forms.Textarea(attrs={'rows': 2}),
            'contractor_address': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'estimate_issued_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_due_date': forms.DateInput(attrs={'type': 'date'}),
            'work_start_date': forms.DateInput(attrs={'type': 'date'}),
            'work_end_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        # 必須項目の設定
        required_fields = [
            'site_name', 'site_address', 'work_type',
            'contractor_name', 'contractor_address',
            'project_manager'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # 諸経費金額は必須でない
        if 'expense_amount_1' in self.fields:
            self.fields['expense_amount_1'].required = False
        if 'expense_amount_2' in self.fields:
            self.fields['expense_amount_2'].required = False


class FixedCostForm(forms.ModelForm):
    """固定費入力フォーム"""

    class Meta:
        model = FixedCost
        fields = ['name', 'cost_type', 'monthly_amount', 'start_date', 'end_date', 'is_active', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '費目名を入力（例：事務所家賃）'
            }),
            'cost_type': forms.Select(attrs={'class': 'form-select'}),
            'monthly_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '月額（円）',
                'min': '0'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '備考があれば入力'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # デフォルト値設定
        if not self.instance.pk:
            self.fields['start_date'].initial = timezone.now().date()
            self.fields['is_active'].initial = True

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError('終了日は開始日より後の日付を選択してください。')

        return cleaned_data


class VariableCostForm(forms.ModelForm):
    """変動費入力フォーム"""

    class Meta:
        model = VariableCost
        fields = ['name', 'cost_type', 'amount', 'incurred_date', 'project', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '費目名を入力（例：交通費、接待費）'
            }),
            'cost_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '金額（円）',
                'min': '0'
            }),
            'incurred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '備考があれば入力'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # デフォルト値設定
        if not self.instance.pk:
            self.fields['incurred_date'].initial = timezone.now().date()

        # プロジェクト選択肢を受注済みのものに限定
        self.fields['project'].queryset = Project.objects.filter(order_status='受注').order_by('-created_at')
        self.fields['project'].empty_label = "関連案件なし（一般経費）"

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('金額は0円より大きい値を入力してください。')
        return amount


class FixedCostFilterForm(forms.Form):
    """固定費フィルタフォーム"""
    cost_type = forms.ChoiceField(
        choices=[('', '全ての種別')] + FixedCost.COST_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.ChoiceField(
        choices=[('', '全て'), ('true', 'アクティブのみ'), ('false', '無効のみ')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class VariableCostFilterForm(forms.Form):
    """変動費フィルタフォーム"""
    cost_type = forms.ChoiceField(
        choices=[('', '全ての種別')] + VariableCost.COST_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(order_status='受注'),
        required=False,
        empty_label="全ての案件",
        widget=forms.Select(attrs={'class': 'form-select'})
    )