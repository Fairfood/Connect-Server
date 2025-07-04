# Generated by Django 4.0.4 on 2024-12-09 09:59

import base.db.utilities
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hashid_field.field


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supply_chains', '0013_company_theme_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalService',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='ABCDEFGHJKMNPQRSTUVWXYZ23456789', min_length=10, prefix='', primary_key=True, serialize=False)),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated On')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Updated On')),
                ('name', models.CharField(help_text='Name of the external service.', max_length=255)),
                ('description', models.TextField(help_text='Detailed description of the service.')),
                ('icon', models.ImageField(blank=True, help_text='Optional icon/image to represent the service.', null=True, upload_to=base.db.utilities.get_file_path, verbose_name='Service Icon')),
                ('service_url', models.TextField(help_text='URL of the external service. Can have variable schema types and lengths. May contain replaceable characters for dynamic URLs.')),
                ('is_available', models.BooleanField(default=True, help_text='Indicates if the service is currently available.')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FarmerService',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='ABCDEFGHJKMNPQRSTUVWXYZ23456789', min_length=10, prefix='', primary_key=True, serialize=False)),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated On')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Updated On')),
                ('refernce_id', models.CharField(help_text="A unique identifier for the farmer's association with the service.", max_length=100)),
                ('is_active', models.BooleanField(default=True, help_text='Indicates if this service is currently active for the farmer.')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('farmer', models.ForeignKey(help_text='The farmer who is associated with this service.', on_delete=django.db.models.deletion.CASCADE, related_name='services', to='supply_chains.farmer')),
                ('service', models.ForeignKey(help_text='The external service associated with the farmer.', on_delete=django.db.models.deletion.CASCADE, related_name='farmers', to='supply_chains.externalservice')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
    ]
