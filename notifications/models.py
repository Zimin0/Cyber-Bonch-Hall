from django.db import models

class Notification(models.Model):
    STATUSES = (
        ('W', 'Ожидает отправки'),
        ('NTS', 'Уже должно быть оптравлено, но пока еще нет.'),
        ('S', 'Оптравлено')
    )

    TYPES = (
        ('NS', 'Без типа'),
        ('RTC', 'Напоминание о брони.'),
        ('AC', 'Проверка, находится ли пользователь за компьютером.'),
        ('EW', 'Предупреждение о конце сесиии.')

    )
    time = models.TimeField(verbose_name="Время", blank=False)
    text = models.TextField(verbose_name="Текст")
    user_vk_id = models.IntegerField(verbose_name="VK ID пользователя, которому будет отправлено уведомление", blank=False)
    type = models.CharField(verbose_name="Тип", max_length=5, choices=TYPES, default='NS', )
    status = models.CharField(max_length=5, choices=STATUSES, default='W', blank=False, verbose_name="Статус")
