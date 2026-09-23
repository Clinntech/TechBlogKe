"""
WSGI configuration for the TechBlogKe project.

This module exposes the WSGI application used by Django's
development server and production hosting platforms.
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
