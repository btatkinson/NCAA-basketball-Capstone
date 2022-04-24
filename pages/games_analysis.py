import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from collections import Counter

df = pd.read_csv('src/test_games.csv')

def team_pbp_df(school, season):
  # find how many games we have for each team-season in the db

  # cut the number of cols, drop dupes, get counts, and reset index
  home = df[['meta.id','play.on_court.home.market','play.on_court.home.name','season']].drop_duplicates()[['play.on_court.home.market','play.on_court.home.name','season']].value_counts().reset_index()
  away = df[['meta.id','play.on_court.away.market','play.on_court.away.name','season']].drop_duplicates()[['play.on_court.away.market','play.on_court.away.name','season']].value_counts().reset_index()

  # change names of columns
  home.columns = ['market','name','season','count']
  away.columns = ['market','name','season','count']

  # stack home and away datasets
  ha = pd.concat([home,away])

  # sum up number of home and away games for each team-season
  game_counts = ha.groupby(['market','name','season'],as_index=False)['count'].sum().sort_values(by='count',ascending=False).reset_index(drop=True)

  # filter for top team market and name and season in both home and away columns
  # grab the unique ids for those games
  team_games = df[(df['play.on_court.home.market'] == school) | (df['play.on_court.away.market'] == school)]['meta.id'].unique()

  # filter the original dataframe for those game_ids
  team = df[(df['meta.id'].isin(team_games))]


  ### STACK DATAFRAMES ON TOP OF EACH OTHER
  # so that we don't have to check home/away for auburn data

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

  combo = combo[combo['season'] == season]

  return combo

def player_oncourt_season(pbp_df, school, playername):
  player_cols = [i for i in pbp_df.columns if all(['team.player' in i, 'full_name' in i])]

  from collections import Counter
  c = Counter()

  cts = Counter(list([item for sublist in pbp_df[player_cols].values for item in sublist]))

  cts_li = sorted(dict(cts).items(),key=lambda x: x[1],reverse=True)

  #player = cts_li[0][0]

  cols_to_keep = ['meta.id','meta.scheduled','play.id','play.clock','play.description','play.team_points','play.event_type','play.on_court.team.market',
                'play.on_court.team.name','type', 'made', 'shot_type', 'three_point_shot','player.full_name', 'player.jersey_number', 'rebound_type', 
                'points','free_throw_type', 'shot_type_desc', 'play.clock.seconds','play.period', 'play.clock.seconds_game', 'play.clock.time_elapsed',
                'play.on_court.team.player1.full_name','play.on_court.team.player2.full_name','play.on_court.team.player3.full_name',
                'play.on_court.team.player4.full_name','play.on_court.team.player5.full_name','meta.team.color', 'label']
  
  filt = pbp_df[cols_to_keep]

  filt = filt[(filt['play.on_court.team.market'].isnull()) | (filt['play.on_court.team.market'] == school)]

  filt = filt.sort_values(by=['meta.scheduled','play.clock.seconds_game'],ascending=False).fillna(method='ffill')

  filt['on_court_players'] = filt[['play.on_court.team.player1.full_name','play.on_court.team.player2.full_name','play.on_court.team.player3.full_name',
      'play.on_court.team.player4.full_name','play.on_court.team.player5.full_name']].agg(', '.join, axis = 1)

  gs = filt.copy()
  # filter data from only selected player
  gs['player_on'] = gs['on_court_players'].str.contains(playername)

  # create a dataframe that has all seconds from 0-2399
  # eventually we will create a bar chart that has a bar for each game second whose bars go to 1 when the player is on court
  all_times = pd.DataFrame(list(range(0,2400)),columns=['play.clock.seconds_game']).sort_values(by='play.clock.seconds_game',ascending=False)

  # drop dupes and rename columns
  gs_dedupe = gs.drop_duplicates(subset=['meta.id','play.clock.seconds_game']).rename(columns={'play.clock.seconds_game':'time',
                                                                                             'meta.id':'meta_id',
                                                                                             'meta.scheduled':'meta_scheduled'})

  # merge with the all_times dataframe to fill in time gaps
  gs_merged = (gs_dedupe.groupby(['meta_id','meta_scheduled']).apply(lambda group: all_times.merge(group[['time','player_on', 'label']],
                                                                                                 left_on=['play.clock.seconds_game'],
                                                                                                 right_on=['time'],how='left').fillna(method='bfill')))

  # reset index and rename time col
  gs_merged = gs_merged.reset_index().drop(columns=['level_2','time']).rename(columns={'play.clock.seconds_game':'time'})

  # change time col from bool to int
  #gs_merged['player_on'] = gs_merged['player_on'].astype(int)
  gs_merged.player_on = gs_merged.player_on.replace({True: 1, False: 0})

  # format mp column for each game
  gs_merged['mp_decimal'] = gs_merged.groupby('meta_id')['player_on'].transform('sum')

  from datetime import timedelta

  def get_time_mm_ss(sec):
      # create timedelta and convert it into string
      td_str = str(timedelta(seconds=sec))

      # split string into individual component
      x = td_str.split(':')
      return f"{x[-2]}:{x[-1]}"

  gs_merged['mp'] = gs_merged['mp_decimal'].apply(lambda x: get_time_mm_ss(x))

  # add for labeling purposes
  gs_merged['mp'] = gs_merged['mp'] + ' minutes'

  #gs_merged = gs_merged.merge(df,left_on='meta_id',right_on='meta.id')

  gs_merged = gs_merged.drop_duplicates(['meta_id','time'])

  alt.data_transformers.disable_max_rows()

  gs_merged['half_time'] = 1200

  cols_to_keep_viz = ['time','player_on','label','half_time','meta_scheduled','mp']

  gs_viz = gs_merged[cols_to_keep_viz]

  return gs_viz[gs_viz['label'].notna()]

def app():
  
  st.title('Play-by-Play + Substitution Analysis')
  st.markdown('''Using data provided by Sportradar – an organization that collects and analyzes sports data – we analyzed individual games on a
                play-by-play basis.  For the purposes of this app, we are limited to only a subset of games due to the constraints imposed by file
                size limits.  We selected games for a handful of teams occurring on or after January 1st, 2022 which you can explore with the various
                dropdown menus.''')
  
  option_team = st.selectbox(
     'Please choose a team...',
     ['Michigan', 'Michigan State', 'Kentucky', 'Duke', 'Kansas', 'Gonzaga'])
