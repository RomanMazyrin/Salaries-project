from django.db import models


class Setting(models.Model):

    name = models.SlugField('Строковой идентификатор параметра',
                            unique=True, blank=False, null=False)
    value = models.TextField("Значение параметра")
    description = models.CharField("Описание параметра", max_length=1000)

    class Meta:
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'
