from datetime import date

from django.contrib.auth import get_user_model
from django.core.management import call_command
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
            first_name="Marie",
            last_name="Curie",
            is_teacher=True,
        )
        cls.other_teacher_user = User.objects.create_user(
            email="other-teacher@example.com",
            password="StrongPass123!",
            first_name="Ada",
            last_name="Lovelace",
            is_teacher=True,
        )
        cls.department = Department.objects.create(name="Science", description="Science department")
        cls.other_department = Department.objects.create(name="Languages", description="Languages department")
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
        cls.other_teacher = TeacherProfile.objects.create(
            user=cls.other_teacher_user,
            department=cls.other_department,
            employee_id="TCH-901",
            first_name="Ada",
            last_name="Lovelace",
            email="other-teacher@example.com",
            phone_number="0600012346",
            qualification="PhD",
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
        cls.other_subject = Subject.objects.create(
            department=cls.other_department,
            teacher=cls.other_teacher,
            code="LAN-01",
            name="English",
            credit_hours=3,
            description="English basics",
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

    def create_exam(self, *, teacher=None, subject=None, title="Midterm Physics"):
        return Exam.objects.create(
            title=title,
            subject=subject or self.subject,
            teacher=teacher or self.teacher,
            target_class="Grade 7",
            section="A",
            exam_date=date(2025, 1, 10),
            start_time="10:00",
            end_time="11:00",
            total_marks=100,
            description="Term exam",
        )

    def test_department_creation_view(self):
        response = self.client.post(
            reverse("department_add"),
            {"name": "Mathematics", "description": "Mathematics department"},
        )
        self.assertRedirects(response, reverse("department_list"))
        self.assertTrue(Department.objects.filter(name="Mathematics").exists())

    def test_teacher_creation_view_creates_user_and_profile(self):
        response = self.client.post(
            reverse("teacher_add"),
            {
                "first_name": "Alan",
                "last_name": "Turing",
                "email": "alan@example.com",
                "employee_id": "TCH-902",
                "department": self.department.id,
                "phone_number": "0600012347",
                "qualification": "PhD",
                "hire_date": "2024-10-01",
                "password": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("teacher_list"))
        self.assertTrue(TeacherProfile.objects.filter(email="alan@example.com").exists())
        self.assertTrue(User.objects.get(email="alan@example.com").is_teacher)

    def test_teacher_form_rejects_existing_admin_email(self):
        response = self.client.post(
            reverse("teacher_add"),
            {
                "first_name": "Alan",
                "last_name": "Turing",
                "email": self.admin.email,
                "employee_id": "TCH-903",
                "department": self.department.id,
                "phone_number": "0600012348",
                "qualification": "PhD",
                "hire_date": "2024-10-01",
                "password": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This email is already used by another account.")
        self.assertFalse(TeacherProfile.objects.filter(employee_id="TCH-903").exists())

    def test_teacher_detail_edit_and_delete_flow(self):
        detail_response = self.client.get(reverse("teacher_detail", args=[self.teacher.id]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, self.teacher.full_name)

        response = self.client.post(
            reverse("teacher_edit", args=[self.teacher.id]),
            {
                "first_name": "Marie",
                "last_name": "Curie",
                "email": "faculty-teacher@example.com",
                "employee_id": "TCH-900",
                "department": self.other_department.id,
                "phone_number": "0600012349",
                "qualification": "PhD",
                "hire_date": "2024-09-01",
                "password": "",
            },
        )
        self.assertRedirects(response, reverse("teacher_detail", args=[self.teacher.id]))
        self.teacher.refresh_from_db()
        self.teacher_user.refresh_from_db()
        self.assertEqual(self.teacher.department, self.other_department)
        self.assertEqual(self.teacher.qualification, "PhD")
        self.assertTrue(self.teacher_user.check_password("StrongPass123!"))

        delete_response = self.client.post(reverse("teacher_delete", args=[self.teacher.id]))
        self.assertRedirects(delete_response, reverse("teacher_list"))
        self.assertFalse(TeacherProfile.objects.filter(pk=self.teacher.id).exists())
        self.assertFalse(User.objects.filter(email="faculty-teacher@example.com").exists())

    def test_admin_can_edit_and_delete_department_subject_and_holiday(self):
        holiday = Holiday.objects.create(
            title="National Day",
            start_date=date(2025, 7, 30),
            end_date=date(2025, 7, 30),
            description="Public holiday",
        )

        response = self.client.post(
            reverse("department_edit", args=[self.department.id]),
            {"name": "Natural Sciences", "description": "Updated description"},
        )
        self.assertRedirects(response, reverse("department_list"))
        self.department.refresh_from_db()
        self.assertEqual(self.department.name, "Natural Sciences")

        response = self.client.post(
            reverse("subject_edit", args=[self.subject.id]),
            {
                "department": self.department.id,
                "teacher": self.teacher.id,
                "code": "SCI-01",
                "name": "Advanced Physics",
                "credit_hours": 5,
                "description": "Updated subject",
            },
        )
        self.assertRedirects(response, reverse("subject_list"))
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.name, "Advanced Physics")
        self.assertEqual(self.subject.credit_hours, 5)

        response = self.client.post(
            reverse("holiday_edit", args=[holiday.id]),
            {
                "title": "National Celebration",
                "start_date": "2025-07-30",
                "end_date": "2025-07-31",
                "description": "Updated holiday",
            },
        )
        self.assertRedirects(response, reverse("holiday_calendar"))
        holiday.refresh_from_db()
        self.assertEqual(holiday.title, "National Celebration")

        delete_response = self.client.post(reverse("holiday_delete", args=[holiday.id]))
        self.assertRedirects(delete_response, reverse("holiday_calendar"))
        self.assertFalse(Holiday.objects.filter(pk=holiday.id).exists())

    def test_admin_can_edit_and_delete_timetable_exam_and_result(self):
        entry = TimetableEntry.objects.create(
            subject=self.subject,
            teacher=self.teacher,
            day_of_week="Monday",
            target_class="Grade 7",
            section="A",
            room="B12",
            start_time="08:00",
            end_time="09:00",
        )
        exam = self.create_exam()
        result = ExamResult.objects.create(
            exam=exam,
            student=self.student,
            graded_by=self.teacher,
            marks_obtained="88.50",
            remarks="Great job",
        )

        response = self.client.post(
            reverse("timetable_edit", args=[entry.id]),
            {
                "subject": self.subject.id,
                "teacher": self.teacher.id,
                "day_of_week": "Tuesday",
                "target_class": "Grade 7",
                "section": "A",
                "room": "B14",
                "start_time": "09:00",
                "end_time": "10:00",
            },
        )
        self.assertRedirects(response, reverse("timetable_list"))
        entry.refresh_from_db()
        self.assertEqual(entry.day_of_week, "Tuesday")
        self.assertEqual(entry.room, "B14")

        response = self.client.post(
            reverse("exam_edit", args=[exam.id]),
            {
                "title": "Final Physics",
                "subject": self.subject.id,
                "teacher": self.teacher.id,
                "target_class": "Grade 7",
                "section": "A",
                "exam_date": "2025-01-12",
                "start_time": "10:30",
                "end_time": "11:30",
                "total_marks": 120,
                "description": "Updated exam",
            },
        )
        self.assertRedirects(response, reverse("exam_list"))
        exam.refresh_from_db()
        self.assertEqual(exam.title, "Final Physics")
        self.assertEqual(exam.total_marks, 120)

        response = self.client.post(
            reverse("result_edit", args=[result.id]),
            {
                "exam": exam.id,
                "student": self.student.id,
                "graded_by": self.teacher.id,
                "marks_obtained": "91.00",
                "remarks": "Excellent",
            },
        )
        self.assertRedirects(response, reverse("result_list"))
        result.refresh_from_db()
        self.assertEqual(float(result.marks_obtained), 91.0)
        self.assertEqual(result.remarks, "Excellent")

        response = self.client.post(reverse("result_delete", args=[result.id]))
        self.assertRedirects(response, reverse("result_list"))
        self.assertFalse(ExamResult.objects.filter(pk=result.id).exists())

        response = self.client.post(reverse("exam_delete", args=[exam.id]))
        self.assertRedirects(response, reverse("exam_list"))
        self.assertFalse(Exam.objects.filter(pk=exam.id).exists())

        response = self.client.post(reverse("timetable_delete", args=[entry.id]))
        self.assertRedirects(response, reverse("timetable_list"))
        self.assertFalse(TimetableEntry.objects.filter(pk=entry.id).exists())

    def test_teacher_can_manage_only_their_own_exam_and_result(self):
        own_exam = self.create_exam(teacher=self.teacher, subject=self.subject, title="Own Exam")
        own_result = ExamResult.objects.create(
            exam=own_exam,
            student=self.student,
            graded_by=self.teacher,
            marks_obtained="85.00",
            remarks="Solid work",
        )
        other_exam = self.create_exam(
            teacher=self.other_teacher,
            subject=self.other_subject,
            title="Other Exam",
        )
        other_result = ExamResult.objects.create(
            exam=other_exam,
            student=self.student,
            graded_by=self.other_teacher,
            marks_obtained="70.00",
            remarks="Needs work",
        )

        self.client.force_login(self.teacher_user)

        response = self.client.get(reverse("exam_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View only")

        response = self.client.post(
            reverse("exam_edit", args=[own_exam.id]),
            {
                "title": "Own Exam Updated",
                "subject": self.subject.id,
                "teacher": self.teacher.id,
                "target_class": "Grade 7",
                "section": "A",
                "exam_date": "2025-01-11",
                "start_time": "10:15",
                "end_time": "11:15",
                "total_marks": 100,
                "description": "Updated by owner",
            },
        )
        self.assertRedirects(response, reverse("exam_list"))
        own_exam.refresh_from_db()
        self.assertEqual(own_exam.title, "Own Exam Updated")

        response = self.client.post(
            reverse("exam_edit", args=[other_exam.id]),
            {
                "title": "Illegal Update",
                "subject": self.other_subject.id,
                "teacher": self.other_teacher.id,
                "target_class": "Grade 7",
                "section": "A",
                "exam_date": "2025-01-11",
                "start_time": "10:15",
                "end_time": "11:15",
                "total_marks": 100,
                "description": "Illegal update",
            },
        )
        self.assertRedirects(response, reverse("exam_list"))
        other_exam.refresh_from_db()
        self.assertEqual(other_exam.title, "Other Exam")

        response = self.client.post(
            reverse("result_edit", args=[own_result.id]),
            {
                "exam": own_exam.id,
                "student": self.student.id,
                "graded_by": self.teacher.id,
                "marks_obtained": "90.00",
                "remarks": "Updated by owner",
            },
        )
        self.assertRedirects(response, reverse("result_list"))
        own_result.refresh_from_db()
        self.assertEqual(float(own_result.marks_obtained), 90.0)

        response = self.client.post(
            reverse("result_edit", args=[other_result.id]),
            {
                "exam": other_exam.id,
                "student": self.student.id,
                "graded_by": self.other_teacher.id,
                "marks_obtained": "99.00",
                "remarks": "Illegal update",
            },
        )
        self.assertRedirects(response, reverse("result_list"))
        other_result.refresh_from_db()
        self.assertEqual(float(other_result.marks_obtained), 70.0)

    def test_subject_timetable_exam_result_and_holiday_creation_flows(self):
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

    def test_seed_demo_data_command_is_idempotent(self):
        if not User.objects.filter(email="student@gmail.com").exists():
            User.objects.create_user(
                email="student@gmail.com",
                password="student",
                is_student=True,
            )
        if not User.objects.filter(email="teachers@gmail.com").exists():
            User.objects.create_user(
                email="teachers@gmail.com",
                password="teacher",
                first_name="Seed",
                last_name="Teacher",
                is_teacher=True,
            )

        call_command("seed_demo_data")
        first_counts = {
            "departments": Department.objects.filter(name="Science").count(),
            "subjects": Subject.objects.filter(code="SCI-DEMO-01").count(),
            "holidays": Holiday.objects.filter(title="Demo Holiday").count(),
            "exams": Exam.objects.filter(title="Demo Science Exam").count(),
            "results": ExamResult.objects.filter(exam__title="Demo Science Exam").count(),
        }

        call_command("seed_demo_data")
        second_counts = {
            "departments": Department.objects.filter(name="Science").count(),
            "subjects": Subject.objects.filter(code="SCI-DEMO-01").count(),
            "holidays": Holiday.objects.filter(title="Demo Holiday").count(),
            "exams": Exam.objects.filter(title="Demo Science Exam").count(),
            "results": ExamResult.objects.filter(exam__title="Demo Science Exam").count(),
        }

        self.assertEqual(first_counts, second_counts)
        self.assertTrue(TeacherProfile.objects.filter(email="teachers@gmail.com").exists())
        self.assertTrue(Student.objects.filter(student_id="STU-DEMO-01").exists())
