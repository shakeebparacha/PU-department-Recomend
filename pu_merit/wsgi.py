"""
WSGI config for pu_merit project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pu_merit.settings')

application = get_wsgi_application()
