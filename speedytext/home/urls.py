from django.urls import path, include
from home import views
urlpatterns = [
    path('',views.converting, name='converter'),
]
    