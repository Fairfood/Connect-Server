# Generated by Django 4.0.4 on 2023-11-30 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0005_alter_formfield_type'),
        ('supply_chains', '0003_alter_farmer_identification_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyproduct',
            name='form',
        ),
        migrations.AddField(
            model_name='companyproduct',
            name='forms',
            field=models.ManyToManyField(blank=True, related_name='company_products', to='forms.form', verbose_name='Forms'),
        ),
    ]
