# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0004_auto_20150512_2234'),
    ]

    operations = [
        migrations.CreateModel(
            name='RaspberryDevice',
            fields=[
                ('rfid', models.CharField(primary_key=True, max_length=100, serialize=False)),
                ('mac', models.CharField(unique=True, max_length=17)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ThermostatDevice',
            fields=[
                ('rfid', models.CharField(primary_key=True, max_length=100, serialize=False)),
                ('mac', models.CharField(unique=True, max_length=17)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
