from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import sitemaps
from config.seo_views import robots_txt


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "accounts/",
        include("accounts.urls"),
    ),
    path(
        "",
        include("blog.urls"),
    ),
    path(
    "ckeditor5/",
    include("django_ckeditor_5.urls"),
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),
    path("robots.txt", robots_txt, name="robots_txt"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
