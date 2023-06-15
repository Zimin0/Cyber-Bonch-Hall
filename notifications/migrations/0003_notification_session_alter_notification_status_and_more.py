# Generated by Django 4.2.1 on 2023-06-15 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0006_session_vk_id'),
        ('notifications', '0002_alter_notification_status_alter_notification_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='session',
            field=models.ForeignKey(blank=True, help_text='Уведомления привязаны к этой сесиии.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notions', to='booking.session', verbose_name='Сессия'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.CharField(choices=[('W', 'Ожидает отправки'), ('NTS', 'Уже должно быть оптравлено, но пока еще нет.'), ('S', 'Оптравлено')], default='W', max_length=5, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('NS', 'Без типа'), ('RTC', 'Напоминание о брони.'), ('AC', 'Проверка, находится ли пользователь за компьютером.'), ('EW', 'Предупреждение о конце сесиии.')], default='NS', max_length=5, verbose_name='Тип'),
        ),
    ]