# Generated by Django 4.0.4 on 2023-11-28 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chains', '0002_alter_companyproduct_premiums'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farmer',
            name='identification_no',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Identification'),
        ),
    ]
