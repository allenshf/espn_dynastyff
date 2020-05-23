from django import forms
from django.forms import ModelForm
from .models import League

class LeagueRegisterForm(ModelForm):

    class Meta:
        model = League
        fields = ['leagueId', 'teams', 'rounds']
        labels = {'leagueId': "League ID", 'teams': "# of Teams", 'rounds': "# of rounds"}