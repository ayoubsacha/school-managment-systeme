from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from home_auth.decorators import role_required

from student.models import Student

from .forms import (
    DepartmentForm,
    ExamForm,
    ExamResultForm,
    HolidayForm,
    SubjectForm,
    TeacherCreateForm,
    TimetableEntryForm,
)
from .models import Department, Exam, ExamResult, Holiday, Subject, TeacherProfile, TimetableEntry


DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def index(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser or user.is_admin:
        return redirect("admin_dashboard")
    if user.is_teacher:
        return redirect("teacher_dashboard")
    return redirect("student_dashboard")


@role_required("admin")
def admin_dashboard(request):
    context = {
        "stats": {
            "students": Student.objects.count(),
            "teachers": TeacherProfile.objects.count(),
            "departments": Department.objects.count(),
            "subjects": Subject.objects.count(),
            "exams": Exam.objects.count(),
            "holidays": Holiday.objects.count(),
        },
        "latest_timetable_entries": TimetableEntry.objects.select_related("subject", "teacher")[:5],
        "latest_exams": Exam.objects.select_related("subject", "teacher")[:5],
        "department_breakdown": Department.objects.annotate(total_subjects=Count("subjects"))[:5],
    }
    return render(request, "Home/index.html", context)


@role_required("teacher")
def teacher_dashboard(request):
    teacher_profile = getattr(request.user, "teacher_profile", None)
    context = {
        "teacher_profile": teacher_profile,
        "subjects": Subject.objects.filter(teacher=teacher_profile).select_related("department"),
        "timetable_entries": TimetableEntry.objects.filter(teacher=teacher_profile).select_related("subject")[:10],
        "exams": Exam.objects.filter(teacher=teacher_profile).select_related("subject")[:10],
        "holidays": Holiday.objects.all()[:5],
    }
    return render(request, "faculty/teacher-dashboard.html", context)


@role_required("student", "admin", "teacher")
def student_dashboard(request):
    context = {
        "student_count": Student.objects.count(),
        "upcoming_exams": Exam.objects.select_related("subject").all()[:5],
        "recent_results": ExamResult.objects.select_related("exam", "student").all()[:5],
        "timetable_entries": TimetableEntry.objects.select_related("subject", "teacher").all()[:6],
        "holidays": Holiday.objects.all()[:5],
    }
    return render(request, "students/student-dashboard.html", context)


@login_required
def department_list(request):
    departments = Department.objects.prefetch_related("subjects", "teachers").all()
    return render(request, "faculty/department-list.html", {"departments": departments})


@role_required("admin")
def department_add(request):
    form = DepartmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        department = form.save()
        messages.success(request, f"{department.name} department created successfully.")
        return redirect("department_list")
    return render(request, "faculty/department-form.html", {"form": form})


@login_required
def teacher_list(request):
    teachers = TeacherProfile.objects.select_related("department", "user").all()
    return render(request, "faculty/teacher-list.html", {"teachers": teachers})


@role_required("admin")
def teacher_add(request):
    form = TeacherCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        teacher = form.save()
        messages.success(request, f"{teacher.full_name} was added successfully.")
        return redirect("teacher_list")
    return render(request, "faculty/teacher-form.html", {"form": form})


@login_required
def subject_list(request):
    subjects = Subject.objects.select_related("department", "teacher").all()
    return render(request, "faculty/subject-list.html", {"subjects": subjects})


@role_required("admin")
def subject_add(request):
    form = SubjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        subject = form.save()
        messages.success(request, f"{subject.name} was added successfully.")
        return redirect("subject_list")
    return render(request, "faculty/subject-form.html", {"form": form})


@login_required
def timetable_list(request):
    entries = TimetableEntry.objects.select_related("subject", "teacher").all()
    return render(request, "faculty/timetable-list.html", {"entries": entries})


@role_required("admin")
def timetable_add(request):
    form = TimetableEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save()
        messages.success(request, f"Timetable entry for {entry.subject.name} was created.")
        return redirect("timetable_list")
    return render(request, "faculty/timetable-form.html", {"form": form})


@login_required
def visual_timetable(request):
    timetable = OrderedDict((day, []) for day in DAY_ORDER)
    entries = TimetableEntry.objects.select_related("subject", "teacher").all()
    for entry in entries:
        timetable.setdefault(entry.day_of_week, []).append(entry)
    return render(request, "faculty/visual-timetable.html", {"timetable": timetable})


@login_required
def exam_list(request):
    exams = Exam.objects.select_related("subject", "teacher").all()
    return render(request, "faculty/exam-list.html", {"exams": exams})


@role_required("admin", "teacher")
def exam_add(request):
    form = ExamForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        exam = form.save()
        messages.success(request, f"{exam.title} has been scheduled.")
        return redirect("exam_list")
    return render(request, "faculty/exam-form.html", {"form": form})


@login_required
def result_list(request):
    results = ExamResult.objects.select_related("exam", "student", "graded_by").all()
    return render(request, "faculty/result-list.html", {"results": results})


@role_required("admin", "teacher")
def result_add(request):
    form = ExamResultForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        result = form.save()
        messages.success(
            request,
            f"Grade saved for {result.student.full_name} in {result.exam.title}.",
        )
        return redirect("result_list")
    return render(request, "faculty/result-form.html", {"form": form})


@login_required
def holiday_calendar(request):
    holidays = Holiday.objects.all()
    return render(request, "faculty/holiday-calendar.html", {"holidays": holidays})


@role_required("admin")
def holiday_add(request):
    form = HolidayForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        holiday = form.save()
        messages.success(request, f"{holiday.title} holiday was added.")
        return redirect("holiday_calendar")
    return render(request, "faculty/holiday-form.html", {"form": form})
