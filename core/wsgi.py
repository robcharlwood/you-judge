"""
WSGI config for you judge project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

from core.boot import fix_path  # isort:skip
fix_path()

import os  # noqa

from djangae.wsgi import DjangaeApplication  # noqa
from django.core.wsgi import get_wsgi_application  # noqa

from core.utils import get_settings_name  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_settings_name())
application = DjangaeApplication(get_wsgi_application())
