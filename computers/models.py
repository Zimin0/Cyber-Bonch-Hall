from django.db import models
from config.config import BOOKING_TIME_START, BOOKING_TIME_END
from django.core.validators import MaxValueValidator, MinValueValidator
# from .models import TimePeriod





class Computer(models.Model):
    ready_to_use = models.BooleanField(default=True, verbose_name="Можно ли использовать компьютер? Напрм: сломался, сгорел, украден.")
    number = models.IntegerField(verbose_name="Номер компьютера в холле", help_text="Требуется, чтобы пользователь мог найти компьютер в холле.", blank=True)

    def __str__(self):
        return f'ПК № {self.number}'
    
    # def save(self, *args, **kwargs):
    #     # !!!!!!!!!!!!!! Задокументировать !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #     for i in range(7):
    #         for j in range(4):
    #             if j == 0:
    #                 TimePeriod.objects.create(time=f'{16+i}:00', computer=self)
    #                 continue
    #             TimePeriod.objects.create(time=f'{16+i}:{15*j}', computer=self)
    #     super(Computer, self).save(*args, **kwargs)
    


    




