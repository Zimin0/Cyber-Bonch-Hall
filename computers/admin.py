from django.contrib import admin
from .models import Computer

class ComputerAdmin(admin.ModelAdmin):
    list_display = ('number','ready_to_use')

admin.site.register(Computer, ComputerAdmin )