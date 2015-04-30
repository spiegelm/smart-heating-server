# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0002_auto_20150424_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='temperature',
            name='thermostat',
            field=models.ForeignKey(to='smart_heating.Thermostat', default=0, related_name='temperatures'),
            preserve_default=False,
        ),
    ]
