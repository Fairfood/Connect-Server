# Generated by Django 4.0.4 on 2023-11-29 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0004_formfield_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfield',
            name='type',
            field=models.CharField(choices=[('TEXT', 'Text'), ('INTEGER', 'Integer'), ('FLOAT', 'Float'), ('RADIO', 'Radio'), ('MULTI_SELECT', 'Multi Select'), ('EMAIL', 'Email'), ('PHONE', 'Phone'), ('DATE', 'Date'), ('BOOLEAN', 'Boolean'), ('DROPDOWN', 'Dropdown')], max_length=20, verbose_name='Field Type'),
        ),
    ]