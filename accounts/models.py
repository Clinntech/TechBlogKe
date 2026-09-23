from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model for TechBlogKe."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        AUTHOR = "AUTHOR", "Author"
        READER = "READER", "Regular User"

    email = models.EmailField(
        unique=True,
        help_text="A unique email address is required.",
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.READER,
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    website = models.URLField(
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_admin_user(self):
        return (
            self.role == self.Role.ADMIN
            or self.is_staff
            or self.is_superuser
        )

    @property
    def is_author(self):
        return (
            self.role == self.Role.AUTHOR
            or self.is_admin_user
        )

    @property
    def is_regular_user(self):
        return self.role == self.Role.READER