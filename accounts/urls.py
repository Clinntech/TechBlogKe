from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)

from django.urls import (
    path,
    reverse_lazy,
)

from .forms import (
    CustomPasswordResetForm,
    CustomSetPasswordForm,
)

from .views import (
    CustomLoginView,
    dashboard_view,
    logout_view,
    profile_edit_view,
    profile_view,
    public_profile,
    register_view,
)


app_name = "accounts"



urlpatterns = [

    path(
        "register/",
        register_view,
        name="register",
    ),


    path(
        "login/",
        CustomLoginView.as_view(),
        name="login",
    ),


    path(
        "logout/",
        logout_view,
        name="logout",
    ),


    path(
        "dashboard/",
        dashboard_view,
        name="dashboard",
    ),


    path(
        "profile/",
        profile_view,
        name="profile",
    ),


    path(
        "profile/edit/",
        profile_edit_view,
        name="profile_edit",
    ),


    # Public author profiles

    path(
        "authors/<str:username>/",
        public_profile,
        name="public_profile",
    ),



    # Password reset

    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name=(
                "registration/password_reset_email.html"
            ),
            subject_template_name=(
                "registration/password_reset_subject.txt"
            ),
            form_class=CustomPasswordResetForm,
            success_url=reverse_lazy(
                "accounts:password_reset_done"
            ),
        ),
        name="password_reset",
    ),



    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name=(
                "registration/password_reset_done.html"
            ),
        ),
        name="password_reset_done",
    ),



    path(
        "password-reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name=(
                "registration/password_reset_confirm.html"
            ),
            form_class=CustomSetPasswordForm,
            success_url=reverse_lazy(
                "accounts:password_reset_complete"
            ),
        ),
        name="password_reset_confirm",
    ),



    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name=(
                "registration/password_reset_complete.html"
            ),
        ),
        name="password_reset_complete",
    ),

]