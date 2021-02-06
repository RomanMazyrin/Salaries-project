from django.urls import path

from . import views

app_name = "integrations"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('add_review/<int:integration_id>/', views.add_review, name='add_review')
]