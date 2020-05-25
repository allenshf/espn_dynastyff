from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


#League
class League(models.Model):
    leagueId = models.IntegerField()
    teams = models.IntegerField(default=10)
    rounds = models.IntegerField(default=4)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    draft_order = models.CharField(max_length=500)
    curr_round = models.IntegerField()
    curr_pick = models.IntegerField()
    date_created = models.DateTimeField(default=timezone.now)
    unique_key = models.CharField(max_length=50, unique=True) #leagueId+username

    def __str__(self):
        return 'League ' + str(self.leagueId)


#Free Agents in a league        
class Player(models.Model):
    rank = models.IntegerField()
    name = models.CharField(max_length=50)
    team = models.CharField(max_length=5)
    position = models.CharField(max_length=5)
    projection = models.IntegerField()
    points = models.IntegerField()
    drafted = models.BooleanField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

#Picks in a league
class Pick(models.Model):
    round = models.IntegerField()
    number = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str__(self):
        return 'Pick ' + str(self.round) + '.' + str(self.number)

#Teams in a league
class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str(self):
        return self.name
        


