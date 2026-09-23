from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # Public pages
    path(
        "",
        views.home_view,
        name="home",
    ),
    path(
        "articles/",
        views.post_list_view,
        name="post_list",
    ),
    path(
        "search/",
        views.search_view,
        name="search",
    ),

    # Category pages
    path(
        "categories/create/",
        views.category_create_view,
        name="category_create",
    ),
    path(
        "categories/<slug:slug>/",
        views.category_posts_view,
        name="category_posts",
    ),

    # Tag pages
    path(
        "tags/create/",
        views.tag_create_view,
        name="tag_create",
    ),
    path(
        "tags/<slug:slug>/",
        views.tag_posts_view,
        name="tag_posts",
    ),

    # Author pages
    path(
        "authors/<str:username>/",
        views.author_posts_view,
        name="author_posts",
    ),

    # Article management
    path(
        "dashboard/articles/",
        views.my_posts_view,
        name="my_posts",
    ),
    path(
        "articles/create/",
        views.post_create_view,
        name="post_create",
    ),
    path(
        "articles/<slug:slug>/edit/",
        views.post_update_view,
        name="post_update",
    ),
     path(
            "articles/<slug:slug>/preview/",
            views.post_preview_view,
            name="post_preview",
        ),
    path(
        "articles/<slug:slug>/delete/",
        views.post_delete_view,
        name="post_delete",
    ),
    

    # Comments
    path(
        "articles/<slug:slug>/comments/add/",
        views.comment_create_view,
        name="comment_create",
    ),
    path(
        "comments/<int:pk>/delete/",
        views.comment_delete_view,
        name="comment_delete",
    ),

    # Article detail
    path(
        "articles/<slug:slug>/",
        views.post_detail_view,
        name="post_detail",
    ),
]