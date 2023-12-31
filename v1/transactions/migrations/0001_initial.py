# Generated by Django 4.0.4 on 2023-11-24 07:00

import base.db.utilities
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import hashid_field.field


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('forms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supply_chains', '0001_initial'),
        ('catalogs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseTransaction',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='ABCDEFGHJKMNPQRSTUVWXYZ23456789', min_length=10, prefix='', primary_key=True, serialize=False)),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated On')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Updated On')),
                ('number', models.CharField(blank=True, max_length=10, null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('invoice', models.FileField(blank=True, null=True, upload_to=base.db.utilities.get_file_path, verbose_name='Invoice')),
                ('invoice_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Invoice Number')),
                ('verification_latitude', models.FloatField(default=0.0, verbose_name='Verification Latitude')),
                ('verification_longitude', models.FloatField(default=0.0, verbose_name='Verification Longitude')),
                ('method', models.CharField(blank=True, choices=[('CARD', 'Card'), ('INVOICE', 'Invoice'), ('NONE', 'None')], max_length=15, null=True)),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='catalogs.connectcard', verbose_name='Card')),
                ('creator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_transactions', to='supply_chains.entity', verbose_name='Destination')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_transactions', to='supply_chains.entity', verbose_name='Source')),
                ('submissions', models.ManyToManyField(blank=True, to='forms.submission', verbose_name='Submissions')),
                ('updater', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_%(class)s_objects', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductTransaction',
            fields=[
                ('basetransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='transactions.basetransaction')),
                ('quality_correction', models.FloatField(default=100.0, verbose_name='Quality Correction')),
                ('quantity', models.DecimalField(blank=True, decimal_places=3, default=0.0, max_digits=25, null=True, verbose_name='Quantity')),
                ('parents', models.ManyToManyField(blank=True, related_name='children', to='transactions.producttransaction', verbose_name='Parent Transactions')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalogs.product', verbose_name='Product')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
            bases=('transactions.basetransaction',),
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('basetransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='transactions.basetransaction')),
                ('payment_type', models.CharField(choices=[('TRANSACTION', 'Transaction'), ('PREMIUM', 'Premium'), ('TRANSACTION_PREMIUM', 'Transaction Premium')], default='TRANSACTION_PREMIUM', max_length=20, verbose_name='Payment Type')),
                ('amount', models.FloatField(default=0.0, verbose_name='Amount')),
                ('currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogs.currency', verbose_name='Currency')),
                ('premium', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='premium_payments', to='catalogs.premium', verbose_name='Premium')),
                ('selected_option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogs.premiumoption', verbose_name='Selected Option')),
                ('transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_payments', to='transactions.producttransaction')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
            bases=('transactions.basetransaction',),
        ),
    ]
