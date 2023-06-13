from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('pk','time', 'user_vk_id', 'type', 'status')

admin.site.register(Notification, NotificationAdmin)
