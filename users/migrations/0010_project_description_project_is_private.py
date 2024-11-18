# Generated by Django 4.2.4 on 2024-11-18 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_comment_project_comment_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]
