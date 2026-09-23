#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    """Run Django administrative tasks."""

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings",
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as error:
        raise ImportError(
            "Django could not be imported. Confirm that Django is "
            "installed and that your virtual environment is active."
        ) from error

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
    