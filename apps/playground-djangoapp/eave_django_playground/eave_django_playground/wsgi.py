"""
WSGI config for eave_django_playground project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from eave.collectors.django_orm import DjangoOrmCollectorManager

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eave_django_playground.settings')

DjangoOrmCollectorManager.start()

application = get_wsgi_application()
