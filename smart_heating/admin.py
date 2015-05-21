from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from django.db import models

# Register your models here.
app = apps.get_app_config('smart_heating')

for model in app.get_models():
    admin.site.register(model)
