#First need to import espn_api library to computer
#Use command: pip insatall espi_api
from espn_api.football import League
import pandas as pd
import sqlite3
from os import path
import sys

#Establish SQL connection
DATA_DIR = 'C:/Users/dude0/Desktop/RookieDraft/rookiedraft' #Insert local directory path for sqlite database
conn = sqlite3.connect(path.join(DATA_DIR, 'freeagent.sqlite'))

#Request league info from API
leagueID = int(sys.argv[1])
league = League(league_id = leagueID, year = 2020)

#Collect list of top free agents
fa = league.free_agents(size=150)

#Create list of what player info we want
fa_info = [[fa.index(player) + 1, player.name, player.proTeam, player.position,
           player.projected_points, player.points, False] for player in fa]


#Create list of all owners
teams = [team.team_name for team in league.teams]

#Turn list into table
fa_df = pd.DataFrame(fa_info, columns = ['Rank', 'Name', 'Team', 'Position', 'Projected_Points', 'Points', 'Drafted'])
team_df = pd.DataFrame(teams, columns = ['Name'])

fa_df.to_sql('free_agents', conn, index = False, if_exists = 'replace')
team_df.to_sql('teams', conn, index=False, if_exists='replace')
