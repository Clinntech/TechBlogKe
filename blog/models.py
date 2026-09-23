import math

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def create_unique_slug(instance, value, max_length):
    """
    Generate a unique slug for a model instance.
    """

    base_slug = slugify(value)[:max_length] or "item"

    slug = base_slug

    counter = 2

    queryset = instance.__class__.objects.all()

    if instance.pk:

        queryset = queryset.exclude(
            pk=instance.pk,
        )


    while queryset.filter(slug=slug).exists():

        suffix = f"-{counter}"

        available_length = max_length - len(suffix)

        slug = (
            f"{base_slug[:available_length]}"
            f"{suffix}"
        )

        counter += 1


    return slug



class Category(models.Model):
    """
    A category used to organize blog posts.
    """

    name = models.CharField(
        max_length=120,
        unique=True,
    )


    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True,
    )


    description = models.TextField(
        max_length=500,
        blank=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    updated_at = models.DateTimeField(
        auto_now=True,
    )


    class Meta:

        verbose_name_plural = "Categories"

        ordering = (
            "name",
        )



    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = create_unique_slug(
                self,
                self.name,
                140,
            )


        super().save(
            *args,
            **kwargs,
        )



    def get_absolute_url(self):

        return reverse(
            "blog:category_posts",
            kwargs={
                "slug": self.slug,
            },
        )



    def __str__(self):

        return self.name





class Tag(models.Model):
    """
    A tag attached to one or more blog posts.
    """

    name = models.CharField(
        max_length=80,
        unique=True,
    )


    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    class Meta:

        ordering = (
            "name",
        )



    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = create_unique_slug(
                self,
                self.name,
                100,
            )


        super().save(
            *args,
            **kwargs,
        )



    def get_absolute_url(self):

        return reverse(
            "blog:tag_posts",
            kwargs={
                "slug": self.slug,
            },
        )



    def __str__(self):

        return self.name





class Post(models.Model):
    """
    A technology article published on TechBlogKe.
    """


    class Status(models.TextChoices):

        DRAFT = (
            "DRAFT",
            "Draft",
        )

        SCHEDULED = (
            "SCHEDULED",
            "Scheduled",
        )

        PUBLISHED = (
            "PUBLISHED",
            "Published",
        )



    title = models.CharField(
        max_length=220,
    )


    slug = models.SlugField(
        max_length=240,
        unique=True,
        blank=True,
    )


    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )


    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="posts",
        null=True,
        blank=True,
    )


    tags = models.ManyToManyField(
        Tag,
        related_name="posts",
        blank=True,
    )


    excerpt = models.TextField(
        max_length=350,
        help_text=(
            "Write a short summary of the article."
        ),
    )


    content = models.TextField()



    featured_image = models.ImageField(
        upload_to="posts/%Y/%m/",
        blank=True,
        null=True,
    )



    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )



    is_featured = models.BooleanField(
        default=False,
    )



    allow_comments = models.BooleanField(
        default=True,
    )



    view_count = models.PositiveIntegerField(
        default=0,
        editable=False,
    )



    meta_title = models.CharField(
        max_length=60,
        blank=True,
    )



    meta_description = models.CharField(
        max_length=160,
        blank=True,
    )



    published_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
    )



    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
    )



    created_at = models.DateTimeField(
        auto_now_add=True,
    )



    updated_at = models.DateTimeField(
        auto_now=True,
    )



    class Meta:

        ordering = (
            "-published_at",
            "-created_at",
        )


        indexes = [

            models.Index(
                fields=[
                    "status",
                    "-published_at",
                ],
            ),


            models.Index(
                fields=[
                    "author",
                    "status",
                ],
            ),

        ]



    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = create_unique_slug(
                self,
                self.title,
                240,
            )



        if not self.meta_title:

            self.meta_title = (
                f"{self.title} | TechBlogKe"
            )[:60]



        if not self.meta_description:

            self.meta_description = (
                self.excerpt[:160]
            )



        if self.status == self.Status.PUBLISHED:


            if not self.published_at:

                self.published_at = timezone.now()



            self.scheduled_at = None



        elif self.status == self.Status.SCHEDULED:


            self.published_at = None



        else:


            self.published_at = None

            self.scheduled_at = None



        super().save(
            *args,
            **kwargs,
        )



    def get_absolute_url(self):

        return reverse(
            "blog:post_detail",
            kwargs={
                "slug": self.slug,
            },
        )



    @property
    def reading_time(self):
        """
        Estimate reading time using approximately
        200 words per minute.
        """

        word_count = len(
            self.content.split()
        )


        return max(
            1,
            math.ceil(
                word_count / 200
            ),
        )



    @property
    def approved_comments(self):

        return self.comments.filter(
            is_approved=True,
        )



    def __str__(self):

        return self.title





class Comment(models.Model):
    """
    A comment submitted on a blog post.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_comments",
    )


    content = models.TextField(
        max_length=1000,
    )


    is_approved = models.BooleanField(
        default=True,
        db_index=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    updated_at = models.DateTimeField(
        auto_now=True,
    )


    class Meta:

        ordering = (
            "created_at",
        )


        indexes = [

            models.Index(
                fields=[
                    "post",
                    "is_approved",
                    "created_at",
                ],
            ),

        ]



    def __str__(self):

        return (
            f"Comment by {self.user.username} "
            f"on {self.post.title}"
        )