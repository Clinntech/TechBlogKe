from django.contrib import admin
from django.utils import timezone

from .models import Category, Comment, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for blog categories."""

    list_display = (
        "name",
        "slug",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for blog tags."""

    list_display = (
        "name",
        "slug",
        "created_at",
    )

    search_fields = (
        "name",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for TechBlogKe posts."""

    list_display = (
        "title",
        "author",
        "category",
        "status",
        "is_featured",
        "view_count",
        "published_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "is_featured",
        "allow_comments",
        "category",
        "created_at",
        "published_at",
    )

    search_fields = (
        "title",
        "excerpt",
        "content",
        "author__username",
        "author__email",
        "category__name",
        "tags__name",
    )

    readonly_fields = (
        "view_count",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "author",
        "category",
        "tags",
    )

    filter_horizontal = (
        "tags",
    )

    date_hierarchy = "published_at"

    ordering = (
        "-created_at",
    )

    actions = (
        "publish_selected_posts",
        "move_selected_posts_to_draft",
        "feature_selected_posts",
        "remove_selected_posts_from_featured",
    )

    fieldsets = (
        (
            "Article information",
            {
                "fields": (
                    "title",
                    "slug",
                    "author",
                    "category",
                    "tags",
                ),
            },
        ),
        (
            "Article content",
            {
                "fields": (
                    "excerpt",
                    "content",
                    "featured_image",
                ),
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "published_at",
                    "is_featured",
                    "allow_comments",
                ),
            },
        ),
        (
            "Search engine optimization",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
        (
            "Statistics and dates",
            {
                "fields": (
                    "view_count",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.action(description="Publish selected posts")
    def publish_selected_posts(self, request, queryset):
        queryset.update(
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    @admin.action(description="Move selected posts to draft")
    def move_selected_posts_to_draft(self, request, queryset):
        queryset.update(
            status=Post.Status.DRAFT,
            published_at=None,
        )

    @admin.action(description="Feature selected posts")
    def feature_selected_posts(self, request, queryset):
        queryset.update(
            is_featured=True,
        )

    @admin.action(description="Remove selected posts from featured")
    def remove_selected_posts_from_featured(
        self,
        request,
        queryset,
    ):
        queryset.update(
            is_featured=False,
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for blog comments."""

    list_display = (
        "user",
        "post",
        "short_content",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "content",
        "user__username",
        "user__email",
        "post__title",
    )

    autocomplete_fields = (
        "user",
        "post",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    actions = (
        "approve_selected_comments",
        "hide_selected_comments",
    )

    @admin.display(description="Comment")
    def short_content(self, obj):
        if len(obj.content) <= 70:
            return obj.content

        return f"{obj.content[:67]}..."

    @admin.action(description="Approve selected comments")
    def approve_selected_comments(self, request, queryset):
        queryset.update(
            is_approved=True,
        )

    @admin.action(description="Hide selected comments")
    def hide_selected_comments(self, request, queryset):
        queryset.update(
            is_approved=False,
        )
        