# faculty/views.py
from django.shortcuts import render, redirect

def index(request):
    return render(request, 'authentication/login.html')

def dashboard(request):
    return render(request, 'students/student-dashboard.html')