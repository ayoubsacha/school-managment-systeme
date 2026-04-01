from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string


def generate_reset_token():
    return get_random_string(32)


class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email field must be set.")

        email = self.normalize_email(email)
        username = extra_fields.pop("username", "") or email
        extra_fields.setdefault("username", username)
        user = self.model(email=email, **extra_fields)
        user.username = username
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_authorized = models.BooleanField(default=False)
    login_token = models.CharField(max_length=6, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_student = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email

    @property
    def role(self):
        if self.is_superuser or self.is_admin:
            return "Admin"
        if self.is_teacher:
            return "Teacher"
        if self.is_student:
            return "Student"
        return "User"

    def dashboard_name(self):
        if self.is_superuser or self.is_admin:
            return "admin_dashboard"
        if self.is_teacher:
            return "teacher_dashboard"
        return "student_dashboard"


class PasswordResetRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_requests",
    )
    email = models.EmailField()
    token = models.CharField(
        max_length=32,
        default=generate_reset_token,
        editable=False,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    TOKEN_VALIDITY_PERIOD = timezone.timedelta(hours=1)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Password reset request"
        verbose_name_plural = "Password reset requests"

    def __str__(self):
        return f"Reset request for {self.email}"

    def is_valid(self):
        return timezone.now() <= self.created_at + self.TOKEN_VALIDITY_PERIOD

    def get_reset_link(self):
        return reverse("reset_password", kwargs={"token": self.token})

    def send_reset_email(self):
        reset_link = self.get_reset_link()
        send_mail(
            "Password Reset Request",
            f"Use this link to reset your password: {reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )
