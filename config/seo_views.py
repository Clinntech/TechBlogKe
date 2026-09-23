from django.http import HttpResponse
from django.urls import reverse


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))

    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/dashboard/",
        "Disallow: /accounts/profile/",
        "Disallow: /accounts/login/",
        "Disallow: /accounts/logout/",
        "Disallow: /accounts/register/",
        "Disallow: /accounts/password-reset/",
        "",
        f"Sitemap: {sitemap_url}",
        "",
    ]

    return HttpResponse(
        "\n".join(lines),
        content_type="text/plain; charset=utf-8",
    )
