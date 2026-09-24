from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    CategoryForm,
    CommentForm,
    PostForm,
    TagForm,
)

from .models import Category, Comment, Post, Tag


User = get_user_model()


def publish_due_posts():
    """Publish scheduled posts whose scheduled time has arrived."""
    now = timezone.now()

    Post.objects.filter(
        status=Post.Status.SCHEDULED,
        scheduled_at__isnull=False,
        scheduled_at__lte=now,
    ).update(
        status=Post.Status.PUBLISHED,
        published_at=F("scheduled_at"),
        scheduled_at=None,
        updated_at=now,
    )

def published_posts():
    """
    Return only publicly available published posts.
    """
    publish_due_posts()

    return (
        Post.objects.filter(
            status=Post.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )
        .select_related( "author","category",)
        .prefetch_related("tags",)
    )

def paginate_queryset(
    request,
    queryset,
    items_per_page=9,
):
    """
    Paginate queryset using page query parameter.
    """

    paginator = Paginator(
        queryset,
        items_per_page,
    )

    page_number = request.GET.get("page")

    return paginator.get_page(page_number)



def author_required(view_function):
    """
    Allow access only to authors and administrators.
    """

    @wraps(view_function)
    def wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect(
                f"/accounts/login/?next={request.path}"
            )

        if not request.user.is_author:

            messages.error(
                request,
                "Only TechBlogKe authors can access this page.",
            )

            return redirect(
                "blog:home"
            )

        return view_function(
            request,
            *args,
            **kwargs,
        )

    return wrapped_view



def administrator_required(view_function):
    """
    Allow access only to administrators.
    """

    @wraps(view_function)
    def wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:

            return redirect(
                f"/accounts/login/?next={request.path}"
            )

        if not request.user.is_admin_user:

            messages.error(
                request,
                "Administrator access is required.",
            )

            return redirect(
                "blog:home"
            )

        return view_function(
            request,
            *args,
            **kwargs,
        )

    return wrapped_view



def home_view(request):
    """
    Display featured and recent TechBlogKe articles.
    """

    posts = published_posts()

    featured_post = posts.filter(
        is_featured=True,
    ).first()

    latest_posts = posts

    if featured_post:

        latest_posts = latest_posts.exclude(
            pk=featured_post.pk,
        )


    categories = (
        Category.objects.annotate(
            published_post_count=Count(
                "posts",
                filter=Q(
                    posts__status=Post.Status.PUBLISHED,
                    posts__published_at__lte=timezone.now(),
                ),
            )
        )
        .filter(
            published_post_count__gt=0,
        )
        .order_by(
            "name",
        )[:8]
    )


    context = {

        "page_title": "TechBlogKe",

        "page_description": (
            "Technology news, tutorials, insights, "
            "and stories from Kenya and beyond."
        ),

        "featured_post": featured_post,

        "latest_posts": latest_posts[:6],

        "categories": categories,

    }


    return render(
        request,
        "blog/home.html",
        context,
    )



def post_list_view(request):
    """
    Display all published posts.
    """

    posts = published_posts()


    page = paginate_queryset(
        request,
        posts,
    )


    context = {

        "page_title": "Latest Articles",

        "page_description": (
            "Browse the latest technology articles on TechBlogKe."
        ),

        "page_obj": page,

        "posts": page.object_list,

    }


    return render(
        request,
        "blog/post_list.html",
        context,
    )



