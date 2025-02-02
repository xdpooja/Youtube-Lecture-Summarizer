from django.urls import path
from . import views

urlpatterns = [
    path('', views.converting, name='home'),  # This will handle the root URL
    path('api/summarize/', views.api_summarize, name='api_summarize'),
]
