# School Management System

A Django-based school management application with role-based authentication and core academic administration features.

## Overview

This project provides:

- Role-based login for `Admin`, `Teacher`, and `Student`
- Student management
- Teacher management
- Department management
- Subject management
- Timetable creation and display
- Visual timetable view
- Exam planning
- Grade entry and result display
- Holiday calendar

The project is structured as a multi-app Django project and is ready to be published to GitHub with basic documentation, tests, and dependency management.

## Tech Stack

- Python
- Django `5.2.12`
- SQLite
- Pillow
- Bootstrap-based frontend templates

## Project Structure

```text
school/
|-- faculty/        # Academic management: teachers, departments, subjects, timetable, exams, holidays
|-- home_auth/      # Custom authentication, roles, password reset
|-- school/         # Django project settings and root URLs
|-- student/        # Student and parent management
|-- static/         # Static assets
|-- templates/      # Shared templates
|-- manage.py
`-- requirements.txt
```

## Main Features

### Authentication

- Custom user model
- Login with email/password
- Role-aware redirect after login
- Password reset with token-based flow
- Seeded demo users available after migration

### Academic Management

- Create and view departments
- Create and view teachers
- Create and view subjects
- Create and view timetable entries
- Visual timetable board
- Plan exams
- Enter grades
- View holiday calendar

### Student Module

- Add, edit, view, and delete students
- Store parent information
- Enforce unique student identifiers

## Demo Accounts

These accounts are created by migrations for development/demo use:

- Student: `student@gmail.com` / `student`
- Admin: `admin@gmail.com` / `admin`
- Teacher: `teachers@gmail.com` / `teacher`

Important:
- Passwords are hashed in the database
- These credentials are weak and should be changed for any real deployment

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd school
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

Then open:

- App: `http://127.0.0.1:8000/`
- Django admin: `http://127.0.0.1:8000/admin/`

## Useful Commands

Run tests:

```bash
python manage.py test
```

Run Django checks:

```bash
python manage.py check
```

Create a superuser manually:

```bash
python manage.py createsuperuser
```

## Roles and Access

- Admin:
  - Full access to academic management features
  - Can create departments, teachers, subjects, holidays
  - Can access Django admin
- Teacher:
  - Can view academic data
  - Can create timetable entries, exams, and grades
- Student:
  - Can view timetable, exams, grades, departments, subjects, and holidays

## Testing Status

The project includes automated tests for:

- Authentication flows
- Seeded user accounts
- Student CRUD
- Dashboard access control
- Department, teacher, subject creation
- Timetable, exam, grade, and holiday flows

## Current Limitations

- SQLite is used for development simplicity
- Some academic modules currently support `create + list/view` but not full edit/delete workflows
- Student-grade visibility is currently global for authenticated users; per-student private portal behavior can be added later
- The visual timetable is an internal board view, not a third-party timetabling integration

## Recommended Next Improvements

- Add edit/delete support for faculty modules
- Link authenticated student users directly to student records
- Add pagination and filtering on all lists
- Add production settings and environment-based secret management
- Replace demo passwords before deployment

## Repository Readiness

This repository now includes:

- `README.md`
- `PROJECT_REPORT.md`
- `requirements.txt`
- `.gitignore`

That makes it suitable for GitHub submission or portfolio publication.
