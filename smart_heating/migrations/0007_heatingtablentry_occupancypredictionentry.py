# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0006_validators'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeatingTableEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.CharField(max_length=3, choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sub', 'Sunday')])),
                ('time', models.TimeField()),
                ('temperature', models.FloatField()),
                ('thermostat', models.ForeignKey(related_name='heating_table_entries', to='smart_heating.Thermostat')),
            ],
        ),
        migrations.CreateModel(
            name='OccupancyPredictionEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.CharField(max_length=3, choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sub', 'Sunday')])),
                ('time', models.TimeField()),
                ('user', models.ForeignKey(to='smart_heating.User')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='occupancypredictionentry',
            unique_together=set([('day', 'time', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='heatingtableentry',
            unique_together=set([('day', 'time', 'thermostat')]),
        ),
    ]
