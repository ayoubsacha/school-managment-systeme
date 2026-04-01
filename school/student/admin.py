from django.contrib import admin

from .models import Parent, Student


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("father_name", "mother_name", "father_mobile", "mother_mobile")
    search_fields = ("father_name", "mother_name", "father_email", "mother_email")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "full_name", "student_class", "section", "admission_number")
    search_fields = ("student_id", "first_name", "last_name", "admission_number")
    list_filter = ("student_class", "section", "gender")
