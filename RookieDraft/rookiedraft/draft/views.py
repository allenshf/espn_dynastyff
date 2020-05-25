from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import requests
from subprocess import run,PIPE
import sys
import sqlite3
from os import path
from .models import Pick, Player, League, Team
from .forms import LeagueRegisterForm
from espn_api.football import League as League_espn
import pandas as pd
import re


def home(request):
    #Send League Registration Form
    form = LeagueRegisterForm(request.user)
    return render(request, 'draft/home.html', {'form': form})

@login_required
def draft(request):

    #Get info from form
    form = LeagueRegisterForm(request.user, request.POST)
    leagueID = request.POST.get('leagueId')

    #Call ESPN API
    try:
        league = League_espn(league_id = leagueID, year = 2020)
    except Exception:
        messages.warning(request, 'No Such League with this ID')
        return redirect('draft-home')

    #Get current user
    user = request.user

    #Validate form
    if form.is_valid():
        try:
            League.objects.get(leagueId=leagueID, user=user).delete()
        except League.DoesNotExist:
            pass
        temp = form.save(commit=False)
        temp.user = request.user
        temp.unique_key = str(leagueID) + user.username
        temp.curr_round = 1
        temp.curr_pick = 1
        temp.save()
    else:
        messages.warning(request, 'Incorrect information entered')
        return redirect('draft-home')

    #Get league info from Django database
    league_mod = League.objects.get(leagueId=leagueID, user=user)
    num_rounds = form.cleaned_data['rounds']
    num_teams = form.cleaned_data['teams']

    #Collect list of top free agents
    fa = league.free_agents(size=150)

    #Create list of what player info we want
    fa_info = [[fa.index(player) + 1, player.name, player.proTeam, player.position,
            player.projected_points, player.points, False] for player in fa]

    #Create list of all owners
    teams = [team.team_name for team in league.teams]

    #Initialize Draft Order
    for x in range(num_teams):
        if x+1 == num_teams:
            league_mod.draft_order += teams[x]
        else:
            league_mod.draft_order += teams[x] + ","
    league_mod.save()

    #Add players to database
    for player in fa:
            player_mod = Player(rank=fa.index(player)+1,name=player.name,team=player.proTeam,
            position=player.position,projection=player.projected_points,points=player.points,drafted=False, league=league_mod)
            player_mod.save()

    #Add teams to database
    for team in teams:
        team_mod = Team(name=team, league=league_mod)
        team_mod.save()

    player = Player(name='placeholder', position='NA',rank=0,team='NA',projection=0,points=0,drafted=False, league=league_mod)
    player.save()
    #Add picks to database
    for x in range(num_rounds):
        for y in range(num_teams):
            pick = Pick(round=x+1,number=y+1,league=league_mod, player=player)
            pick.save()    

    #Go to display league
    return redirect('/draft/' + str(leagueID))

#TODO: Allow user to enter in traded picks
@login_required
def access(request, id):

    #Get League Info
    try:
        league = League.objects.get(leagueId=id, user=request.user)
    except League.DoesNotExist:
        messages.warning(request, 'You do not own a league with this ID')
        return redirect('draft-home')
    rounds = league.rounds
    teams = league.teams
    players = league.player_set.all()

    #Get player and team info
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

    users = [re.sub('  ',' ',team.name) for team in league.team_set.all()]

    #Get draft order
    draft_order = league.draft_order.split(',')
    draft_order = [{
        'name': name,
        'position': index,
    }for name,index in zip(draft_order,range(teams))]

    picks = []
    for x in range(rounds):
        draft_round = []
        for y in range(teams):
            draft_round.append({
                'player': league.pick_set.get(round=x+1,number=y+1).player.name,
                'postition': league.pick_set.get(round=x+1,number=y+1).player.position,
                'round': x+1,
                'number':y+1,
            })
        picks.append(draft_round)

    return render(request, 'draft/draftroom.html', {'players':fa_dict, 'rounds':range(rounds),'names':users, 'league':league, 'order':draft_order, 'picks':picks})

def find(request):
    #Get ID searched
    leagueId = request.POST.get('leagueId')
    
    #Check if ID is valid integer
    try:
        leagueId = int(leagueId)
    except ValueError:
        messages.warning(request, 'Invalid Value Entered')
        next = request.POST.get('next','/')
        return redirect(next)

    return redirect('/league-list/' + str(leagueId))

#TODO: Maybe combine with views.find?
def leaguelist(request, id):
    #Find all leagues with searched ID
    leagues = League.objects.all().filter(leagueId=id)
    return render(request, 'draft/list.html', {'leagues': leagues, 'id': id})

@login_required
def saveorder(request, id):
    #Get League
    league = League.objects.get(leagueId=id, user=request.user)
    #Generate new order based on form
    new_order = ''
    for x in range(league.teams):
        name = 'team' + str(x)
        if x+1 == league.teams:
            new_order += request.POST.get(name)
        else:
            new_order += request.POST.get(name) + ','

    league.draft_order = new_order
    league.save()

    #Return to draft room
    return redirect('/draft/' + str(id))

#View-only version of draft room        
def viewonly(request, key):

    league = League.objects.get(unique_key=key)
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

    draft_order = league.draft_order.split(',')

    picks = []
    for x in range(rounds):
        draft_round = []
        for y in range(teams):
            draft_round.append({
                'player': league.pick_set.get(round=x+1,number=y+1).player.name,
                'postition': league.pick_set.get(round=x+1,number=y+1).player.position,
                'round': x+1,
                'number':y+1,
            })
        picks.append(draft_round)

    return render(request, 'draft/viewonly.html', {'players':fa_dict, 'rounds':range(rounds), 'league':league, 'order':draft_order, 'picks':picks})

