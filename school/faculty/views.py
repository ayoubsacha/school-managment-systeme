from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

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


def teacher_profile_for_user(user):
    return getattr(user, "teacher_profile", None)


def user_is_admin(user):
    return user.is_superuser or user.is_admin


def can_manage_exam(user, exam):
    teacher_profile = teacher_profile_for_user(user)
    return user_is_admin(user) or (
        user.is_teacher and teacher_profile and exam.teacher_id == teacher_profile.id
    )


def can_manage_result(user, result):
    teacher_profile = teacher_profile_for_user(user)
    return user_is_admin(user) or (
        user.is_teacher
        and teacher_profile
        and (result.graded_by_id == teacher_profile.id or result.exam.teacher_id == teacher_profile.id)
    )


def restrict_exam_form_for_teacher(form, teacher_profile):
    form.fields["teacher"].queryset = TeacherProfile.objects.filter(pk=teacher_profile.pk)
    form.fields["teacher"].initial = teacher_profile.pk
    form.fields["subject"].queryset = Subject.objects.filter(teacher=teacher_profile)


def restrict_result_form_for_teacher(form, teacher_profile):
    form.fields["graded_by"].queryset = TeacherProfile.objects.filter(pk=teacher_profile.pk)
    form.fields["graded_by"].initial = teacher_profile.pk
    form.fields["exam"].queryset = Exam.objects.filter(teacher=teacher_profile)


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
    teacher_profile = teacher_profile_for_user(request.user)
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
    return render(
        request,
        "faculty/department-form.html",
        {"form": form, "page_heading": "Add Department", "submit_label": "Save Department"},
    )


