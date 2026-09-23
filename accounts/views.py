from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from blog.models import Post

from .forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
    UserProfileForm,
)


class CustomLoginView(LoginView):
    """Handle user login."""

    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Welcome back, {form.get_user().username}.",
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Login failed. Check your username and password.",
        )

        return super().form_invalid(form)



def register_view(request):
    """Register a new regular TechBlogKe user."""

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")


    if request.method == "POST":

        form = CustomUserCreationForm(
            request.POST
        )


        if form.is_valid():

            user = form.save()


            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )


            messages.success(
                request,
                "Your TechBlogKe account has been created successfully.",
            )


            return redirect(
                "accounts:dashboard"
            )


        messages.error(
            request,
            "Please correct the errors shown below.",
        )


    else:

        form = CustomUserCreationForm()



    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )



@login_required
def dashboard_view(request):
    """
    Display the user dashboard with content statistics.
    """

    user_posts = Post.objects.filter(
        author=request.user,
    )

    published_posts = user_posts.filter(
        status=Post.Status.PUBLISHED,
    )

    draft_posts = user_posts.filter(
        status=Post.Status.DRAFT,
    )

    total_views = user_posts.aggregate(
        total=Sum("view_count")
    )["total"] or 0

    recent_posts = user_posts.order_by(
        "-created_at"
    )[:5]

    context = {

        "profile_user": request.user,

        "is_admin_user": request.user.is_admin_user,

        "is_author": request.user.is_author,

        "is_regular_user": request.user.is_regular_user,


        "article_count": user_posts.count(),

        "published_count": published_posts.count(),

        "draft_count": draft_posts.count(),

        "total_views": total_views,

        "recent_posts": recent_posts,

    }

    return render(
        request,
        "accounts/dashboard.html",
        context,
    )

@login_required
def profile_view(request):
    """Display the signed-in user's profile."""

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": request.user,
        },
    )



@login_required
def profile_edit_view(request):
    """Allow the signed-in user to edit their profile."""

    if request.method == "POST":

        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )


        if form.is_valid():

            form.save()


            messages.success(
                request,
                "Your profile has been updated successfully.",
            )


            return redirect(
                "accounts:profile"
            )


        messages.error(
            request,
            "Please correct the errors shown below.",
        )


    else:

        form = UserProfileForm(
            instance=request.user,
        )



    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form,
        },
    )



def public_profile(request, username):
    """
    Display a public author profile.
    """

    User = get_user_model()


    profile_user = get_object_or_404(
        User,
        username=username,
    )


    posts = Post.objects.filter(
        author=profile_user,
        status=Post.Status.PUBLISHED,
    ).order_by(
        "-published_at",
    )


    total_views = posts.aggregate(
        total=Sum("view_count")
    )["total"] or 0



    category_count = (
        posts
        .filter(
            category__isnull=False
        )
        .values(
            "category"
        )
        .distinct()
        .count()
    )



    context = {
        "profile_user": profile_user,
        "posts": posts,
        "article_count": posts.count(),
        "total_views": total_views,
        "category_count": category_count,
    }



    return render(
        request,
        "accounts/public_profile.html",
        context,
    )



@login_required
@require_POST
def logout_view(request):
    """Log the current user out using a POST request."""

    logout(request)


    messages.success(
        request,
        "You have been signed out successfully.",
    )


    return redirect(
        "blog:home"
    )