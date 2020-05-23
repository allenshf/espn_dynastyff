from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class League(models.Model):
    leagueId = models.IntegerField()
    teams = models.IntegerField()
    rounds = models.IntegerField()

    def __str__(self):
        return 'League ' + str(self.leagueId)
        
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

class Pick(models.Model):
    round = models.IntegerField()
    number = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str__(self):
        return 'Pick ' + str(self.round) + '.' + str(self.number)

class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str(self):
        return self.name
        


