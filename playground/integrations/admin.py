from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Integration
from .models import RatingReview


@admin.register(Integration)
class IntegrationAdminConfig(admin.ModelAdmin):
	list_display = ('sys_name', 'get_logo_small', 'get_link')
	save_on_top = True
	readonly_fields = ('get_logo', )
	
	fieldsets = (
		(None, {
			'fields': tuple((n.name for n in Integration._meta.fields if n.name not in ['logo', 'get_logo', 'id']))
		}),
		(None, {
			'fields': (('logo', 'get_logo'), )
		}),
	)

	def get_logo(self, obj):
		return mark_safe(f'<img src="{obj.logo.url}">')

	def get_link(self, obj):
		return mark_safe(f'<a href="{obj.site_link}" target="_blank">{obj.site_link}</a>')

	def get_logo_small(self, obj):
		return mark_safe(f'<img src="{obj.logo.url}" width="100px" height="70px">')

	get_logo.short_description = "Текущее лого"
	get_logo_small.short_description = Integration._meta.get_field("logo").verbose_name
	get_link.short_description = Integration._meta.get_field("site_link").verbose_name



@admin.register(RatingReview)
class RatingReviewAdmonConfig(admin.ModelAdmin):
	list_display = ('__str__', 'is_published', 'integration')
	list_editable = ('is_published', )