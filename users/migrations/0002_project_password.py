# Generated by Django 4.2.4 on 2024-11-21 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
