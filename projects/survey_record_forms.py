from django import forms
from .models import SurveyReport, SurveyPhoto, Survey, Surveyor


class SurveyRecordForm(forms.ModelForm):
    class Meta:
        model = SurveyReport
        fields = [
            "actual_area",
            "access_notes",
            "special_requirements",
            "wall_condition",
            "floor_condition",
            "ceiling_condition",
            "electrical_condition",
            "room_temperature",
            "humidity_level",
            "ventilation_quality",
            "surveyor_notes",
            "estimated_work_days",
            "difficulty_level",
            "assignment_notes",
        ]
        widgets = {
            "actual_area": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "実測面積（㎡）",
                    "step": "0.01",
                }
            ),
            "access_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "駐車場、搬入経路、エレベーター等のアクセス情報",
                }
            ),
            "special_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "家具移動、養生、時間制約等の特殊要件",
                }
            ),
            "wall_condition": forms.Select(attrs={"class": "form-select"}),
            "floor_condition": forms.Select(attrs={"class": "form-select"}),
            "ceiling_condition": forms.Select(attrs={"class": "form-select"}),
            "electrical_condition": forms.Select(attrs={"class": "form-select"}),
            "room_temperature": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "室温（℃）"}
            ),
            "humidity_level": forms.Select(attrs={"class": "form-select"}),
            "ventilation_quality": forms.Select(attrs={"class": "form-select"}),
            "surveyor_notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "調査員のメモ・所感"}
            ),
            "estimated_work_days": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "想定作業日数"}
            ),
            "difficulty_level": forms.Select(attrs={"class": "form-select"}),
            "assignment_notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "職人選定向けのメモ"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # モバイル対応のためのクラス追加
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"data-mobile-optimized": "true"})


class SurveyPhotoUploadForm(forms.ModelForm):
    class Meta:
        model = SurveyPhoto
        fields = ["photo", "location", "description"]
        widgets = {
            "photo": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                    "capture": "environment",  # モバイルでカメラを直接起動
                }
            ),
            "location": forms.Select(attrs={"class": "form-select"}),
            "description": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "写真の説明"}
            ),
        }


class SurveyStartForm(forms.Form):
    survey = forms.ModelChoiceField(
        queryset=Survey.objects.filter(status="scheduled"),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="調査案件",
    )
    surveyor = forms.ModelChoiceField(
        queryset=Surveyor.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="調査員",
    )

    def __init__(self, *args, **kwargs):
        surveyor_id = kwargs.pop("surveyor_id", None)
        super().__init__(*args, **kwargs)

        if surveyor_id:
            self.fields["surveyor"].initial = surveyor_id
            # その調査員にアサインされた案件のみ表示
            self.fields["survey"].queryset = Survey.objects.filter(
                surveyor_id=surveyor_id, status="scheduled"
            ).select_related("project", "project__customer")


class SurveyCompletionForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("completed", "完了"), ("partial", "部分完了"), ("rescheduled", "再調整が必要")],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="調査ステータス",
    )
    completion_notes = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "placeholder": "完了時のメモ"}
        ),
        required=False,
        label="完了メモ",
    )


class QuickPhotoForm(forms.Form):
    photo = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
                "capture": "environment",
            }
        )
    )
    location = forms.ChoiceField(
        choices=SurveyPhoto.LOCATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    description = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "写真の説明"}),
        required=False,
    )


class VoiceMemoForm(forms.Form):
    memo_description = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "音声メモの内容を簡単に説明"}
        ),
        label="メモの説明",
    )
    voice_file = forms.FileField(
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "audio/*"}),
        label="音声ファイル",
    )
