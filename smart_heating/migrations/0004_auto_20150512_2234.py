# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0003_temperature_thermostat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='residence',
            field=models.ForeignKey(to='smart_heating.Residence', related_name='users'),
            preserve_default=True,
        ),
    ]
