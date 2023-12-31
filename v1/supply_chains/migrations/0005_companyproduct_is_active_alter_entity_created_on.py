# Generated by Django 4.0.4 on 2023-12-04 13:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0004_remove_companyproduct_form_companyproduct_forms'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyproduct',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is Company Product Active'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created On'),
        ),
    ]
