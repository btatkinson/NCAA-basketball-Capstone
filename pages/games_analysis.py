import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from collections import Counter

df = pd.read_csv('src/test_games.csv')

def team_pbp_df(school, year):

  """
  school: the name of the school as a string (proper casing is used)
  year: the season as an integer NOTE: the 2020-2021 CBB season is indicated with a value of 2020 – a game that occurred on 3/7/2021 will have a
        a value of 2020 (????? MAYBE ????? NEEDS FURTHER EVALUATION)
  """

  # filter for top team market and name and season in both home and away columns
  # grab the unique ids for those games
  team_games = df[(df['play.on_court.home.market'] == school) | (df['play.on_court.away.market'] == school)]['meta.id'].unique()

  # filter the original dataframe for those game_ids
  team = df[(df['meta.id'].isin(team_games))]

  ### STACK DATAFRAMES ON TOP OF EACH OTHER
  # so that we don't have to check home/away

  # only grab the columns without home/away
  aw = [i for i in team.columns if 'home' not in i]
  hm = [i for i in team.columns if 'away' not in i]

  # filter dataframe for only those columns
  away_df = team[aw]
  home_df = team[hm]

  # rename the columns for each df with 'team' instead of home/away
  away_df.columns = [i.replace('away','team') for i in away_df.columns]
  home_df.columns = [i.replace('home','team') for i in home_df.columns]

  # stack home/away dfs on top of each other
  combo = pd.concat([away_df,home_df])

  combo = combo[combo['year'] == year]

  return combo

def player_oncourt_season(pbp_df, school, playername):

    """
    pbp_df: the dataframe returned by the function team_pbp_df
    school: the name of the school as a string (e.g., "Auburn", "Michigan", "Ohio State")
    playername: the name of the player as a string
    """
    # this is just used to get the example player in the eda notebook
    player_cols = [i for i in pbp_df if all(['team.player' in i, 'full_name' in i])]
    c = Counter()
    cts = Counter(list([item for sublist in pbp_df[player_cols].values for item in sublist]))
    cts_li = sorted(dict(cts).items(),key=lambda x: x[1],reverse=True)

    # create a list of columns to keep in the resulting df
    cols_to_keep = ['meta.id','meta.scheduled','play.id','play.clock','play.description','play.team_points','play.event_type','play.on_court.team.market',
                    'play.on_court.team.name','type', 'made', 'shot_type', 'three_point_shot','player.full_name', 'player.jersey_number', 'rebound_type', 
                    'points','free_throw_type', 'shot_type_desc', 'play.clock.seconds','play.period', 'play.clock.seconds_game', 'play.clock.time_elapsed',
                    'play.on_court.team.player1.full_name','play.on_court.team.player2.full_name','play.on_court.team.player3.full_name',
                    'play.on_court.team.player4.full_name','play.on_court.team.player5.full_name', 'label']
    #filter to include columns
    filt = pbp_df[cols_to_keep]
    # filter to only include rows that are null or the exact school
    # sometimes pbp rows are null because they are things like "end of first half"
    filt = filt[(filt['play.on_court.team.market'].isnull()) | (filt['play.on_court.team.market'] == school)]
    # Sort vlaues by game and seconds remaining in game, fillna with previous values
    filt = filt.sort_values(by=['meta.scheduled','play.clock.seconds_game'],ascending=False).fillna(method='ffill')
    # create a column with comma separated player names
    filt['on_court_players'] = filt[['play.on_court.team.player1.full_name','play.on_court.team.player2.full_name','play.on_court.team.player3.full_name',
        'play.on_court.team.player4.full_name','play.on_court.team.player5.full_name']].agg(', '.join, axis = 1)

    # new df with a new column that states whether or not target player is on the court
    gs = filt.copy()
    gs['player_on'] = gs['on_court_players'].str.contains(playername)


    ### PROBLEM AREA
    # I think something is going wrong with the creation of the "to" column
    # Shifting the column with the groupby is not working to
    # There are times that the to column in the resulting data is a number way smaller than the from column
    
    # truncate columns
    line_df = gs[['meta.id','meta.scheduled','play.clock.seconds_game','player_on']]
    # create to column by groupby and shift
    line_df['to'] = line_df.groupby(['meta.id','meta.scheduled'],as_index=False)['play.clock.seconds_game'].shift(-1).fillna(0).astype(int)
    # rename columns
    line_df = line_df.rename(columns={'play.clock.seconds_game':'from','meta.id':'id'})
    # change time remaing columns to count up towards 2400 (needed for viz)
    line_df['from'] = abs(2400 - line_df['from'])
    line_df['to'] = abs(2400 - line_df['to'])
    # drop duplicates in to/from columns
    line_df = line_df.drop_duplicates(subset=['from','to'])
    # find the rows in which the player's status changes from on-court to off-court
    line_df['change'] = line_df['player_on'].astype(int) == line_df['player_on'].astype(int).shift(1)

    # filter to only include rows where on/off-court status is different
    change = line_df[line_df['change'] == False]
    change['to'] = change['from'].shift(-1).fillna(0)


    trunc_line_df = change.copy()
    # only include rows where player is on-court
    trunc_line_df = trunc_line_df[(trunc_line_df['player_on'] == 1)]
    
    trunc_line_df = trunc_line_df.merge(df[['id','label']],left_on='id',right_on='id')
    trunc_line_df['to'] = trunc_line_df['to'].replace(0,2400)

    return trunc_line_df

def app():
  st.dataframe(df)
   

