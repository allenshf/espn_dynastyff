from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
from subprocess import run,PIPE
import sys
import sqlite3
from os import path
from .models import Pick, Player, League, Team
from .forms import LeagueRegisterForm
from espn_api.football import League as League_espn
import pandas as pd


def home(request):
    return render(request, 'draft/home.html')

def draft(request):
   
    league_id = request.POST.get('param')
    num_rounds = request.POST.get('numRounds')
    num_teams = request.POST.get('numTeams')

    leagueID = int(league_id)
    league = League_espn(league_id = leagueID, year = 2020)

    #Collect list of top free agents
    fa = league.free_agents(size=150)

    #Create list of what player info we want
    fa_info = [[fa.index(player) + 1, player.name, player.proTeam, player.position,
            player.projected_points, player.points, False] for player in fa]

    #Create list of all owners
    teams = [team.team_name for team in league.teams]

    #Put in Django database
    try:
        League.objects.get(leagueId=leagueID).delete()
    except League.DoesNotExist:
        print('No league yet')
    League.objects.create(leagueId=leagueID, teams=num_teams,rounds=num_rounds)
    league_mod = League.objects.get(leagueId=leagueID)

    for player in fa:
            player_mod = Player(rank=fa.index(player)+1,name=player.name,team=player.proTeam,
            position=player.position,projection=player.projected_points,points=player.points,drafted=False, league=league_mod)
            player_mod.save()

    for team in teams:
        team_mod = Team(name=team, league=league_mod)
        team_mod.save()

    players = league_mod.player_set.all()

    fa_dict = [
    {
        'rank': player.rank,
        'name': player.name,
        'team': player.team,
        'position': player.position,
        'projection': player.projection,
        'points': player.points,
        'drafted':player.drafted
    } for player in players]

    users = [team.name for team in league_mod.team_set.all()]

    return render(request, 'draft/draftroom.html', {'players':fa_dict, 'rounds':range(int(num_rounds)), 'teams':range(int(num_teams)), 'names':users})

@login_required
def access(request, id):

    league = League.objects.get(leagueId=id)
    rounds = league.rounds
    teams = league.teams
    players = league.player_set.all()

    fa_dict = [
    {
        'rank': player.rank,
        'name': player.name,
        'team': player.team,
        'position': player.position,
        'projection': player.projection,
        'points': player.points,
        'drafted':player.drafted
    } for player in players]

    users = [team.name for team in league.team_set.all()]

    return render(request, 'draft/draftroom.html', {'players':fa_dict, 'rounds':range(rounds), 'teams':range(teams),'names':users})