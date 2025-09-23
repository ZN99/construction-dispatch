from django import forms
from .models import Contractor, Subcontract


class ContractorForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = [
            'name', 'contractor_type', 'address', 'contact_person',
            'phone', 'email', 'specialties', 'hourly_rate', 'is_active',
            'bank_name', 'branch_name', 'account_type', 'account_number',
            'account_holder', 'payment_day', 'payment_cycle'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'specialties': forms.Textarea(attrs={'rows': 3}),
            'hourly_rate': forms.NumberInput(attrs={'step': '1'}),
            'payment_day': forms.NumberInput(attrs={'min': '1', 'max': '31'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        # 必須項目の設定
        required_fields = ['name', 'contractor_type', 'address']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True


class SubcontractForm(forms.ModelForm):
    class Meta:
        model = Subcontract
        exclude = [
            'project', 'management_no', 'site_name', 'site_address',
            'total_material_cost', 'created_at', 'updated_at'
        ]
        widgets = {
            'payment_due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'work_description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        # 外注先を有効なもののみに限定
        self.fields['contractor'].queryset = Contractor.objects.filter(is_active=True)

        # 必須項目の設定
        required_fields = ['contractor', 'contract_amount']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # フィールドラベルの設定
        self.fields['billed_amount'].help_text = '実際に請求された金額を入力してください'
        self.fields['contract_amount'].help_text = '当初の契約金額を入力してください'