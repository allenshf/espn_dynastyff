from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='draft-home'),
    path('fa/', views.external, name='fa-found')
]