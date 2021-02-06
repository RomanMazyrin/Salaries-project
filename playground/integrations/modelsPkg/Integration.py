from django.db import models


class Integration(models.Model):
	client_id = models.CharField(max_length=255)
	client_secret = models.CharField(max_length=255)
	redirect_uri = models.TextField(blank=True)
	sys_name = models.SlugField("Системное имя интеграции", max_length=255)
	logo = models.ImageField("Логотип", blank=True)
	site_link = models.URLField("Ссылка на сайт", blank=True, max_length=3000)

	def __str__(self):
		return self.sys_name

	class Meta:
		verbose_name = "Интеграция"
		verbose_name_plural = "Интеграции"
