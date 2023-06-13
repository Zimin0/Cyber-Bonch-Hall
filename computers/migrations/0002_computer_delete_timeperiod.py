# Generated by Django 4.2.1 on 2023-05-31 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ready_to_use', models.BooleanField(default=True, verbose_name='Можно ли использовать компьютер? Напрм: сломался, сгорел, украден.')),
                ('number', models.IntegerField(blank=True, help_text='Требуется, чтобы пользователь мог найти компьютер в холле.', verbose_name='Номер компьютера в холле')),
            ],
        ),
        migrations.DeleteModel(
            name='TimePeriod',
        ),
    ]
