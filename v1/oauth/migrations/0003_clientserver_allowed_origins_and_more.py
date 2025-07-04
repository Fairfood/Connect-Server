# Generated by Django 4.0.4 on 2024-07-24 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0002_clientaccesstoken_application_clientserver_companies_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientserver',
            name='allowed_origins',
            field=models.TextField(blank=True, default='', help_text='Allowed origins list to enable CORS, space separated'),
        ),
        migrations.AddField(
            model_name='clientserver',
            name='hash_client_secret',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='clientaccesstoken',
            name='token',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='clientserver',
            name='post_logout_redirect_uris',
            field=models.TextField(blank=True, default='', help_text='Allowed Post Logout URIs list, space separated'),
        ),
    ]
