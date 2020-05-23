from django.shortcuts import render
import requests
from subprocess import run,PIPE
import sys
import sqlite3
from os import path
from .models import Pick, Player, League, Team


def home(request):
    return render(request, 'draft/home.html')

def draft(request):
   
    inp = request.POST.get('param')
    num_rounds = int(request.POST.get('numRounds'))
    num_teams = int(request.POST.get('numTeams'))
    
    out=run([sys.executable, 'C:\\Users\\dude0\\Desktop\\RookieDraft\\fa_request.py', inp], shell=False, stdout=PIPE)
    DATA_DIR = 'C:/Users/dude0/Desktop/RookieDraft/rookiedraft' #Insert local directory path for sqlite database
    conn = sqlite3.connect(path.join(DATA_DIR, 'freeagent.sqlite'))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM free_agents')
    result = cursor.fetchall()
    cursor.execute('SELECT * FROM teams')
    teams = cursor.fetchall()

    teams = [team[0] for team in teams]

    fa_dict = [
    {
        'rank': player[0],
        'name': player[1],
        'team': player[2],
        'position': player[3],
        'projection': player[4],
        'points': player[5],
        'drafted': player[6]
    } for player in result]

    try:
        League.objects.get(leagueId=inp).delete()
    except League.DoesNotExist:
        print('No league yet')
    League.objects.create(leagueId=inp, teams=num_teams,rounds=num_rounds)
    league = League.objects.get(leagueId=inp)

    for player in fa_dict:
        player_mod = Player(rank=player['rank'],name=player['name'],team=player['team'],
        position=player['position'],projection=player['projection'],points=player['points'],drafted=False)
        player_mod.save()
        league.players.add(player_mod)

    for team in teams:
        team_mod = Team(name=team)
        team_mod.save()
        league.users.add(team_mod)


    return render(request, 'draft/draftroom.html', {'players':fa_dict, 'rounds':range(num_rounds), 'teams':range(num_teams), 'names':teams})

def access(request, id):

    league = League.objects.get(leagueId=id)
    rounds = league.rounds
    teams = league.teams
    players = league.players.all()

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

    users = [team.name for team in league.users.all()]

    return render(request, 'draft/draftroom.html', {'players':fa_dict, 'rounds':range(rounds), 'teams':range(teams),'names':users})