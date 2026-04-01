from django import forms
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from home_auth.models import CustomUser

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
    account_email = forms.EmailField(label="Student Email")
    account_password = forms.CharField(
        label="Student Password",
        widget=forms.PasswordInput(),
        required=False,
        help_text="Leave blank while editing to keep the current password.",
    )

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
        if self.instance and self.instance.pk and self.instance.user_id:
            self.initial["account_email"] = self.instance.user.email
        self.order_fields(
            [
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
                "account_email",
                "account_password",
            ]
        )
        self._apply_bootstrap()

    def clean_account_email(self):
        email = self.cleaned_data["account_email"].lower()
        user_qs = CustomUser.objects.filter(email__iexact=email)
        if self.instance and self.instance.user_id:
            user_qs = user_qs.exclude(pk=self.instance.user_id)
        if user_qs.exists():
            raise forms.ValidationError("This email is already used by another account.")
        return email

    def clean_account_password(self):
        password = self.cleaned_data["account_password"]
        if (not self.instance or not self.instance.user_id) and not password:
            raise forms.ValidationError("A password is required for the student account.")
        if password:
            validate_password(password)
        return password

    @transaction.atomic
    def save(self, commit=True):
        student = super().save(commit=False)
        email = self.cleaned_data["account_email"]
        password = self.cleaned_data["account_password"]
        user = getattr(student, "user", None)

        if user is None:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                username=email,
                first_name=student.first_name,
                last_name=student.last_name,
                is_student=True,
                is_admin=False,
                is_teacher=False,
                is_staff=False,
            )
        else:
            user.email = email
            user.username = email
            user.first_name = student.first_name
            user.last_name = student.last_name
            user.is_student = True
            user.is_admin = False
            user.is_teacher = False
            user.is_staff = False
            if password:
                user.set_password(password)
            user.save()

        student.user = user
        if commit:
            student.save()
        return student
