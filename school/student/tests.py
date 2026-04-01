from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Parent, Student


User = get_user_model()


class StudentViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            email="student-admin@example.com",
            password="StrongPass123!",
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def _student_payload(self):
        return {
            "first_name": "Jane",
            "last_name": "Doe",
            "student_id": "STU-100",
            "gender": "Female",
            "date_of_birth": "2010-02-10",
            "student_class": "Grade 8",
            "joining_date": "2024-09-01",
            "mobile_number": "0600000000",
            "admission_number": "ADM-100",
            "section": "A",
            "account_email": "jane.doe@example.com",
            "account_password": "StrongPass123!",
            "father_name": "John Doe",
            "father_occupation": "Engineer",
            "father_mobile": "0600000001",
            "father_email": "father@example.com",
            "mother_name": "Sarah Doe",
            "mother_occupation": "Doctor",
            "mother_mobile": "0600000002",
            "mother_email": "mother@example.com",
            "present_address": "City Center",
            "permanent_address": "City Center",
        }

    def test_add_student_creates_student_and_parent(self):
        initial_student_count = Student.objects.count()
        initial_parent_count = Parent.objects.count()
        initial_user_count = User.objects.count()
        response = self.client.post(reverse("add_student"), self._student_payload())
        self.assertRedirects(response, reverse("student_list"))
        self.assertEqual(Student.objects.count(), initial_student_count + 1)
        self.assertEqual(Parent.objects.count(), initial_parent_count + 1)
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        student = Student.objects.get(student_id="STU-100")
        self.assertEqual(student.user.email, "jane.doe@example.com")
        self.assertTrue(student.user.check_password("StrongPass123!"))

    def test_edit_student_updates_existing_record(self):
        student_user = User.objects.create_user(
            email="old-student@example.com",
            password="StrongPass123!",
            is_student=True,
        )
        parent = Parent.objects.create(
            father_name="Old Father",
            father_occupation="Teacher",
            father_mobile="0600000100",
            father_email="old-father@example.com",
            mother_name="Old Mother",
            mother_occupation="Teacher",
            mother_mobile="0600000101",
            mother_email="old-mother@example.com",
            present_address="Old Address",
            permanent_address="Old Address",
        )
        student = Student.objects.create(
            first_name="Old",
            last_name="Name",
            student_id="STU-101",
            gender="Male",
            date_of_birth="2010-01-01",
            student_class="Grade 7",
            joining_date="2024-09-01",
            mobile_number="0600000102",
            admission_number="ADM-101",
            section="B",
            user=student_user,
            parent=parent,
        )

        payload = self._student_payload()
        payload["student_id"] = student.student_id
        payload["admission_number"] = student.admission_number
        payload["first_name"] = "Updated"
        payload["account_email"] = "updated-student@example.com"
        payload["account_password"] = ""

        response = self.client.post(
            reverse("edit_student", kwargs={"student_id": student.student_id}),
            payload,
        )

        self.assertRedirects(
            response,
            reverse("view_student", kwargs={"student_id": student.student_id}),
        )
        student.refresh_from_db()
        student_user.refresh_from_db()
        self.assertEqual(student.first_name, "Updated")
        self.assertEqual(student.user.email, "updated-student@example.com")
        self.assertTrue(student_user.check_password("StrongPass123!"))

    def test_delete_student_removes_linked_parent(self):
        student_user = User.objects.create_user(
            email="delete-student@example.com",
            password="StrongPass123!",
            is_student=True,
        )
        parent = Parent.objects.create(
            father_name="Delete Father",
            father_occupation="Teacher",
            father_mobile="0600000200",
            father_email="delete-father@example.com",
            mother_name="Delete Mother",
            mother_occupation="Teacher",
            mother_mobile="0600000201",
            mother_email="delete-mother@example.com",
            present_address="Delete Address",
            permanent_address="Delete Address",
        )
        student = Student.objects.create(
            first_name="Delete",
            last_name="Me",
            student_id="STU-102",
            gender="Male",
            date_of_birth="2010-01-01",
            student_class="Grade 7",
            joining_date="2024-09-01",
            mobile_number="0600000202",
            admission_number="ADM-102",
            section="B",
            user=student_user,
            parent=parent,
        )

        response = self.client.post(
            reverse("delete_student", kwargs={"student_id": student.student_id})
        )
        self.assertRedirects(response, reverse("student_list"))
        self.assertFalse(Student.objects.filter(student_id="STU-102").exists())
        self.assertFalse(Parent.objects.filter(id=parent.id).exists())
        self.assertFalse(User.objects.filter(email="delete-student@example.com").exists())
