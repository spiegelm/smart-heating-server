# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0008_heatingtablentry_occupancypredictionentry_ordering'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThermostatMetaEntry',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('rssi', models.IntegerField(null=True)),
                ('uptime', models.IntegerField(null=True)),
                ('battery', models.IntegerField(null=True)),
                ('thermostat', models.ForeignKey(to='smart_heating.Thermostat', related_name='meta_entries')),
            ],
            options={
                'ordering': ('datetime',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='thermostatmetaentry',
            unique_together=set([('thermostat', 'datetime')]),
        ),
    ]
