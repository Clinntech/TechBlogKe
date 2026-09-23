from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Post


class StaticPageSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return ("blog:home", "blog:post_list")

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Post.objects.filter(
            status=Post.Status.PUBLISHED,
            published_at__isnull=False,
        ).order_by("-published_at")

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


sitemaps = {
    "pages": StaticPageSitemap,
    "articles": PostSitemap,
}
