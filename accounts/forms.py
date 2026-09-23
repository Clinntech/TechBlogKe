from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Form used to register a new TechBlogKe user."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
                "autocomplete": "email",
            }
        ),
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
                "autocomplete": "given-name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
                "autocomplete": "family-name",
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Choose a username",
                    "autocomplete": "username",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Confirm your password",
                "autocomplete": "new-password",
            }
        )

        self.fields["username"].help_text = (
            "Use letters, numbers, and the characters @, ., +, -, or _."
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if CustomUser.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data["email"]
        user.role = CustomUser.Role.READER

        if commit:
            user.save()

        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Styled login form."""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your username",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )


class UserProfileForm(forms.ModelForm):
    """Form used by users to update their profiles."""

    class Meta:
        model = CustomUser

        fields = (
            "first_name",
            "last_name",
            "email",
            "bio",
            "profile_image",
            "website",
        )

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First name",
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last name",
                    "autocomplete": "family-name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "name@example.com",
                    "autocomplete": "email",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Tell TechBlogKe readers a little about yourself."
                    ),
                    "rows": 5,
                }
            ),
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "website": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        email_exists = CustomUser.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.pk
        ).exists()

        if email_exists:
            raise forms.ValidationError(
                "Another account is already using this email address."
            )

        return email


class CustomPasswordResetForm(PasswordResetForm):
    """Styled password-reset request form."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your registered email",
                "autocomplete": "email",
            }
        ),
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Styled form for selecting a new password."""

    new_password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter a new password",
                "autocomplete": "new-password",
            }
        ),
    )

    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm your new password",
                "autocomplete": "new-password",
            }
        ),
    )
    