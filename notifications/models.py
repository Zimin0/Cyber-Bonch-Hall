from django.db import models
from booking.models import Session

class Notification(models.Model):
    """ 
    Уведомления в чате VK
        time : 
            16:00
        text : 
            'sample'
        user_vk_id :
            12144141
        type:
            NS: 
                Без типа
            RTC: 
                Напоминание о брони
            AC: 
                Проверка, находится ли пользователь за компьютером. 
            EW: 
                Предупреждение о конце сесиии.
        status:
            W:
                Ожидает отправки
            NTS:
                Уже должно быть оптравлено, но пока еще нет.
            S:
                Оптравлено
        session:
            Session object
    """
    TYPES = (
        ('NS', 'Без типа'),
        ('RTC', 'Напоминание о брони.'),
        ('AC', 'Проверка, находится ли пользователь за компьютером.'),
        ('EW', 'Предупреждение о конце сесиии.')
    )

    STATUSES = (
        ('W', 'Ожидает отправки'),
        ('NTS', 'Уже должно быть оптравлено, но пока еще нет.'),
        ('S', 'Оптравлено')
    )
    
    time = models.CharField(max_length=5, verbose_name="Время", blank=False)
    text = models.TextField(verbose_name="Текст")
    user_vk_id = models.IntegerField(verbose_name="VK ID пользователя, которому будет отправлено уведомление", blank=False)
    type = models.CharField(verbose_name="Тип", max_length=5, choices=TYPES, default='NS', )
    status = models.CharField(max_length=5, choices=STATUSES, default='W', blank=False, verbose_name="Статус")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='notions', verbose_name="Сессия", help_text="Уведомления привязаны к этой сесиии.", blank=True, null=True)
