from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='Draft Home'),
    path('fa/', views.external, name='fa-found')
]