@role_required("admin")
def department_edit(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{department.name} department updated successfully.")
        return redirect("department_list")
    return render(
        request,
        "faculty/department-form.html",
        {"form": form, "page_heading": "Edit Department", "submit_label": "Update Department"},
    )


@role_required("admin")
def department_delete(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.method == "POST":
        department_name = department.name
        department.delete()
        messages.success(request, f"{department_name} department deleted successfully.")
    return redirect("department_list")


@login_required
def teacher_list(request):
    teachers = TeacherProfile.objects.select_related("department", "user").all()
    return render(request, "faculty/teacher-list.html", {"teachers": teachers})


@login_required
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(
        TeacherProfile.objects.select_related("department", "user"),
        pk=teacher_id,
    )
    return render(request, "faculty/teacher-detail.html", {"teacher": teacher})


@role_required("admin")
def teacher_add(request):
    form = TeacherCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        teacher = form.save()
        messages.success(request, f"{teacher.full_name} was added successfully.")
        return redirect("teacher_list")
    return render(
        request,
        "faculty/teacher-form.html",
        {
            "form": form,
            "page_heading": "Add Teacher",
            "submit_label": "Save Teacher",
        },
    )


@role_required("admin")
def teacher_edit(request, teacher_id):
    teacher = get_object_or_404(
        TeacherProfile.objects.select_related("department", "user"),
        pk=teacher_id,
    )
    form = TeacherCreateForm(request.POST or None, instance=teacher)
    if request.method == "POST" and form.is_valid():
        teacher = form.save()
        messages.success(request, f"{teacher.full_name} was updated successfully.")
        return redirect("teacher_detail", teacher_id=teacher.pk)
    return render(
        request,
        "faculty/teacher-form.html",
        {
            "form": form,
            "page_heading": "Edit Teacher",
            "submit_label": "Update Teacher",
            "show_password_help": True,
        },
    )


@role_required("admin")
def teacher_delete(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile.objects.select_related("user"), pk=teacher_id)
    if request.method == "POST":
        teacher_name = teacher.full_name
        user = teacher.user
        with transaction.atomic():
            teacher.delete()
            if user is not None:
                user.delete()
        messages.success(request, f"{teacher_name} was deleted successfully.")
    return redirect("teacher_list")


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
    return render(
        request,
        "faculty/subject-form.html",
        {"form": form, "page_heading": "Add Subject", "submit_label": "Save Subject"},
    )


@role_required("admin")
def subject_edit(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{subject.name} was updated successfully.")
        return redirect("subject_list")
    return render(
        request,
        "faculty/subject-form.html",
        {"form": form, "page_heading": "Edit Subject", "submit_label": "Update Subject"},
    )


@role_required("admin")
def subject_delete(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == "POST":
        subject_name = subject.name
        subject.delete()
        messages.success(request, f"{subject_name} was deleted successfully.")
    return redirect("subject_list")


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
    return render(
        request,
        "faculty/timetable-form.html",
        {"form": form, "page_heading": "Add Timetable Entry", "submit_label": "Save Entry"},
    )


@role_required("admin")
def timetable_edit(request, entry_id):
    entry = get_object_or_404(TimetableEntry, pk=entry_id)
    form = TimetableEntryForm(request.POST or None, instance=entry)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Timetable entry for {entry.subject.name} was updated.")
        return redirect("timetable_list")
    return render(
        request,
        "faculty/timetable-form.html",
        {"form": form, "page_heading": "Edit Timetable Entry", "submit_label": "Update Entry"},
    )


@role_required("admin")
def timetable_delete(request, entry_id):
    entry = get_object_or_404(TimetableEntry.objects.select_related("subject"), pk=entry_id)
    if request.method == "POST":
        subject_name = entry.subject.name
        entry.delete()
        messages.success(request, f"Timetable entry for {subject_name} was deleted.")
    return redirect("timetable_list")


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
    manageable_exam_ids = []
    if request.user.is_teacher and not user_is_admin(request.user):
        teacher_profile = teacher_profile_for_user(request.user)
        if teacher_profile is not None:
            manageable_exam_ids = list(
                Exam.objects.filter(teacher=teacher_profile).values_list("id", flat=True)
            )
    return render(
        request,
        "faculty/exam-list.html",
        {"exams": exams, "manageable_exam_ids": manageable_exam_ids},
    )


@role_required("admin", "teacher")
def exam_add(request):
    form = ExamForm(request.POST or None)
    if request.user.is_teacher and not user_is_admin(request.user):
        teacher_profile = teacher_profile_for_user(request.user)
        if teacher_profile is None:
            messages.error(request, "Your teacher profile is missing.")
            return redirect("teacher_dashboard")
        restrict_exam_form_for_teacher(form, teacher_profile)
    if request.method == "POST" and form.is_valid():
        exam = form.save(commit=False)
        if request.user.is_teacher and not user_is_admin(request.user):
            exam.teacher = teacher_profile_for_user(request.user)
        exam.save()
        messages.success(request, f"{exam.title} has been scheduled.")
        return redirect("exam_list")
    return render(
        request,
        "faculty/exam-form.html",
        {"form": form, "page_heading": "Schedule Exam", "submit_label": "Save Exam"},
    )


@role_required("admin", "teacher")
def exam_edit(request, exam_id):
    exam = get_object_or_404(Exam.objects.select_related("teacher"), pk=exam_id)
    if not can_manage_exam(request.user, exam):
        messages.error(request, "You do not have permission to update this exam.")
        return redirect("exam_list")

    form = ExamForm(request.POST or None, instance=exam)
    if request.user.is_teacher and not user_is_admin(request.user):
        teacher_profile = teacher_profile_for_user(request.user)
        restrict_exam_form_for_teacher(form, teacher_profile)
    if request.method == "POST" and form.is_valid():
        updated_exam = form.save(commit=False)
        if request.user.is_teacher and not user_is_admin(request.user):
            updated_exam.teacher = teacher_profile_for_user(request.user)
        updated_exam.save()
        messages.success(request, f"{updated_exam.title} has been updated.")
        return redirect("exam_list")
    return render(
        request,
        "faculty/exam-form.html",
        {"form": form, "page_heading": "Edit Exam", "submit_label": "Update Exam"},
    )


@role_required("admin", "teacher")
def exam_delete(request, exam_id):
    exam = get_object_or_404(Exam.objects.select_related("teacher"), pk=exam_id)
    if not can_manage_exam(request.user, exam):
        messages.error(request, "You do not have permission to delete this exam.")
        return redirect("exam_list")
    if request.method == "POST":
        exam_title = exam.title
        exam.delete()
        messages.success(request, f"{exam_title} has been deleted.")
    return redirect("exam_list")


@login_required
def result_list(request):
    results = ExamResult.objects.select_related("exam", "student", "graded_by").all()
    manageable_result_ids = []
    if request.user.is_teacher and not user_is_admin(request.user):
        teacher_profile = teacher_profile_for_user(request.user)
        if teacher_profile is not None:
            manageable_result_ids = list(
                ExamResult.objects.filter(
                    Q(exam__teacher=teacher_profile) | Q(graded_by=teacher_profile)
                ).values_list("id", flat=True)
            )
    return render(
        request,
        "faculty/result-list.html",
        {"results": results, "manageable_result_ids": manageable_result_ids},
    )


@role_required("admin", "teacher")
def result_add(request):
    form = ExamResultForm(request.POST or None)
    if request.user.is_teacher and not user_is_admin(request.user):
        teacher_profile = teacher_profile_for_user(request.user)
        if teacher_profile is None:
            messages.error(request, "Your teacher profile is missing.")
            return redirect("teacher_dashboard")
        restrict_result_form_for_teacher(form, teacher_profile)
    if request.method == "POST" and form.is_valid():
        result = form.save(commit=False)
        if request.user.is_teacher and not user_is_admin(request.user):
            result.graded_by = teacher_profile_for_user(request.user)
        result.save()
        messages.success(
            request,
            f"Grade saved for {result.student.full_name} in {result.exam.title}.",
        )
        return redirect("result_list")
    return render(
        request,
        "faculty/result-form.html",
        {"form": form, "page_heading": "Add Grade", "submit_label": "Save Grade"},
    )


@role_required("admin", "teacher")
def result_edit(request, result_id):
    result = get_object_or_404(
        ExamResult.objects.select_related("exam", "graded_by", "student"),
        pk=result_id,
    )
    if not can_manage_result(request.user, result):
        messages.error(request, "You do not have permission to update this result.")
        return redirect("result_list")

    form = ExamResultForm(request.POST or None, instance=result)
    if request.user.is_teacher and not user_is_admin(request.user):
        restrict_result_form_for_teacher(form, teacher_profile_for_user(request.user))
    if request.method == "POST" and form.is_valid():
        updated_result = form.save(commit=False)
        if request.user.is_teacher and not user_is_admin(request.user):
            updated_result.graded_by = teacher_profile_for_user(request.user)
        updated_result.save()
        messages.success(
            request,
            f"Grade updated for {updated_result.student.full_name} in {updated_result.exam.title}.",
        )
        return redirect("result_list")
    return render(
        request,
        "faculty/result-form.html",
        {"form": form, "page_heading": "Edit Grade", "submit_label": "Update Grade"},
    )


@role_required("admin", "teacher")
def result_delete(request, result_id):
    result = get_object_or_404(
        ExamResult.objects.select_related("exam", "graded_by", "student"),
        pk=result_id,
    )
    if not can_manage_result(request.user, result):
        messages.error(request, "You do not have permission to delete this result.")
        return redirect("result_list")
    if request.method == "POST":
        student_name = result.student.full_name
        exam_title = result.exam.title
        result.delete()
        messages.success(request, f"Grade for {student_name} in {exam_title} was deleted.")
    return redirect("result_list")


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
    return render(
        request,
        "faculty/holiday-form.html",
        {"form": form, "page_heading": "Add Holiday", "submit_label": "Save Holiday"},
    )


@role_required("admin")
def holiday_edit(request, holiday_id):
    holiday = get_object_or_404(Holiday, pk=holiday_id)
    form = HolidayForm(request.POST or None, instance=holiday)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{holiday.title} holiday was updated.")
        return redirect("holiday_calendar")
    return render(
        request,
        "faculty/holiday-form.html",
        {"form": form, "page_heading": "Edit Holiday", "submit_label": "Update Holiday"},
    )


@role_required("admin")
def holiday_delete(request, holiday_id):
    holiday = get_object_or_404(Holiday, pk=holiday_id)
    if request.method == "POST":
        holiday_title = holiday.title
        holiday.delete()
        messages.success(request, f"{holiday_title} holiday was deleted.")
    return redirect("holiday_calendar")
