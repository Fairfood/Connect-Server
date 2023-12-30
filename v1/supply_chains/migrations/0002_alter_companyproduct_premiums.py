# Generated by Django 4.0.4 on 2023-11-28 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0002_initial'),
        ('supply_chains', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyproduct',
            name='premiums',
            field=models.ManyToManyField(blank=True, related_name='company_products', to='catalogs.premium', verbose_name='Premium'),
        ),
    ]