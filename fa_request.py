#First need to import espn_api library to computer
#Use command: pip insatall espi_api
from espn_api.football import League
import pandas as pd

#Request league info from API
league = League(league_id = 331933, year = 2020)

#Collect list of top free agents
fa = league.free_agents(size=150)

#Create list of what info we want
fa_info = [[fa.index(player) + 1, player.name, player.proTeam, player.position,
           player.projected_points, player.points] for player in fa]

#Turn list into table
fa_df = pd.DataFrame(fa_info, columns = ['Rank', 'Name', 'Team', 'Position', 'Projected Points', 'Points'])
fa_df = fa_df.set_index('Rank')
