from django import forms
from django.forms import ModelForm
from .models import League

#League Registration Form, asks for ID, # of teams, # of rounds
class LeagueRegisterForm(ModelForm):

    class Meta:
        model = League
        exclude = ('user','draft_order','curr_round','curr_pick','date_created',)
        fields = ['leagueId', 'teams', 'rounds']
        labels = {'leagueId': "League ID", 'teams': "# of Teams", 'rounds': "# of rounds"}
        
    def __init__(self,user,*args,**kwargs):
        self.user = user
        super(LeagueRegisterForm, self).__init__(*args, **kwargs)