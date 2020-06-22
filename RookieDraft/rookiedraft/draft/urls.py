from django.urls import path
from . import views
from .views import LeagueListView

urlpatterns = [
    path('', views.home, name='draft-home'),
    path('draft/', views.draft, name='draft-room'),
    path('reset/<int:id>/', views.reset, name='create-draft'),
    path('draft/<int:id>/', views.access, name='draft-room'),
    path('league/', views.find, name='searched-league'),
    path('league-list/<int:id>/', LeagueListView.as_view(), name='league-list'),
    path('save/<int:id>/', views.saveorder, name='save-draft-order'),
    path('view-only/<str:key>/', views.viewonly, name='view-only'),
    path('draft/<int:id>/<int:rank>/', views.pickplayer, name='pick-player'),
    path('undo/<int:id>/', views.undo, name='undo-pick'),
    path('trade/<int:id>/', views.trade, name='trade-pick'),
    path('delete/<int:id>/', views.delete, name='delete-league'),
    path('delete/<int:id>/confirm/', views.delete_confirm, name='delete-confirm'),
    path('download/<int:id>/', views.download, name='draft-download'),
]