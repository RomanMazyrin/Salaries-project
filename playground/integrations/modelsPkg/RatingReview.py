from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from .Integration import Integration


class RatingReview(models.Model):
	integration = models.ForeignKey(Integration, on_delete=models.CASCADE, verbose_name='Интеграция')
	is_published = models.BooleanField('Опубликовано', default=False)
	review_text = models.TextField("Текст отзыва", blank=True)
	rating_value = models.IntegerField(choices=[
		(1, "1"),
		(2, "2"),
		(3, "3"),
		(4, "4"),
		(5, "5")
	], validators=[MaxValueValidator(5), MinValueValidator(1)])
	created_date = models.DateTimeField(default=timezone.now, editable=False)

	def __str__(self):
		cut_length = 30
		return self.created_date.strftime("%d.%m.%Y, %H:%M") + ": " + self.review_text[0:cut_length] + ("..." if len(self.review_text) > len(self.review_text[0:cut_length]) else "")

	class Meta:
		verbose_name = 'Отзыв'
		verbose_name_plural = 'Отзывы'