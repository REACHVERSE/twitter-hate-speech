"""
WSGI config for hatespeech project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import hatespeech.hatespeech.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hatespeech.settings")

application = get_wsgi_application(hatespeech.hatespeech.asgi)

app = application