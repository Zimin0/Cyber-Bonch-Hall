import os
import django


""" Внешний скрипт вне Django. Но благодаря конструкции ниже позволяет получить доступ к моделям."""
def send_notification():
    from booking.views import send_message
    from notifications.models import Notification
    from booking.models import TimePeriod
    from config.settings import DEBUG
    if DEBUG: print("Выполняю скрипт cron_send_notice.py")
    notifs = Notification.objects.exclude(status="S")

    if DEBUG: print(f"Нашел {notifs.count()} неотправленных уведомдений.")
    for notif in notifs:
        if DEBUG: print(f"Уведомление №{notif.pk}. Его статус={notif.status}")
        if notif.status in ('W', 'NTS') : # Уведомление ожидает отправки
            if DEBUG: print(TimePeriod.start_end_time_to_sec(notif.time), TimePeriod.get_now_in_sec())
            if TimePeriod.start_end_time_to_sec(notif.time) <= TimePeriod.get_now_in_sec(): # если пришло время уведомления
                send_message(notif.user_vk_id, notif.text)
                if DEBUG: print(f"Успешно оправлено уведомление №{notif.pk}")
                notif.status = 'S'
                notif.save()
        ## Добавить логирование


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
send_notification()


"""
Редактирование Cron
Для того чтобы настроить cron для запуска скрипта каждые две минуты, вам нужно открыть crontab файл для редактирования. Вы можете сделать это с помощью команды crontab -e в терминале.
"""