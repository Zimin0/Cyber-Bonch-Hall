from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        return f'Профиль пользователя {self.vk_id}' 
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    vk_id = models.CharField(max_length=200, verbose_name='Vk_id', null=True, blank=True, unique=True)
    #already_booked = models.BooleanField(verbose_name="Есть бронь на сегодня")

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

