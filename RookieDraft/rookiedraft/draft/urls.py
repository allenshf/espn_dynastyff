from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='draft-home'),
    path('draft/', views.draft, name='draft-room'),
    path('reset/<int:id>/', views.reset, name='create-draft'),
    path('draft/<int:id>/', views.access, name='draft-room'),
    path('league/', views.find, name='searched-league'),
    path('league-list/<int:id>/', views.leaguelist, name='league-list'),
    path('save/<int:id>/', views.saveorder, name='save-draft-order'),
    path('view-only/<str:key>/', views.viewonly, name='view-only'),
    path('draft/<int:id>/<int:rank>/', views.pickplayer, name='pick-player'),
]