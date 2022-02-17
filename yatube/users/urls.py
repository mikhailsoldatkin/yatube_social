from django.contrib.auth import views as auth_view
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path(
        "password_change/",
        auth_view.PasswordChangeView.as_view(
            template_name="users/password_change_form.html"
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_view.PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        auth_view.PasswordResetView.as_view(
            template_name="users/password_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_view.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<str:uidb64>/<str:token>/",
        auth_view.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_view.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("signup/", views.SignUp.as_view(), name="signup"),
    path(
        "login/",
        auth_view.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_view.LogoutView.as_view(template_name="users/logged_out.html"),
        name="logout",
    ),
]
