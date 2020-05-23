from django import forms
from .models import League

class LeagueRegisterForm():
    id = forms.IntegerField(label='League ID')
    teams = forms.IntegerField(label='# of Teams')
    rounds = forms.IntegerField(label='# of Rounds')

    class Meta:
        model = League
        fields = ['leagueId', 'teams', 'rounds']