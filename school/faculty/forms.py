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
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.order_by("name")
        if self.instance and not self.is_bound:
            self.initial.update(
                {
                    "first_name": self.instance.first_name,
                    "last_name": self.instance.last_name,
                    "email": self.instance.email,
                    "employee_id": self.instance.employee_id,
                    "department": self.instance.department_id,
                    "phone_number": self.instance.phone_number,
                    "qualification": self.instance.qualification,
                    "hire_date": self.instance.hire_date,
                }
            )
        if not self.instance:
            self.fields["password"].required = True
        self._apply_bootstrap()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        user_qs = CustomUser.objects.filter(email__iexact=email)
        if self.instance and self.instance.user_id:
            user_qs = user_qs.exclude(pk=self.instance.user_id)

        existing_user = user_qs.first()
        if existing_user:
            raise forms.ValidationError("This email is already used by another account.")

        profile_qs = TeacherProfile.objects.filter(email__iexact=email)
        if self.instance:
            profile_qs = profile_qs.exclude(pk=self.instance.pk)
        if profile_qs.exists():
            raise forms.ValidationError("A teacher profile with this email already exists.")

        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"]
        qs = TeacherProfile.objects.filter(employee_id=employee_id)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This employee ID is already assigned.")
        return employee_id

    def clean_password(self):
        password = self.cleaned_data["password"]
        if self.instance and self.instance.user is None and not password:
            raise forms.ValidationError("A password is required when creating a linked login account.")
        if password:
            validate_password(password)
        return password

    @transaction.atomic
    def save(self):
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        user = self.instance.user if self.instance else None

        if user is None:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                username=email,
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                is_teacher=True,
                is_admin=False,
                is_student=False,
                is_staff=False,
            )
        else:
            user.email = email
            user.username = email
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.is_teacher = True
            user.is_admin = False
            user.is_student = False
            user.is_staff = False
            if password:
                user.set_password(password)
            user.save()

        profile = self.instance or TeacherProfile()
        profile.user = user
        profile.email = email
        profile.employee_id = self.cleaned_data["employee_id"]
        profile.department = self.cleaned_data["department"]
        profile.first_name = self.cleaned_data["first_name"]
        profile.last_name = self.cleaned_data["last_name"]
        profile.phone_number = self.cleaned_data["phone_number"]
        profile.qualification = self.cleaned_data["qualification"]
        profile.hire_date = self.cleaned_data["hire_date"]
        profile.is_active = True
        profile.save()
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
