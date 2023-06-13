from django.urls import path, include
from django.contrib import admin
from config import settings
from django.conf.urls.static import static

urlpatterns = [ 
    path('vk_bot/admin/', admin.site.urls), # Занести в урлы vk_bot не получится
    path('vk_bot/', include('booking.urls')),
]

if settings.DEBUG:
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns