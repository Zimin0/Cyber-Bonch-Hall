from django.db import models
from config.config import BOOKING_TIME_START, BOOKING_TIME_END
from django.core.validators import MaxValueValidator, MinValueValidator
from computers.models import Computer
import time
from config.settings import DEBUG
from django.core.cache import cache


class Session(models.Model):
    """Сессия от X до Y"""
    time_start = models.CharField(verbose_name="Время начала сеанса", blank=False, help_text="Формат: XX:XX", max_length=5)
    time_end = models.CharField(verbose_name="Время окончания сеанса", blank=False, help_text="Формат: XX:XX", max_length=5)
    computer = models.ForeignKey(Computer, verbose_name="Компьютер", on_delete=models.CASCADE, related_name="sessions")
    vk_id = models.IntegerField(verbose_name='VK ID', blank=True, default=0)

    def __str__(self) -> str:
        return f"{self.time_start} --> {self.time_end}"
    
    def delete(self, bot):
        start_index = bot.get_ready_to_book_list().index(self.time_start)
        for i in range(6):
            time_period = TimePeriod.objects.filter(time=bot.get_ready_to_book_list()[start_index + i], computer=self.computer).first()
            if time_period is not None:
                time_period.status = "F"
                time_period.save()
        super(Session, self).delete()

    def save(self, *args, **kwargs):
        super(Session, self).save(*args, **kwargs)


    
    # def __save__(self, *args, **kwargs):
    #     cache.set('amount_of_sessions', Session.objects.count(), 60*60)
    #     super(Session, self).save(*args, **kwargs)


class TimePeriod(models.Model):
    """Временные промежутки по N минут"""
    STATUS = (
        ('B', "Забронировано"),
        ('F', 'Свободно'),
        ('TB', 'Перерыв между бронями')
    )

    time = models.CharField(verbose_name="Время", blank=False, help_text="Формат: XX:XX", max_length=5)
    status = models.CharField(choices=STATUS, verbose_name="Статус временного промежутка", default='F', max_length=2)
    computer = models.ForeignKey(Computer, verbose_name="Компьютер", on_delete=models.CASCADE, related_name='time_periods')

    def __str__(self) -> str:
        return str(self.time)
    
    @staticmethod
    def convert_to_second(hours=0, minutes=0): 
        """Переводит из часов и минут в секунды с начала дня (с 00:00)"""
        return (hours * 60 + minutes) * 60

    @staticmethod
    def get_now_only_h_s() -> list: 
        """Возвращает текущие час и минуты"""
        now_sec = time.time() 
        now_struct = time.localtime(now_sec)
        return [now_struct.tm_hour, now_struct.tm_min]
    
    @staticmethod
    def start_end_time_to_sec(time:str) -> str: 
        """Преобразует из вида XX:XX в секунды с начала дня (с 00:00)"""
        hours, minutes = map(int, time.split(':'))
        return TimePeriod.convert_to_second(hours, minutes)

    @staticmethod
    def get_closest_time_div_15(time:str) -> str:
        """ 
        Находит ближайшее кол-во минут, меньшее заданного, делящегося на 15:
        * 16:37 -> 16:30 
        * 16:46 -> 16:45 
        * 16:59 -> 16:45 
        """

        hours = int(time.split(':')[0]) # вынести в отдельную функцию
        minutes = (int(time.split(':')[1]) // 15) * 15
        if minutes < 10:
            return f'{hours}:0{minutes}'
        if hours < 10:
            return f'0{hours}:{minutes}0'
        return f'{hours}:{minutes}'

    @staticmethod
    def get_now_in_sec() -> int:
        """ Возвращает текущее время в секундах с начала дня. """
        now_struct = time.gmtime() # now in struct
        hours = now_struct.tm_hour * 60 * 60 # часы в секундах
        minutes = now_struct.tm_min * 60 # минуты в секундах
        seconds = now_struct.tm_sec
        return hours + minutes + seconds
    
    @staticmethod
    def get_now_time_str() -> str:
        """ Возвращает время с начала дня в виде -> 16:23"""
        hours, minutes = TimePeriod.get_now_only_h_s()
        if minutes < 10:
            return f'{hours}:0{minutes}'
        if hours < 10:
            return f'0{hours}:{minutes}'
        return f'{hours}:{minutes}'

    @staticmethod
    def to_readable(seconds:int) -> str: 
        """Преобразует из секунд c начала дня в удобочитаемое время"""
        return f"{seconds // 3600}:{seconds // 60 % 60}"
    
    @staticmethod
    def compare_two_str_time(time1:str, time2:str) -> bool:
        """ Возвращает True, если time1 > time2. False в обратном случае. """
        time1_s = time1.split(':')
        time2_s = time2.split(':')
        if int(time1_s[0]) == int(time2_s[0]):
            return time1_s[1] > time2_s[1]
        return time1_s[0] > time2_s[0]
    



