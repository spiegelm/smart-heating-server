# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0009_auto_20150608_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temperature',
            name='value',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(30)]),
        ),
    ]
