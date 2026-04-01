from datetime import date, time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from faculty.models import Department, Exam, ExamResult, Holiday, Subject, TeacherProfile, TimetableEntry
from student.models import Parent, Student


User = get_user_model()


class Command(BaseCommand):
    help = "Create safe demo data for teachers, departments, subjects, timetable, exams, results, and holidays."

    def handle(self, *args, **options):
        teacher_user = User.objects.filter(email="teachers@gmail.com").first()
        if teacher_user is None:
            self.stdout.write(self.style.ERROR("Teacher account teachers@gmail.com does not exist."))
            return

        student_user = User.objects.filter(email="student@gmail.com").first()
        if student_user is None:
            self.stdout.write(self.style.ERROR("Student account student@gmail.com does not exist."))
            return

        department, _ = Department.objects.get_or_create(
            name="Science",
            defaults={"description": "Core science department."},
        )
        teacher_profile, _ = TeacherProfile.objects.get_or_create(
            email=teacher_user.email,
            defaults={
                "user": teacher_user,
                "department": department,
                "employee_id": "TCH-002",
                "first_name": teacher_user.first_name or "Teacher",
                "last_name": teacher_user.last_name or "User",
                "phone_number": "0612345678",
                "qualification": "MSc Education",
                "hire_date": date(2024, 9, 1),
                "is_active": True,
            },
        )
        if teacher_profile.department is None:
            teacher_profile.department = department
            teacher_profile.save(update_fields=["department"])

        parent, _ = Parent.objects.get_or_create(
            father_email="demo.parent@example.com",
            defaults={
                "father_name": "Demo Father",
                "father_occupation": "Engineer",
                "father_mobile": "0601000001",
                "mother_name": "Demo Mother",
                "mother_occupation": "Teacher",
                "mother_mobile": "0601000002",
                "mother_email": "demo.mother@example.com",
                "present_address": "Casablanca",
                "permanent_address": "Casablanca",
            },
        )
        student, _ = Student.objects.get_or_create(
            student_id="STU-DEMO-01",
            defaults={
                "user": student_user,
                "first_name": "Demo",
                "last_name": "Student",
                "gender": "Male",
                "date_of_birth": date(2010, 5, 12),
                "student_class": "Grade 7",
                "joining_date": date(2024, 9, 1),
                "mobile_number": "0601000003",
                "admission_number": "ADM-DEMO-01",
                "section": "A",
                "parent": parent,
            },
        )
        if student.user_id is None:
            student.user = student_user
            student.save(update_fields=["user"])

        subject, _ = Subject.objects.get_or_create(
            code="SCI-DEMO-01",
            defaults={
                "department": department,
                "teacher": teacher_profile,
                "name": "General Science",
                "credit_hours": 3,
                "description": "Demo subject created for showcase data.",
            },
        )
        if subject.teacher_id is None:
            subject.teacher = teacher_profile
            subject.department = department
            subject.save(update_fields=["teacher", "department"])

        TimetableEntry.objects.get_or_create(
            subject=subject,
            day_of_week="Monday",
            target_class="Grade 7",
            section="A",
            start_time=time(8, 0),
            defaults={
                "teacher": teacher_profile,
                "room": "B12",
                "end_time": time(9, 0),
            },
        )

        exam, _ = Exam.objects.get_or_create(
            title="Demo Science Exam",
            subject=subject,
            target_class="Grade 7",
            section="A",
            exam_date=date(2025, 1, 15),
            defaults={
                "teacher": teacher_profile,
                "start_time": time(10, 0),
                "end_time": time(11, 0),
                "total_marks": 100,
                "description": "Demo exam for PDF requirements.",
            },
        )

        ExamResult.objects.get_or_create(
            exam=exam,
            student=student,
            defaults={
                "graded_by": teacher_profile,
                "marks_obtained": 86.5,
                "remarks": "Good performance",
            },
        )

        Holiday.objects.get_or_create(
            title="Demo Holiday",
            start_date=date(2025, 7, 30),
            defaults={
                "end_date": date(2025, 7, 30),
                "description": "Sample holiday entry for demonstration.",
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo academic data is ready."))
