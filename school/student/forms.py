from django import forms

from .models import Parent, Student


class BootstrapMixin:
    def _apply_bootstrap(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} form-control".strip()


class ParentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Parent
        fields = [
            "father_name",
            "father_occupation",
            "father_mobile",
            "father_email",
            "mother_name",
            "mother_occupation",
            "mother_mobile",
            "mother_email",
            "present_address",
            "permanent_address",
        ]
        widgets = {
            "present_address": forms.Textarea(attrs={"rows": 3}),
            "permanent_address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class StudentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "student_id",
            "gender",
            "date_of_birth",
            "student_class",
            "joining_date",
            "mobile_number",
            "admission_number",
            "section",
            "student_image",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "joining_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
