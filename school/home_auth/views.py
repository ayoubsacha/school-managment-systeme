from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ForgotPasswordForm, LoginForm, ResetPasswordForm, SignUpForm
from .models import CustomUser, PasswordResetRequest


def redirect_for_user(user):
    return redirect(user.dashboard_name())


def signup_view(request):
    if request.user.is_authenticated:
        return redirect_for_user(request.user)

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="home_auth.backends.EmailBackend")
        messages.success(request, "Your student account has been created.")
        return redirect_for_user(user)

    return render(request, "authentication/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect_for_user(request.user)

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )

        if user is None:
            messages.error(request, "Invalid email or password.")
        else:
            login(request, user, backend="home_auth.backends.EmailBackend")
            messages.success(request, f"Welcome back, {user.first_name or user.email}.")
            return redirect_for_user(user)

    return render(request, "authentication/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    reset_link = None

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        user = CustomUser.objects.filter(email__iexact=email).first()

        if user is None:
            messages.error(request, "No account is registered with that email.")
        else:
            PasswordResetRequest.objects.filter(
                user=user,
                created_at__lt=timezone.now() - PasswordResetRequest.TOKEN_VALIDITY_PERIOD,
            ).delete()
            reset_request = PasswordResetRequest.objects.create(user=user, email=user.email)
            reset_link = request.build_absolute_uri(reset_request.get_reset_link())
            reset_request.send_reset_email()
            messages.success(request, "A reset link has been generated for this account.")

    return render(
        request,
        "authentication/forgot-password.html",
        {"form": form, "reset_link": reset_link},
    )


def reset_password_view(request, token):
    reset_request = get_object_or_404(PasswordResetRequest, token=token)
    if not reset_request.is_valid():
        messages.error(request, "This password reset link has expired.")
        reset_request.delete()
        return redirect("forgot_password")

    form = ResetPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = reset_request.user
        user.set_password(form.cleaned_data["new_password1"])
        user.save(update_fields=["password"])
        reset_request.delete()
        messages.success(request, "Your password has been updated. You can log in now.")
        return redirect("login")

    return render(
        request,
        "authentication/reset_password.html",
        {"form": form, "reset_request": reset_request},
    )
