# Generated by Django 4.0.4 on 2023-11-24 07:01

from django.db import migrations, models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='formfield',
            name='default_value',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Default Value'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_en_uk',
            field=models.CharField(max_length=100, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_en_us',
            field=models.CharField(max_length=100, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_fr',
            field=models.CharField(max_length=100, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_ind',
            field=models.CharField(max_length=100, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='label_nl',
            field=models.CharField(max_length=100, null=True, verbose_name='Label'),
        ),
        migrations.AddField(
            model_name='formfield',
            name='options',
            field=django_extensions.db.fields.json.JSONField(blank=True, default=dict, null=True, verbose_name='Options'),
        ),
    ]
