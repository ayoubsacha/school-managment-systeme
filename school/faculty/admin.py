from django.contrib import admin

from .models import Department, Exam, ExamResult, Holiday, Subject, TeacherProfile, TimetableEntry


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "full_name", "email", "department", "is_active")
    search_fields = ("employee_id", "first_name", "last_name", "email")
    list_filter = ("department", "is_active")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "department", "teacher", "credit_hours")
    search_fields = ("code", "name")
    list_filter = ("department",)


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ("subject", "day_of_week", "target_class", "section", "start_time", "end_time")
    list_filter = ("day_of_week", "target_class", "section")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "target_class", "section", "exam_date", "total_marks")
    list_filter = ("exam_date", "target_class", "section")
    search_fields = ("title", "subject__name")


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "marks_obtained", "graded_by", "created_at")
    search_fields = ("student__first_name", "student__last_name", "exam__title")


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date")
    list_filter = ("start_date",)
