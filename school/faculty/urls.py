from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_add, name="department_add"),
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/add/", views.teacher_add, name="teacher_add"),
    path("subjects/", views.subject_list, name="subject_list"),
    path("subjects/add/", views.subject_add, name="subject_add"),
    path("timetable/", views.timetable_list, name="timetable_list"),
    path("timetable/add/", views.timetable_add, name="timetable_add"),
    path("timetable/visual/", views.visual_timetable, name="visual_timetable"),
    path("exams/", views.exam_list, name="exam_list"),
    path("exams/add/", views.exam_add, name="exam_add"),
    path("results/", views.result_list, name="result_list"),
    path("results/add/", views.result_add, name="result_add"),
    path("holidays/", views.holiday_calendar, name="holiday_calendar"),
    path("holidays/add/", views.holiday_add, name="holiday_add"),
]
