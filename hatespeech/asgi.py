import os
import logging
from django.core.asgi import get_asgi_application
from hatemodel.services.prediction import initialize_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hatespeech.settings')

logger.info("👋 ASGI application is initializing...")
django_app = get_asgi_application()
logger.info("✅ Django ASGI application instance created.")

async def application(scope, receive, send):
    """
    The main ASGI application that wraps Django and adds lifespan support.
    """
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                logger.info("🚀 Lifespan startup: Loading ML model and assets...")
                initialize_model()
                logger.info("✅ Lifespan startup: Model loaded successfully!")
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                logger.info("🧹 Lifespan shutdown: Cleaning up resources...")
                await send({'type': 'lifespan.shutdown.complete'})
                return
    else:
        await django_app(scope, receive, send)