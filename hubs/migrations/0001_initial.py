# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eventName_text', models.CharField(max_length=50)),
                ('eventHost_text', models.CharField(max_length=50)),
                ('date_text', models.DateField()),
                ('time_text', models.TimeField()),
                ('location_text', models.CharField(max_length=200)),
                ('latCoordinate', models.FloatField()),
                ('longCoordinate', models.FloatField()),
                ('description_text', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('memberCount', models.IntegerField()),
                ('viewsCount', models.IntegerField()),
                ('hub', models.ForeignKey(to='hubs.Hub')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstName_text', models.CharField(max_length=50)),
                ('lastName_text', models.CharField(max_length=50)),
                ('username_text', models.CharField(max_length=50)),
                ('hashedPassword_text', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ('firstName_text',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='hub',
            name='users',
            field=models.ManyToManyField(to='hubs.User'),
            preserve_default=True,
        ),
    ]
