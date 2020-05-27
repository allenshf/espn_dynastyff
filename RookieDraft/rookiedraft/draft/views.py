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

    #Validate League Registration Form
    if form.is_valid():
        try:
            League.objects.get(leagueId=leagueID, user=request.user).delete()
        except League.DoesNotExist:
            pass
        temp = form.save(commit=False)
        temp.user = request.user
        temp.unique_key = str(leagueID) + request.user.username
        temp.curr_round = 1
        temp.curr_pick = 1
        temp.save()
    else:
        messages.warning(request, 'Incorrect information entered')
        return redirect('draft-home')

    #Get current user
    user = request.user

    #Get league info from Django database
    league_mod = League.objects.get(leagueId=leagueID, user=user)
    num_rounds = league_mod.rounds
    num_teams = league_mod.teams

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
            pick = Pick(round=x+1,number=y+1,league=league_mod, player=player, owner='')
            pick.save()

    return redirect('/reset/' + str(leagueID))

@login_required
def reset(request, id):

    #Get current user
    user = request.user

    #Get league info from Django database
    league_mod = League.objects.get(leagueId=id, user=user)
    num_rounds = league_mod.rounds
    num_teams = league_mod.teams

    players = league_mod.player_set.all()
    for player in players:
        player.drafted = False
        player.save()

    placeholder = league_mod.player_set.get(name='placeholder')
    #Add picks to database
    for pick in league_mod.pick_set.all():
        pick.player = placeholder
        pick.owner = ''
        pick.save()
    
    league_mod.curr_pick = 1
    league_mod.curr_round = 1
    league_mod.save()

    #Go to display league
    return redirect('/draft/' + str(id))

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

    #Remove double spaces from team names
    users = [re.sub('  ',' ',team.name) for team in league.team_set.all()]

    #Get draft order
    draft_order = league.draft_order.split(',')
    draft_order = [{
        'name': name,
        'position': index,
    }for name,index in zip(draft_order,range(teams))]

    #Dict of picks in draft
    picks = []
    for x in range(rounds):
        draft_round = []
        for y in range(teams):
            draft_round.append({
                'player_first': league.pick_set.get(round=x+1,number=y+1).player.name.split(' ',1)[0],
                'player_last': league.pick_set.get(round=x+1,number=y+1).player.name.split(' ',1)[-1],
                'position': league.pick_set.get(round=x+1,number=y+1).player.position,
                'team' : league.pick_set.get(round=x+1,number=y+1).player.team,
                'round': x+1,
                'number': y+1,
                'owner': league.pick_set.get(round=x+1,number=y+1).owner,
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
    leagues = League.objects.all().filter(leagueId=id).order_by('-date_created')
    return render(request, 'draft/list.html',{'leagues': leagues,'id': id,})

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

    #Get league info from database
    league = League.objects.get(unique_key=key)
    rounds = league.rounds
    teams = league.teams
    players = league.player_set.all()

    #Free Agent information to pass to template
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

    #Pick information to pass to template
    picks = []
    for x in range(rounds):
        draft_round = []
        for y in range(teams):
            draft_round.append({
                'player_first': league.pick_set.get(round=x+1,number=y+1).player.name.split(' ',1)[0],
                'player_last': league.pick_set.get(round=x+1,number=y+1).player.name.split(' ',1)[-1],
                'position': league.pick_set.get(round=x+1,number=y+1).player.position,
                'team' : league.pick_set.get(round=x+1,number=y+1).player.team,
                'round': x+1,
                'number':y+1,
                'owner': league.pick_set.get(round=x+1,number=y+1).owner,

            })
        picks.append(draft_round)

    return render(request, 'draft/viewonly.html', {'players':fa_dict, 'rounds':range(rounds), 'league':league, 'order':draft_order, 'picks':picks})

#Draft Player Button
@login_required
def pickplayer(request, id, rank):

    #Get league from databse
    league = League.objects.get(leagueId=id, user=request.user)
    #Check if the draft is over
    if(league.curr_round > league.rounds):
        messages.warning(request, 'Draft is already complete')
        return redirect('/draft/' + str(id))

    #Get the current pick and link it to selected player
    otc_pick = league.pick_set.get(round=league.curr_round, number=league.curr_pick)
    picked_player = league.player_set.get(rank=rank)
    picked_player.drafted = True
    picked_player.save()
    otc_pick.player = picked_player
    otc_pick.save()

    #Update the current pick with the next pick
    league.curr_pick = league.curr_pick+1
    if(league.curr_pick > league.teams):
        league.curr_round = league.curr_round+1
        league.curr_pick = 1
    league.save()
    return redirect('/draft/' + str(id))

@login_required
def undo(request, id):
    
    #Get league from database
    league = League.objects.get(leagueId=id, user=request.user)
    #Check if there are previous picks to undo
    if(league.curr_round == 1 and league.curr_pick == 1):
        messages.warning(request, 'There is no pick to undo')
        return redirect('/draft/' + str(id))

    #Get previous pick information
    prev_round = league.curr_round
    prev_pick = league.curr_pick - 1
    if(prev_pick == 0):
        prev_round = prev_round - 1
        prev_pick = league.teams
    pick = league.pick_set.get(round=prev_round,number=prev_pick)
    player = pick.player

    #Revert pick information to default
    player.drafted = False
    player.save()
    pick.player = league.player_set.get(name='placeholder')
    pick.save()
    league.curr_pick = prev_pick
    league.curr_round = prev_round
    league.save()

    return redirect('/draft/' + str(id))

@login_required    
def trade(request, id):
    #Get league from database
    league = League.objects.get(leagueId=id, user=request.user)
    team = request.POST.get('team')
    round = request.POST.get('round')
    number = request.POST.get('pick')

    #Get pick to be traded
    pick = league.pick_set.get(round=round, number=number)
    draft_order = league.draft_order.split(',')
    #Check if team being traded is original owner
    if team == draft_order[int(number)-1]:
        pick.owner = ''
    else:
        pick.owner = team
    pick.save()
    return redirect('/draft/' + str(id))

@login_required
def delete_confirm(request,id):
    try:
        league = League.objects.get(leagueId=id, user=request.user)
    except League.DoesNotExist:
        messages.warning(request, "You don't own this league")
        next = request.POST.get('back')
        return redirect(next)
    return render(request, 'draft/confirm_delete.html', {'id':id})

@login_required
def delete(request, id):
    try:
        league = League.objects.get(leagueId=id, user=request.user)
    except League.DoesNotExist:
        messages.warning(request, "You don't own this league")
        return redirect('/')
    league = League.objects.get(leagueId=id, user=request.user).delete()
    messages.success(request, "League succesfully deleted")
    return redirect('/')