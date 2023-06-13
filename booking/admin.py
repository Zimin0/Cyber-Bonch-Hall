from django.contrib import admin
from .models import Session, TimePeriod

class SessionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'time_start','time_end', 'computer')
    list_filter = ['time_start', 'computer']

class TimePeriodAdmin(admin.ModelAdmin):
    list_display = ('time','status', 'computer')
    list_filter = ['time', 'status', 'computer']

admin.site.register(Session, SessionAdmin)
admin.site.register(TimePeriod, TimePeriodAdmin)