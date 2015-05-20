# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('smart_heating', '0005_raspberrydevice_thermostatdevice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raspberrydevice',
            name='rfid',
            field=models.CharField(primary_key=True, max_length=100, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]+$', 'Only alphanumeric characters are allowed.')], serialize=False),
        ),
        migrations.AlterField(
            model_name='residence',
            name='rfid',
            field=models.CharField(primary_key=True, max_length=100, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]+$', 'Only alphanumeric characters are allowed.')], serialize=False),
        ),
        migrations.AlterField(
            model_name='thermostat',
            name='rfid',
            field=models.CharField(primary_key=True, max_length=100, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]+$', 'Only alphanumeric characters are allowed.')], serialize=False),
        ),
        migrations.AlterField(
            model_name='thermostatdevice',
            name='rfid',
            field=models.CharField(primary_key=True, max_length=100, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]+$', 'Only alphanumeric characters are allowed.')], serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='imei',
            field=models.CharField(primary_key=True, max_length=100, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]+$', 'Only alphanumeric characters are allowed.')], serialize=False),
        ),
    ]
