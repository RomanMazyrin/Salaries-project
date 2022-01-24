from django.db import models


class OnpbxAccount(models.Model):

    subdomain = models.CharField("Субдомен", max_length=255)
    api_key = models.CharField("Ключ API", max_length=255)

    def __str__(self):
        return self.subdomain

    class Meta:
        verbose_name = 'Аккаунт OnlinePBX'
        verbose_name_plural = 'Аккаунты OnlinePBX'