import os
import django


""" Внешний скрипт вне Django. Но благодаря конструкции ниже позволяет получить доступ к моделям."""
def send_notification():
    from booking.views import send_message
    from notifications.models import Notification
    from booking.models import TimePeriod

    try:
        notifs = Notification.objects.exclude(status="S")
        for notif in notifs:
            if notif.status in ('W', 'NTS') : # Уведомление ожидает отправки
                time_now = f"{notif.time.hour}:{notif.time.second}"
                if TimePeriod.start_end_time_to_sec(time_now) <= TimePeriod.get_now_in_sec(): # если пришло время уведомления
                    send_message(notif.user_vk_id, notif.text)
                    notif.status = 'S'
                    notif.save()
    except Exception as e:
        print(e)
        ## Добавить логирование

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    send_notification()
