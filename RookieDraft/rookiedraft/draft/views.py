from django.shortcuts import render
import requests
from subprocess import run,PIPE
import sys
import sqlite3
from os import path



def home(request):
    return render(request, 'draft/home.html')

def external(request):
    inp = request.POST.get('param')
    rounds = request.POST.get('numRounds')
    teams = request.POST.get('numTeams')
    out=run([sys.executable, 'C:\\Users\\dude0\\Desktop\\RookieDraft\\fa_request.py', inp], shell=False, stdout=PIPE)

    DATA_DIR = 'C:/Users/dude0/Desktop/RookieDraft/rookiedraft' #Insert local directory path for sqlite database
    conn = sqlite3.connect(path.join(DATA_DIR, 'freeagent.sqlite'))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM free_agents')
    result = cursor.fetchall()

    fa_dict = [
    {
        'rank': player[0],
        'name': player[1],
        'team': player[2],
        'position': player[3],
        'projection': player[4],
        'points': player[5]
    } for player in result]

    return render(request, 'draft/players.html', {'players':fa_dict})
