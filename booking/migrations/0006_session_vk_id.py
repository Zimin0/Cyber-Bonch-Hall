# Generated by Django 4.2.1 on 2023-06-05 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_alter_session_computer_alter_timeperiod_computer'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='vk_id',
            field=models.IntegerField(blank=True, default=0, verbose_name='VK ID'),
        ),
    ]
