# Generated by Django 4.0.4 on 2024-10-03 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiauth', '0002_authsession_device_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authsession',
            name='client_nonce',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
