from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.views import generic
from .models import Integration, RatingReview


class IndexView(generic.ListView):

	def get_queryset(self):
		return Integration.objects.all()


class DetailView(generic.DetailView):
	model = Integration

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['ratings'] = context['integration'].ratingreview_set.filter(is_published=True)
		return context


def add_review(request, integration_id):
	integration = get_object_or_404(Integration, pk=integration_id)
	new_review = RatingReview(
		integration=integration,
		review_text=request.POST['review_text'],
		rating_value=int(request.POST.get('rating_value', 0))
	)

	try:
		new_review.full_clean()
		new_review.save()
	except ValidationError as e:
		print(e.message_dict)

	return HttpResponseRedirect(reverse('integrations:detail', args=(integration.id,)))
