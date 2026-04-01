from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="teacher_profile",
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        related_name="teachers",
        null=True,
        blank=True,
    )
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    qualification = models.CharField(max_length=255)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Subject(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        related_name="subjects",
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    credit_hours = models.PositiveSmallIntegerField(default=3)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["department", "name"],
                name="faculty_subject_department_id_name_baa88039_uniq",
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class TimetableEntry(models.Model):
    DAY_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="timetable_entries",
    )
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        related_name="timetable_entries",
        null=True,
        blank=True,
    )
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    target_class = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    room = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["day_of_week", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["day_of_week", "target_class", "section", "start_time"],
                name="faculty_timetableentry_day_of_week_target_class_section_start_time_08f15d48_uniq",
            )
        ]

    def __str__(self):
        return f"{self.subject} - {self.day_of_week} {self.start_time}"


class Exam(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exams",
    )
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        related_name="exams",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=150)
    target_class = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_marks = models.PositiveIntegerField(default=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["exam_date", "start_time"]

    def __str__(self):
        return self.title


class ExamResult(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="results",
    )
    student = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        related_name="exam_results",
    )
    graded_by = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        related_name="graded_results",
        null=True,
        blank=True,
    )
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "student"],
                name="faculty_examresult_exam_id_student_id_f56d79ff_uniq",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.exam}"

    @property
    def percentage(self):
        if not self.exam.total_marks:
            return 0
        return round((float(self.marks_obtained) / self.exam.total_marks) * 100, 2)


class Holiday(models.Model):
    title = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["start_date", "title"]

    def __str__(self):
        return self.title
