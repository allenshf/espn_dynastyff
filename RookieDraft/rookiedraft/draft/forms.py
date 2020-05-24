from django import forms
from django.forms import ModelForm
from .models import League

class LeagueRegisterForm(ModelForm):

    class Meta:
        model = League
        exclude = ('user',)
        fields = ['leagueId', 'teams', 'rounds']
        labels = {'leagueId': "League ID", 'teams': "# of Teams", 'rounds': "# of rounds"}
        
    def __init__(self,user,*args,**kwargs):
        self.user = user
        super(LeagueRegisterForm, self).__init__(*args, **kwargs)