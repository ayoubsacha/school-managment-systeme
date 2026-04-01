from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser


class BootstrapMixin:
    def _apply_bootstrap(self):
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} form-control".strip()


class LoginForm(BootstrapMixin, forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class SignUpForm(BootstrapMixin, forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")

        if password1:
            validate_password(password1)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.username = user.email
        user.is_student = True
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ForgotPasswordForm(BootstrapMixin, forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class ResetPasswordForm(BootstrapMixin, forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "Passwords do not match.")

        if password1:
            validate_password(password1)

        return cleaned_data
