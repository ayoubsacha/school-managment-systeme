from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import PasswordResetRequest


User = get_user_model()


class AuthenticationFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            email="student-test@example.com",
            password="StrongPass123!",
            first_name="Student",
            is_student=True,
        )
        cls.teacher = User.objects.create_user(
            email="teacher-test@example.com",
            password="StrongPass123!",
            first_name="Teacher",
            is_teacher=True,
        )
        cls.admin = User.objects.create_superuser(
            email="admin-test@example.com",
            password="StrongPass123!",
            first_name="Admin",
        )

    def test_student_login_redirects_to_student_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.student.email, "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("student_dashboard"))

    def test_teacher_login_redirects_to_teacher_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.teacher.email, "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("teacher_dashboard"))

    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.admin.email, "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("admin_dashboard"))

    def test_signup_creates_student_account_with_hashed_password(self):
        response = self.client.post(
            reverse("signup"),
            {
                "first_name": "New",
                "last_name": "Student",
                "email": "new-student@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("student_dashboard"))
        user = User.objects.get(email="new-student@example.com")
        self.assertTrue(user.is_student)
        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_password_reset_flow_updates_password(self):
        response = self.client.post(
            reverse("forgot_password"),
            {"email": self.student.email},
        )
        self.assertEqual(response.status_code, 200)
        reset_request = PasswordResetRequest.objects.get(user=self.student)

        response = self.client.post(
            reverse("reset_password", kwargs={"token": reset_request.token}),
            {"new_password1": "UpdatedPass123!", "new_password2": "UpdatedPass123!"},
        )
        self.assertRedirects(response, reverse("login"))
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password("UpdatedPass123!"))
