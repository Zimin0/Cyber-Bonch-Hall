import os
import django
import logging


""" Внешний скрипт вне Django. Но благодаря конструкции ниже позволяет получить доступ к моделям."""
def clear_database():
    from booking.models import Session, TimePeriod
    from django.core.cache import cache
    logger = logging.getLogger(__name__)
    cache.clear() # Очистка кэша
    logger.info("Кэш очищен.")
    Session.objects.all().delete()
    logger.info("Сесии очищены.")
    times = TimePeriod.objects.all().iterator() # https://django.fun/ru/articles/tips/sovety-po-optimizacii-raboty-s-bazoj-dannyh-v-django/
    for time in times:
        if time.status != 'F':
            time.status = 'F'
            time.save()
    logger.info("Временные промежутки очищены.")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
clear_database()


"""
Редактирование Cron
Для того чтобы настроить cron для запуска скрипта каждые две минуты, вам нужно открыть crontab файл для редактирования. Вы можете сделать это с помощью команды crontab -e в терминале.
"""