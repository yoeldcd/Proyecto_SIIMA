# Generated by Django 4.1.2 on 2022-12-06 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_systemuser_system_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='actions',
            field=models.CharField(default='None', max_length=10),
        ),
    ]
