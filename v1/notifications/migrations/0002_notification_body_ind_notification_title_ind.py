# Generated by Django 4.0.4 on 2023-11-24 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='body_ind',
            field=models.CharField(max_length=500, null=True, verbose_name='Body'),
        ),
        migrations.AddField(
            model_name='notification',
            name='title_ind',
            field=models.CharField(max_length=300, null=True, verbose_name='Title'),
        ),
    ]
