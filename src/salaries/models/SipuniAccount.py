from django.db import models
from packages.Sipuni.Client import Client


class SipuniAccount(models.Model):

    user_id = models.CharField("ID пользователя (user_id)", max_length=255)
    secret_key = models.CharField("Секретный ключ", max_length=255)

    class Meta:
        verbose_name = "Аккаунт Sipuni"
        verbose_name_plural = "Аккаунты Sipuni"

    @property
    def client(self):
        return Client(self.user_id, self.secret_key)
