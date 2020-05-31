# pylint: skip-file
from django.db import models
from django.contrib.auth.models import User


class VKToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField('VK Token', max_length=100, default='')

    def __str__(self):
        return f'<Token of {self.user}: {self.token}>'

    class Meta:
        verbose_name = 'VK Token'
        verbose_name_plural = 'VK Tokens'
