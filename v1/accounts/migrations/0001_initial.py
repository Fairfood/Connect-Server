# Generated by Django 4.0.4 on 2023-11-24 07:00

import base.db.utilities
import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import hashid_field.field


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', hashid_field.field.HashidAutoField(alphabet='ABCDEFGHJKMNPQRSTUVWXYZ23456789', min_length=10, prefix='', primary_key=True, serialize=False)),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated On')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Updated On')),
                ('dob', models.DateField(blank=True, null=True, verbose_name='Date Of Birth')),
                ('phone', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='Phone Number')),
                ('address', models.CharField(blank=True, default='', max_length=2000, null=True, verbose_name='Address')),
                ('language', models.CharField(choices=[('en', 'English'), ('nl', 'Dutch'), ('de', 'German'), ('fr', 'French')], default='en', max_length=10, verbose_name='Selected Language')),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to=base.db.utilities.get_file_path, verbose_name='Photo')),
                ('type', models.IntegerField(choices=[(101, 'Super Admin'), (111, 'Admin'), (121, 'Entity User')], default=121, verbose_name='User Type')),
                ('status', models.IntegerField(choices=[(101, 'User Created'), (111, 'User Active')], default=101, verbose_name='User Status')),
                ('is_blocked', models.BooleanField(default=False, verbose_name='Block User')),
                ('updated_email', models.EmailField(blank=True, default='', max_length=254, null=True, verbose_name='Last Updated Email')),
                ('force_logout', models.BooleanField(default=False, verbose_name='Force Logout User')),
            ],
            options={
                'verbose_name': 'Base User',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ValidationToken',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='ABCDEFGHJKMNPQRSTUVWXYZ23456789', min_length=10, prefix='', primary_key=True, serialize=False)),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated On')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Updated On')),
                ('ip', models.CharField(blank=True, default='', max_length=500)),
                ('location', models.CharField(blank=True, default='', max_length=500)),
                ('device', models.CharField(blank=True, default='', max_length=500)),
                ('key', models.CharField(max_length=200, verbose_name='Token')),
                ('status', models.IntegerField(choices=[(101, 'Used'), (111, 'Unused')], default=111, verbose_name='Token Status')),
                ('expiry', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Token Expiry Date')),
                ('type', models.IntegerField(choices=[(101, 'Verify Email'), (102, 'Change Email'), (103, 'Reset Password'), (104, 'OTP'), (105, 'Magic Login'), (106, 'Invite'), (107, 'Notification')], default=101, verbose_name='Token Type')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='validation_tokens', to=settings.AUTH_USER_MODEL, verbose_name='Token User')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserDevice',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='ABCDEFGHJKMNPQRSTUVWXYZ23456789', min_length=10, prefix='', primary_key=True, serialize=False)),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated On')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Updated On')),
                ('type', models.IntegerField(choices=[(101, 'Android'), (102, 'Ios'), (103, 'Web')], default=101, verbose_name='Device Type')),
                ('registration_id', models.TextField(blank=True, default='', verbose_name='Registration token')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='devices', to=settings.AUTH_USER_MODEL, verbose_name='Device User')),
            ],
            options={
                'verbose_name': 'User device',
                'verbose_name_plural': 'User devices',
            },
        ),
        migrations.CreateModel(
            name='PrivacyPolicy',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='ABCDEFGHJKMNPQRSTUVWXYZ23456789', min_length=10, prefix='', primary_key=True, serialize=False)),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated On')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Updated On')),
                ('content', models.TextField(blank=True, default='', null=True, verbose_name='Policy Content')),
                ('content_en_us', models.TextField(blank=True, default='', null=True, verbose_name='Policy Content')),
                ('content_en_uk', models.TextField(blank=True, default='', null=True, verbose_name='Policy Content')),
                ('content_fr', models.TextField(blank=True, default='', null=True, verbose_name='Policy Content')),
                ('content_nl', models.TextField(blank=True, default='', null=True, verbose_name='Policy Content')),
                ('version', models.PositiveIntegerField(default=0, unique=True, verbose_name='Version')),
                ('date', models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Privacy Policy Date')),
                ('since', models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Start Date')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
            ],
            options={
                'verbose_name_plural': 'Privacy Policies',
            },
        ),
        migrations.AddField(
            model_name='customuser',
            name='accepted_policy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accepted_users', to='accounts.privacypolicy', verbose_name='Latest Accepted Privacy Policy'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='creator',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
    ]
