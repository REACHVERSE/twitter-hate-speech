"""
ASGI config for hatespeech project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import logging
from django.core.asgi import get_asgi_application

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("👋 ASGI application is initializing...")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hatespeech.settings')

application = get_asgi_application()

logger.info("✅ ASGI application is ready!")