def post_detail_view(request, slug):
    """
    Display one published post or an authorized draft.
    """

    post = get_object_or_404(
        Post.objects.select_related(
            "author",
            "category",
        ).prefetch_related(
            "tags",
        ),
        slug=slug,
    )


    is_owner = (
        request.user.is_authenticated
        and post.author_id == request.user.id
    )


    is_administrator = (
        request.user.is_authenticated
        and request.user.is_admin_user
    )


    if post.status != Post.Status.PUBLISHED:

        if not is_owner and not is_administrator:

            raise Http404(
                "This article is not available."
            )


    elif post.published_at and post.published_at > timezone.now():

        if not is_owner and not is_administrator:

            raise Http404(
                "This article is not available."
            )


    if post.status == Post.Status.PUBLISHED:

        Post.objects.filter(
            pk=post.pk,
        ).update(
            view_count=F("view_count") + 1,
        )


        post.refresh_from_db(
            fields=[
                "view_count",
            ],
        )



    comments = (
        post.comments.filter(
            is_approved=True,
        )
        .select_related(
            "user",
        )
        .order_by(
            "created_at",
        )
    )


    related_posts = Post.objects.none()


    if post.category:

        related_posts = (
            published_posts()
            .filter(
                category=post.category,
            )
            .exclude(
                pk=post.pk,
            )[:3]
        )
        social_image_url = ""

    if post.featured_image:
        social_image_url = request.build_absolute_uri(
            post.featured_image.url
        )

    context = {

        "page_title": post.meta_title or post.title,

        "page_description": (
            post.meta_description
            or post.excerpt
        ),

        "post": post,
        "social_image_url": social_image_url,
        "comments": comments,
        "comment_form": CommentForm(),
        "current_time": timezone.now(),
        "related_posts": related_posts,
        "can_edit": (
            is_owner
            or is_administrator
        ),

    }


    return render(
        request,
        "blog/post_detail.html",
        context,
    )
def post_preview_view(request, slug):
    """
    Preview an article before publishing.
    """

    post = get_object_or_404(
        Post.objects.select_related(
            "author",
            "category",
        ).prefetch_related(
            "tags",
        ),
        slug=slug,
    )


    if (
        post.author_id != request.user.id
        and not request.user.is_admin_user
    ):
        raise Http404(
            "You cannot preview this article."
        )


    context = {

        "page_title": (
            f"Preview: {post.title}"
        ),

        "post": post,

        "comments": [],

        "comment_form": CommentForm(),

        "related_posts": Post.objects.none(),

        "can_edit": True,

        "is_preview": True,

    }


    return render(
        request,
        "blog/post_detail.html",
        context,
    )



def search_view(request):
    """
    Search published articles.
    """

    query = request.GET.get(
        "q",
        "",
    ).strip()


    posts = published_posts()


    if query:

        posts = posts.filter(

            Q(title__icontains=query)

            |

            Q(excerpt__icontains=query)

            |

            Q(content__icontains=query)

            |

            Q(category__name__icontains=query)

            |

            Q(tags__name__icontains=query)

        ).distinct()



    page = paginate_queryset(
        request,
        posts,
    )


    context = {

        "page_title": (
            f"Search results for {query}"
            if query
            else "Search Articles"
        ),

        "page_description": (
            "Search TechBlogKe articles."
        ),

        "query": query,

        "posts": page.object_list,

        "page_obj": page,

    }


    return render(
        request,
        "blog/search_results.html",
        context,
    )



def category_posts_view(request, slug):
    """
    Display articles in a category.
    """

    category = get_object_or_404(
        Category,
        slug=slug,
    )


    posts = published_posts().filter(
        category=category,
    )


    page = paginate_queryset(
        request,
        posts,
    )


    context = {

        "page_title": category.name,

        "page_description": category.description,

        "category": category,

        "posts": page.object_list,

        "page_obj": page,

    }


    return render(
        request,
        "blog/category_posts.html",
        context,
    )



def tag_posts_view(request, slug):
    """
    Display articles with a specific tag.
    """

    tag = get_object_or_404(
        Tag,
        slug=slug,
    )


    posts = published_posts().filter(
        tags=tag,
    )


    page = paginate_queryset(
        request,
        posts,
    )


    context = {

        "page_title": tag.name,

        "page_description": (
            f"Articles tagged with {tag.name}"
        ),

        "tag": tag,

        "posts": page.object_list,

        "page_obj": page,

    }


    return render(
        request,
        "blog/tag_posts.html",
        context,
    )



