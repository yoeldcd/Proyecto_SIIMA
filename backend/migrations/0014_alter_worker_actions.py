# Generated by Django 4.1.2 on 2022-12-06 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_worker_actions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='actions',
            field=models.CharField(default='None', max_length=22),
        ),
    ]