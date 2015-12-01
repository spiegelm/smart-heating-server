# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0011_auto_20151128_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='thermostat',
            name='name',
            field=models.CharField(max_length=100, default='Thermostat'),
            preserve_default=False,
        ),
    ]
