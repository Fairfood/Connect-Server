# Generated by Django 4.0.4 on 2023-11-30 06:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0002_initial'),
        ('forms', '0006_remove_submission_product_submission_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='products',
        ),
        migrations.AddField(
            model_name='submission',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submissions', to='catalogs.product', verbose_name='Product'),
        ),
    ]
