# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestTwo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lol', models.CharField(max_length=230)),
                ('boom', models.CharField(max_length=230)),
                ('zoom', models.CharField(max_length=230)),
                ('first', models.CharField(max_length=230)),
                ('second', models.CharField(max_length=230)),
                ('third', models.CharField(max_length=230)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
