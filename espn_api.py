import requests
import pandas as pd
from pandas import DataFrame
import numpy as np
import sqlite3
from os import path

league_id = 331933
year = 2019

#espn API ul
url = f'https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}?seasonId={year}'

resp = requests.get(url)

d = resp.json()[0]
"""Columns: gameId, id, members [(displayName, id, isLeagueManager)], scoringPeriodId,
        seasonId, segmentId, settings (name), status (currentMatchupPeriod, isActive, latestScoringPeriod),
        teams [(abbrev, id, location, nickname, owners)]
"""

#Establish SQL connection
DATA_DIR = '' #Insert local directory path for sqlite database
conn = sqlite3.connect(path.join(DATA_DIR, 'fantasy.sqlite'))

#Create table of team name and ids
team_data = [[
    team['location'] + team['nickname'],
    team['id']]
    for team in d['teams']]

#Turn to DataFrame
team_df = pd.DataFrame(team_data, columns = ['Team Name', 'ID'])
team_df.set_index('ID')

#Get matchup data
resp = requests.get(url, params={"view":"mMatchup"})
d = resp.json()[0]
"""Keys: [draftDetail (drafted, inProgress), gameId, id,
        schedule [(away, home, id, matchupPeriodId, winner)]
            for each home and away, (cumulativeScore, gamesPlayed, pointsByScoringPeriod, teamId, totalPoints)
        scoringPeriodId, seasonId, segmentId, status (bunch of info),
        teams [(id, roster)
               for roster['entries'] (acquisition(Date,Type), injuryStatus, lineupSlotId, pendingTransactionIds, playerId,
                    playerPoolEntry (active, defaultPositionId, droppable, eligibleSlots, firstName, fullName, id, injured, injuryStatus, lastName, lastNewsDate, lastVideoDate, proTeamId, rankings, universeId),
                    status)]
    Useful: schedule, teams[index]['roster']['entries']
"""

#From schedule retrive desired columns
df = [[
   game['matchupPeriodId'],
   game['home']['teamId'], game['home']['totalPoints'],
   game['away']['teamId'], game['away']['totalPoints'], game['winner']
   ] for game in d['schedule'] if 'away' in game.keys()]

#Set as DataFrame, and add matchup type to filter for playoffs
df = pd.DataFrame(df, columns=['Week', 'Team1', 'Score1', 'Team2', 'Score2', 'Winner'])
df['Type'] = ['Regular' if w<=14 else 'Playoff' for w in df['Week']]

df.to_sql('matchups', conn, index = False, if_exists = 'replace')



#Code to sort matchups by team
teamId = 1


def getResults(teamId):
    
    avgs = (df
        .filter(['Week', 'Score1', 'Score2'])
        .melt(id_vars=['Week'], value_name='Score')
        .groupby('Week')
        .mean()
        .reset_index()
        )

    # grab all games with this team
    df2 = df.query('Team1 == @teamId | Team2 == @teamId').reset_index(drop=True)
    
    # move the team of interest to "Team1" column
    ix = list(df2['Team2'] == teamId)
    df2.loc[ix, ['Team1','Score1','Team2','Score2']] = \
        df2.loc[ix, ['Team2','Score2','Team1','Score1']].values
    
    # add new score and win cols
    df2 = (df2
     .assign(Chg1 = df2['Score1'] - avgs['Score'],
             Chg2 = df2['Score2'] - avgs['Score'],
             Win  = df2['Score1'] > df2['Score2'])
    )
    
    conditions = [ 
        df2['Chg1'] == df2['Chg2'],
        (((df2['Chg1'] > 0) & (df2['Chg2'] > 0)) | (df2['Chg1'] < 0)) & df2['Win'],
        (((df2['Chg1'] < 0) & (df2['Chg2'] < 0)) | (df2['Chg1'] > 0)) & (~df2['Win']),
        df2['Win'], ~df2['Win']
        ]
        
    choices = ['Tie','Lucky Win', 'Unlucky Loss', 'Win', 'Loss']
    df2['Result'] = np.select(conditions, choices)
    return df2

results = getResults(2)

print(results)
print(team_df)

