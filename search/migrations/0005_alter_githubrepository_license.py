# Generated by Django 3.2.12 on 2022-03-20 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_alter_githubrepository_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='githubrepository',
            name='license',
            field=models.CharField(blank=True, max_length=48, null=True),
        ),
    ]