def author_posts_view(request, username):
    """
    Display articles written by an author.
    """

    author = get_object_or_404(
        User,
        username=username,
    )


    posts = published_posts().filter(
        author=author,
    )


    page = paginate_queryset(
        request,
        posts,
    )


    context = {

        "page_title": (
            f"Articles by {author.username}"
        ),

        "author": author,

        "posts": page.object_list,

        "page_obj": page,

    }


    return render(
        request,
        "blog/author_posts.html",
        context,
    )



@author_required
def my_posts_view(request):
    """
    Display the logged-in author's article dashboard.
    """
    publish_due_posts()
    
    author_posts = (
        Post.objects.filter(
            author=request.user,
        )
        .select_related(
            "category",
        )
        .prefetch_related(
            "tags",
        )
        .order_by(
            "-updated_at",
        )
    )


    status_filter = request.GET.get(
        "status",
        "",
    )


    featured_filter = request.GET.get(
        "featured",
        "",
    )


    search_query = request.GET.get(
        "q",
        "",
    ).strip()



    if status_filter:

        valid_statuses = [

            Post.Status.PUBLISHED,

            Post.Status.DRAFT,

            Post.Status.SCHEDULED,

        ]


        if status_filter in valid_statuses:

            author_posts = author_posts.filter(
                status=status_filter,
            )



    if featured_filter == "true":

        author_posts = author_posts.filter(
            is_featured=True,
        )



    if search_query:

        author_posts = author_posts.filter(

            Q(title__icontains=search_query)

            |

            Q(excerpt__icontains=search_query)

            |

            Q(content__icontains=search_query)

        )



    total_count = Post.objects.filter(
        author=request.user,
    ).count()


    published_count = Post.objects.filter(
        author=request.user,
        status=Post.Status.PUBLISHED,
    ).count()


    draft_count = Post.objects.filter(
        author=request.user,
        status=Post.Status.DRAFT,
    ).count()


    scheduled_count = Post.objects.filter(
        author=request.user,
        status=Post.Status.SCHEDULED,
    ).count()


    total_views = Post.objects.filter(
        author=request.user,
    ).aggregate(
        total=Sum("view_count"),
    )["total"] or 0



    page = paginate_queryset(
        request,
        author_posts,
        items_per_page=10,
    )



    context = {

        "page_title": "Manage Articles",

        "posts": page.object_list,

        "page_obj": page,

        "total_count": total_count,

        "published_count": published_count,

        "draft_count": draft_count,

        "scheduled_count": scheduled_count,

        "total_views": total_views,

        "status_filter": status_filter,

        "featured_filter": featured_filter,

        "search_query": search_query,

    }


    return render(
        request,
        "blog/my_posts.html",
        context,
    )

@login_required
@author_required
def post_create_view(request):
    """
    Create a new article.
    """

    if request.method == "POST":

        form = PostForm(
            request.POST,
            request.FILES,
        )


        if form.is_valid():

            post = form.save(
                commit=False
            )


            post.author = request.user



            if post.status == Post.Status.PUBLISHED:

                if not post.published_at:

                    post.published_at = timezone.now()



            elif post.status == Post.Status.SCHEDULED:

                post.published_at = None



            else:

                post.published_at = None



            post.save()


            form.save_m2m()


            messages.success(
                request,
                "Article created successfully.",
            )


            return redirect(
                "blog:my_posts"
            )


    else:

        form = PostForm()



    context = {

        "page_title": "Create Article",

        "form": form,

        "is_create": True,

    }


    return render(
        request,
        "blog/post_form.html",
        context,
    )



