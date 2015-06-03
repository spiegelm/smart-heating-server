# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0007_heatingtablentry_occupancypredictionentry'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='heatingtableentry',
            options={'ordering': ('day', 'time')},
        ),
        migrations.AlterModelOptions(
            name='occupancypredictionentry',
            options={'ordering': ('day', 'time')},
        ),
        migrations.AlterField(
            model_name='heatingtableentry',
            name='day',
            field=models.CharField(max_length=3, choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]),
        ),
        migrations.AlterField(
            model_name='occupancypredictionentry',
            name='day',
            field=models.CharField(max_length=3, choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]),
        ),
    ]
