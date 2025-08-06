"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

if os.getenv("ENVIRONMENT") == "production":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.local")

# Django 앱을 먼저 초기화
django.setup()

# Django가 초기화된 후에 import
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat import routing

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        ),
    }
)
