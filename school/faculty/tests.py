from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from student.models import Parent, Student

from .models import Department, Exam, ExamResult, Holiday, Subject, TeacherProfile, TimetableEntry


User = get_user_model()


class FacultyManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            email="faculty-admin@example.com",
            password="StrongPass123!",
        )
        cls.teacher_user = User.objects.create_user(
            email="faculty-teacher@example.com",
            password="StrongPass123!",
            is_teacher=True,
        )
        cls.department = Department.objects.create(name="Science", description="Science department")
        cls.teacher = TeacherProfile.objects.create(
            user=cls.teacher_user,
            department=cls.department,
            employee_id="TCH-900",
            first_name="Marie",
            last_name="Curie",
            email="faculty-teacher@example.com",
            phone_number="0600012345",
            qualification="MSc",
            hire_date=date(2024, 9, 1),
        )
        cls.subject = Subject.objects.create(
            department=cls.department,
            teacher=cls.teacher,
            code="SCI-01",
            name="Physics",
            credit_hours=4,
            description="Physics basics",
        )
        parent = Parent.objects.create(
            father_name="Result Father",
            father_occupation="Engineer",
            father_mobile="0600099001",
            father_email="result-father@example.com",
            mother_name="Result Mother",
            mother_occupation="Architect",
            mother_mobile="0600099002",
            mother_email="result-mother@example.com",
            present_address="Main Street",
            permanent_address="Main Street",
        )
        cls.student = Student.objects.create(
            first_name="Lina",
            last_name="Student",
            student_id="STU-500",
            gender="Female",
            date_of_birth=date(2011, 1, 1),
            student_class="Grade 7",
            joining_date=date(2024, 9, 1),
            mobile_number="0600099003",
            admission_number="ADM-500",
            section="A",
            parent=parent,
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_department_creation_view(self):
        response = self.client.post(
            reverse("department_add"),
            {"name": "Languages", "description": "Languages department"},
        )
        self.assertRedirects(response, reverse("department_list"))
        self.assertTrue(Department.objects.filter(name="Languages").exists())

    def test_teacher_creation_view_creates_user_and_profile(self):
        response = self.client.post(
            reverse("teacher_add"),
            {
                "first_name": "Alan",
                "last_name": "Turing",
                "email": "alan@example.com",
                "employee_id": "TCH-901",
                "department": self.department.id,
                "phone_number": "0600012346",
                "qualification": "PhD",
                "hire_date": "2024-10-01",
                "password": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("teacher_list"))
        self.assertTrue(TeacherProfile.objects.filter(email="alan@example.com").exists())
        self.assertTrue(User.objects.get(email="alan@example.com").is_teacher)

    def test_subject_timetable_exam_result_and_holiday_flows(self):
        response = self.client.post(
            reverse("timetable_add"),
            {
                "subject": self.subject.id,
                "teacher": self.teacher.id,
                "day_of_week": "Monday",
                "target_class": "Grade 7",
                "section": "A",
                "room": "B12",
                "start_time": "08:00",
                "end_time": "09:00",
            },
        )
        self.assertRedirects(response, reverse("timetable_list"))
        self.assertEqual(TimetableEntry.objects.count(), 1)

        response = self.client.post(
            reverse("exam_add"),
            {
                "title": "Midterm Physics",
                "subject": self.subject.id,
                "teacher": self.teacher.id,
                "target_class": "Grade 7",
                "section": "A",
                "exam_date": "2025-01-10",
                "start_time": "10:00",
                "end_time": "11:00",
                "total_marks": 100,
                "description": "Term exam",
            },
        )
        self.assertRedirects(response, reverse("exam_list"))
        exam = Exam.objects.get(title="Midterm Physics")

        response = self.client.post(
            reverse("result_add"),
            {
                "exam": exam.id,
                "student": self.student.id,
                "graded_by": self.teacher.id,
                "marks_obtained": "88.50",
                "remarks": "Great job",
            },
        )
        self.assertRedirects(response, reverse("result_list"))
        self.assertEqual(ExamResult.objects.count(), 1)

        response = self.client.post(
            reverse("holiday_add"),
            {
                "title": "National Day",
                "start_date": "2025-07-30",
                "end_date": "2025-07-30",
                "description": "Public holiday",
            },
        )
        self.assertRedirects(response, reverse("holiday_calendar"))
        self.assertTrue(Holiday.objects.filter(title="National Day").exists())

    def test_visual_timetable_page_renders(self):
        TimetableEntry.objects.create(
            subject=self.subject,
            teacher=self.teacher,
            day_of_week="Tuesday",
            target_class="Grade 7",
            section="A",
            room="B14",
            start_time="09:00",
            end_time="10:00",
        )
        response = self.client.get(reverse("visual_timetable"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visual Timetable")
