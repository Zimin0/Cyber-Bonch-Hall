# Generated by Django 4.2.1 on 2023-06-15 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_notification_session_alter_notification_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='time',
            field=models.CharField(max_length=5, verbose_name='Время'),
        ),
    ]
