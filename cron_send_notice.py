import os
import django
import logging


""" Внешний скрипт вне Django. Но благодаря конструкции ниже позволяет получить доступ к моделям."""
def send_notification():
    from booking.views import send_message
    from notifications.models import Notification
    from booking.models import TimePeriod
    from config.settings import DEBUG
    from booking.views import create_kb_book
    
    logger = logging.getLogger(__name__)
    notifs = Notification.objects.exclude(status="S")

    logger.info("Выполняю скрипт cron_send_notice.py")
    logger.info(f"Нашел {notifs.count()} неотправленных уведомдений.")

    for notif in notifs:
        logger.info(f"Уведомление №{notif.pk}. Его статус={notif.status}")
        if notif.status in ('W', 'NTS') : # Уведомление ожидает отправки
            if TimePeriod.start_end_time_to_sec(notif.time) <= TimePeriod.get_now_in_sec(): # если пришло время уведомления
                can_book = False
                is_sesion_in_progress = True
                if "игру!" in notif.text:  # !!!!!!!!!!!!!!!!!!!!!!!УДАЛИУДАЛИУДАЛИУДАЛИУДАЛИУДАЛИУДАЛИУДАЛИУДАЛИУДАЛИ
                    can_book = True
                    is_sesion_in_progress = False

                send_message(notif.user_vk_id, notif.text, create_kb_book(can_book, is_sesion_in_progress))
                logger.info(f"Успешно оправлено уведомление №{notif.pk}")
                notif.status = 'S'
                notif.save()


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
send_notification()


"""
Редактирование Cron
Для того чтобы настроить cron для запуска скрипта каждые две минуты, вам нужно открыть crontab файл для редактирования. Вы можете сделать это с помощью команды crontab -e в терминале.
"""