@login_required
@author_required
def post_update_view(request, slug):
    """
    Update an existing article.
    """

    post = get_object_or_404(
        Post,
        slug=slug,
    )


    if (
        post.author_id != request.user.id
        and not request.user.is_admin_user
    ):

        messages.error(
            request,
            "You cannot edit this article.",
        )

        return redirect(
            "blog:my_posts"
        )



    if request.method == "POST":

        form = PostForm(
            request.POST,
            request.FILES,
            instance=post,
        )


        if form.is_valid():

            updated_post = form.save(
                commit=False
            )



            if updated_post.status == Post.Status.PUBLISHED:

                if not updated_post.published_at:

                    updated_post.published_at = timezone.now()



                updated_post.scheduled_at = None



            elif updated_post.status == Post.Status.SCHEDULED:

                updated_post.published_at = None



            else:

                updated_post.published_at = None

                updated_post.scheduled_at = None



            updated_post.save()


            form.save_m2m()



            messages.success(
                request,
                "Article updated successfully.",
            )


            return redirect(
                "blog:my_posts"
            )



    else:

        form = PostForm(
            instance=post,
        )



    context = {

        "page_title": (
            f"Edit: {post.title}"
        ),

        "form": form,

        "post": post,

        "is_create": False,

    }



    return render(
        request,
        "blog/post_form.html",
        context,
    )



@login_required
@author_required
def post_delete_view(request, slug):
    """
    Delete an article.
    """

    post = get_object_or_404(
        Post,
        slug=slug,
    )


    if (
        post.author_id != request.user.id
        and not request.user.is_admin_user
    ):

        messages.error(
            request,
            "You cannot delete this article.",
        )

        return redirect(
            "blog:my_posts"
        )



    if request.method == "POST":

        title = post.title


        post.delete()



        messages.success(
            request,
            f'"{title}" was deleted successfully.',
        )


        return redirect(
            "blog:my_posts"
        )



    context = {

        "page_title": "Delete Article",

        "post": post,

    }


    return render(
        request,
        "blog/post_confirm_delete.html",
        context,
    )

@login_required
def comment_create_view(request, slug):
    """
    Add a comment to an article.
    """

    post = get_object_or_404(
        Post,
        slug=slug,
        status=Post.Status.PUBLISHED,
    )


    if request.method == "POST":

        form = CommentForm(
            request.POST,
        )


        if form.is_valid():

            comment = form.save(
                commit=False,
            )

            comment.post = post

            comment.user = request.user

            comment.save()


            messages.success(
                request,
                "Your comment has been submitted.",
            )


    return redirect(
        "blog:post_detail",
        slug=slug,
    )



@login_required
@require_POST
def comment_delete_view(request, pk):
    """
    Delete a comment.
    """

    comment = get_object_or_404(
        Comment,
        pk=pk,
    )


    if (
        comment.user_id != request.user.id
        and not request.user.is_admin_user
    ):

        messages.error(
            request,
            "You cannot delete this comment.",
        )

        return redirect(
            "blog:home"
        )


    comment.delete()


    messages.success(
        request,
        "Comment deleted successfully.",
    )


    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "blog:home",
        )
    )



@administrator_required
def category_create_view(request):
    """
    Create a category.
    """

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
        )


        if form.is_valid():

            form.save()


            messages.success(
                request,
                "Category created successfully.",
            )


            return redirect(
                "blog:home"
            )


    else:

        form = CategoryForm()



    context = {

        "page_title": "Create Category",

        "form": form,

    }


    return render(
        request,
        "blog/category_form.html",
        context,
    )



@administrator_required
def tag_create_view(request):
    """
    Create a tag.
    """

    if request.method == "POST":

        form = TagForm(
            request.POST,
        )


        if form.is_valid():

            form.save()


            messages.success(
                request,
                "Tag created successfully.",
            )


            return redirect(
                "blog:home"
            )


    else:

        form = TagForm()



    context = {

        "page_title": "Create Tag",

        "form": form,

    }


    return render(
        request,
        "blog/tag_form.html",
        context,
    )
