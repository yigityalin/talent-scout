# Generated by Django 3.2.12 on 2022-03-21 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='githubuser',
            name='profession',
        ),
        migrations.AddField(
            model_name='githubuser',
            name='languages',
            field=models.TextField(blank=True, null=True),
        ),
    ]