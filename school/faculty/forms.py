from django import forms
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from home_auth.models import CustomUser

from .models import Department, Exam, ExamResult, Holiday, Subject, TeacherProfile, TimetableEntry


class BootstrapMixin:
    def _apply_bootstrap(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} form-control".strip()


class DepartmentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class TeacherCreateForm(BootstrapMixin, forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    employee_id = forms.CharField(max_length=20)
    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=False)
    phone_number = forms.CharField(max_length=20)
    qualification = forms.CharField(max_length=255)
    hire_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.order_by("name")
        self._apply_bootstrap()

    def clean_email(self):
        return self.cleaned_data["email"].lower()

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    @transaction.atomic
    def save(self):
        email = self.cleaned_data["email"]
        user, _ = CustomUser.objects.update_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": self.cleaned_data["first_name"],
                "last_name": self.cleaned_data["last_name"],
                "is_teacher": True,
                "is_admin": False,
                "is_student": False,
                "is_staff": False,
            },
        )
        user.set_password(self.cleaned_data["password"])
        user.save()

        profile, _ = TeacherProfile.objects.update_or_create(
            email=email,
            defaults={
                "user": user,
                "employee_id": self.cleaned_data["employee_id"],
                "department": self.cleaned_data["department"],
                "first_name": self.cleaned_data["first_name"],
                "last_name": self.cleaned_data["last_name"],
                "phone_number": self.cleaned_data["phone_number"],
                "qualification": self.cleaned_data["qualification"],
                "hire_date": self.cleaned_data["hire_date"],
                "is_active": True,
            },
        )
        return profile


class SubjectForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["department", "teacher", "code", "name", "credit_hours", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class TimetableEntryForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = [
            "subject",
            "teacher",
            "day_of_week",
            "target_class",
            "section",
            "room",
            "start_time",
            "end_time",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and start_time >= end_time:
            self.add_error("end_time", "End time must be after start time.")
        return cleaned_data


class ExamForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "title",
            "subject",
            "teacher",
            "target_class",
            "section",
            "exam_date",
            "start_time",
            "end_time",
            "total_marks",
            "description",
        ]
        widgets = {
            "exam_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and start_time >= end_time:
            self.add_error("end_time", "End time must be after start time.")
        return cleaned_data


class ExamResultForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ["exam", "student", "graded_by", "marks_obtained", "remarks"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        exam = cleaned_data.get("exam")
        marks_obtained = cleaned_data.get("marks_obtained")
        if exam and marks_obtained is not None and marks_obtained > exam.total_marks:
            self.add_error("marks_obtained", "Marks obtained cannot exceed the exam total.")
        return cleaned_data


class HolidayForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ["title", "start_date", "end_date", "description"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date > end_date:
            self.add_error("end_date", "End date must be on or after the start date.")
        return cleaned_data
