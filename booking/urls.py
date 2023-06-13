from django.urls import path, include
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.index, name='index'),
    path('info/', views.info, name='info'),
    path('free/', views.free_sessions, name='free'),
    #path('__debug__/', include('debug_toolbar.urls')),
]