from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from home_auth.decorators import role_required

from .forms import ParentForm, StudentForm
from .models import Student


@login_required
def student_list(request):
    students = Student.objects.select_related("parent").all()
    return render(request, "students/students.html", {"student_list": students})


@role_required("admin")
def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    parent_form = ParentForm(request.POST or None)

    if request.method == "POST" and student_form.is_valid() and parent_form.is_valid():
        with transaction.atomic():
            parent = parent_form.save()
            student = student_form.save(commit=False)
            student.parent = parent
            student.save()

        messages.success(request, f"{student.full_name} was added successfully.")
        return redirect("student_list")

    return render(
        request,
        "students/add-student.html",
        {"student_form": student_form, "parent_form": parent_form},
    )


@login_required
def view_student(request, student_id):
    student = get_object_or_404(Student.objects.select_related("parent", "user"), student_id=student_id)
    return render(request, "students/student-details.html", {"student": student})


@role_required("admin")
def edit_student(request, student_id):
    student = get_object_or_404(Student.objects.select_related("parent", "user"), student_id=student_id)
    student_form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    parent_form = ParentForm(request.POST or None, instance=student.parent)

    if request.method == "POST" and student_form.is_valid() and parent_form.is_valid():
        with transaction.atomic():
            parent_form.save()
            student_form.save()
        messages.success(request, f"{student.full_name} was updated successfully.")
        return redirect("view_student", student_id=student.student_id)

    return render(
        request,
        "students/edit-student.html",
        {"student": student, "student_form": student_form, "parent_form": parent_form},
    )


@role_required("admin")
def delete_student(request, student_id):
    student = get_object_or_404(Student.objects.select_related("parent", "user"), student_id=student_id)
    if request.method == "POST":
        student_name = student.full_name
        user = student.user
        with transaction.atomic():
            student.parent.delete()
            if user is not None:
                user.delete()
        messages.success(request, f"{student_name} was deleted successfully.")
    return redirect("student_list")
