from django.contrib import admin
from django.apps import apps

# Register all models
app = apps.get_app_config('smart_heating')

for model in app.get_models():
    admin.site.register(model)
