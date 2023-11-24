import os
from celery import Celery
from django.conf import settings
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LeLuChat_ChatEngine.settings")
django.setup()

app = Celery("LeLuChat_ChatEngine")
app.config_from_object("django.conf:settings",  namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
