"""
ASGI config for eave_django_playground project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from eave.collectors.django_orm import DjangoOrmCollectorManager

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eave_django_playground.settings')

DjangoOrmCollectorManager.start()

application = get_asgi_application()
