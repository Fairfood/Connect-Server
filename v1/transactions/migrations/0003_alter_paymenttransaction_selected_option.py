# Generated by Django 4.0.4 on 2023-12-05 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_alter_basetransaction_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenttransaction',
            name='selected_option',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Selected Option'),
        ),
    ]