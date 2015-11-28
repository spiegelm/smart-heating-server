# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0010_auto_20151001_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='heatingtableentry',
            name='temperature',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(30)]),
        ),
        migrations.AlterField(
            model_name='temperature',
            name='value',
            field=models.FloatField(),
        ),
    ]
