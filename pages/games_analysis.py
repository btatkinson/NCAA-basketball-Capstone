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
  
  option_game = st.selectbox(
     'Please choose a game...',
     df[(df['play.on_court.away.market'] == option_team) | (df['play.on_court.home.market'] == option_team)]['label'].unique())
  
  score = df[df['label'] == option_game]
  score = score[['play.home_points','play.away_points','play.clock.seconds_game','play.on_court.away.market','play.on_court.away.name',
        'play.on_court.home.market','play.on_court.home.name','meta.home.color','meta.away.color']]
  score.columns = ['home','away','time','home_market','home_name','away_market','away_name','home_color','away_color']
  score['time'] = abs(2400 - score['time'])
  score = score.fillna(method='ffill')
  
  score['score_diff'] = score['home'] - score['away']
  score['leading_team'] = np.where(score['score_diff'] > 0,'home','away')
  
  home_color = score['home_color'].iloc[0]
  away_color = score['away_color'].iloc[0]
  
  lineups = df[df['label'] == option_game]
  
  player_names = [i for i in [i for i in df.columns if 'full_name' in i] if 'on_court' in i]

  home_players = [i for i in player_names if 'home' in i]
  away_players = [i for i in player_names if 'away' in i]
  
  lineups['home_lineup'] = lineups[home_players].fillna(method='ffill').agg(', '.join,axis=1).apply(lambda x: ', '.join(sorted(x.split(', '))))
  lineups['away_lineup'] = lineups[away_players].fillna(method='ffill').agg(', '.join,axis=1).apply(lambda x: ', '.join(sorted(x.split(', '))))
  
  lineups = lineups[['play.home_points','play.away_points','play.clock.seconds_game','play.on_court.away.market','play.on_court.away.name',
        'play.on_court.home.market','play.on_court.home.name','home_lineup','away_lineup','meta.home.color','meta.away.color']].fillna(method='ffill')
  
  a = lineups[['play.home_points','play.away_points','play.clock.seconds_game','play.on_court.away.market','play.on_court.away.name','away_lineup','meta.away.color']]
  h = lineups[['play.home_points','play.away_points','play.clock.seconds_game','play.on_court.home.market','play.on_court.home.name','home_lineup','meta.home.color']]
  
  a.columns = ['home_points','away_points','time','team_market','team_name','lineup','color']
  h.columns = ['home_points','away_points','time','team_market','team_name','lineup','color']
  
  ha = pd.concat([h,a])
  ha['from'] = abs(2400 - ha['time'])
  ha['to'] = abs(2400 - ha.groupby(['team_market','team_name'])['time'].shift(-1).fillna(0).astype(int))
  ha = ha.drop_duplicates(subset=['team_market','from','to'])
  
  home = ha[ha['team_market'] == ha['team_market'].iloc[0]]
  away = ha[ha['team_market'] == ha['team_market'].iloc[-1]]

  home['change'] = home['lineup'] == home['lineup'].shift(1)
  away['change'] = away['lineup'] == away['lineup'].shift(1)
  
  h_change = home[home['change'] == False]
  a_change = away[away['change'] == False]
  
  h_change['to'] = h_change['from'].shift(-1).fillna(2400).astype(int)
  a_change['to'] = a_change['from'].shift(-1).fillna(2400).astype(int)
  
  h_change['point_diff'] = (h_change['home_points'] - h_change['away_points']).shift(-1).fillna(method='ffill')
  a_change['point_diff'] = (a_change['away_points'] - a_change['home_points']).shift(-1).fillna(method='ffill')
  
  h_change['point_diff_stint'] = (h_change['point_diff'] - h_change['point_diff'].shift(1)).fillna(0)
  a_change['point_diff_stint'] = (a_change['point_diff'] - a_change['point_diff'].shift(1)).fillna(0)
  
  h_change['lineup_sorted'] = h_change['lineup'].apply(lambda x: ', '.join(sorted(x.split(', '))))
  
  h_change['time_played'] = (h_change['to'] - h_change['from']) / 60
  a_change['time_played'] = (a_change['to'] - a_change['from']) / 60
  
  h_change['home_id'] = list(range(len(h_change)))
  h_change['time_old'] = abs(2400 - h_change['time'])
  
  a_change['away_id'] = list(range(len(a_change)))
  a_change['time_old'] = abs(2400 - a_change['time'])
  
  score_id = score.merge(h_change[['home_points','away_points','time_old','home_id']],left_on=['home','away','time'], \
                          right_on=['home_points','away_points','time_old'],how='left').fillna(method='ffill')
  score_id = score_id.merge(a_change[['home_points','away_points','time_old','away_id']],left_on=['home','away','time'], \
                        right_on=['home_points','away_points','time_old'],how='left').fillna(method='ffill')
  
  h_color = h_change['color'].iloc[0]
  a_color = a_change['color'].iloc[0]

  #interactivity
  sel = alt.selection_single(on='mouseover')
  colorbar = alt.Color('point_diff:Q',scale=alt.Scale(scheme='viridis'), legend = alt.Legend(title = 'Score Difference'))
  opacity_cond = alt.condition(sel,alt.value(1),alt.value(.4))

  #more preprocessing
  all_times = pd.DataFrame(list(range(2401)),columns=['time'])
  score_id_all = all_times.merge(score_id,how='left').fillna(method='ffill')
  score_id_all = score_id_all.drop_duplicates()

  #score line plot
  band = alt.Chart(score_id).mark_area(opacity=.5).encode(
      x=alt.X('time', axis=alt.Axis(title='Seconds into Game')),
      y=alt.Y('home', title = 'Score'),
      y2='away',
      color = alt.value('lightblue')
  ).properties(width=650)

  home_line = alt.Chart(score_id).mark_line(strokeWidth=4,color=alt.HexColor(h_color)).encode(
      x='time',
      y='home',
      #for some reason the dataframe has away_market and home_market flipped
      color = alt.Color(field = 'away_market', legend = alt.Legend(title = 'Team'), scale = alt.Scale(range = [h_color]))
  ).properties(width=650)

  away_line = alt.Chart(score_id).mark_line(strokeWidth=4,color=alt.HexColor(a_color)).encode(
      x='time',
      y='away',
      #for some reason the dataframe has away_market and home_market flipped
      color = alt.Color(field = 'home_market', legend = alt.Legend(title = ''), scale = alt.Scale(range = [a_color]))
  ).properties(width=650)

  #home bar chart
  h_bar = alt.Chart(h_change).mark_bar(size=40).encode(
      x = alt.X('from', axis=alt.Axis(title=h_change['team_market'].unique())),
      x2 = 'to',
      color= alt.Color('point_diff:Q',scale=alt.Scale(scheme='viridis'), legend = alt.Legend(title = 'Score Difference')),
      opacity=opacity_cond,
      tooltip=['lineup','point_diff_stint','point_diff','time_played']
  ).properties(height=50,width=650).add_selection(sel)

  #away bar chart
  a_bar = alt.Chart(a_change).mark_bar(size=40).encode(
      x = alt.X('from', axis=alt.Axis(title=a_change['team_market'].unique())),
      x2 = 'to',
      color=colorbar,
      opacity=opacity_cond,
      tooltip=['lineup','point_diff_stint','point_diff','time_played']
  ).properties(height=50,width=650).add_selection(sel)
  
  line_chart = (band+home_line+away_line).resolve_scale(color='independent').configure_axis(gridOpacity=.5).configure_view(strokeWidth=0)
  bar_chart = (h_bar&a_bar).configure_axis(gridOpacity=.5).configure_view(strokeWidth=0)
  
  st.altair_chart(line_chart)
  st.caption('The score line plot displays the cumulative score of each team throughout the game.')
  st.altair_chart(bar_chart)
  st.caption('''The two bar charts depict the various lineups used by each team over the course of the game.  Each block on a bar
             represents the 5-man unit that was used by the team (indicated on the x-axis) at different points in the game, where the length of each
             block corresponds to the time that the unit spent on the floor.  Each block is color coded for the cumulative score difference at the
             end of the unit's stint.  Placing your cursor over each block displays the names of the 5 players along with the plus/minus rating for
             that unit, the cumulative score difference, and the time played, in minutes, for that unit.''')

  team = team_pbp_df(option_team, 2022)

  option_player = st.selectbox(
     'Please choose a player...',
     team[(team['play.on_court.team.market'].isnull()) | (team['play.on_court.team.market'] == option_team)][['play.on_court.team.player1.full_name', \
     'play.on_court.team.player2.full_name','play.on_court.team.player3.full_name', 'play.on_court.team.player4.full_name', \
     'play.on_court.team.player5.full_name']].melt().value.unique())

  individual_player_times = player_oncourt_season(team, option_team, option_player)
  
  ### VISUALIZE

  # this isn't behaving the way i want, but is used to label halftime
  axis_labels = (
      "datum.time == 1 ? 'Half' : datum.time == 1200 ? 'Half' : 'Half'"
  )

  bars = alt.Chart().mark_bar(width=1).encode(
      x=alt.X('time',axis=alt.Axis(values=[1200],labelExpr=axis_labels, title = ''),scale=alt.Scale(domainMax=2400,domainMin=0,clamp=True,padding=0)),
      y=alt.Y('player_on',axis=None)
  ).properties(width=500,height=20)

  text = alt.Chart().mark_text(align='right',baseline='middle',dx=-260).encode(
      text='label'
  )

  text2 = alt.Chart().mark_text(align='left',baseline='middle',dx=260).encode(
      text='mp'
  )

  ticks = alt.Chart().mark_rule(color='white',strokeDash=[1,1],size=2).encode(
      x='half_time'
  )

  individual_player_chart = alt.layer(bars,text,text2,ticks, data=individual_player_times).facet(
                                      spacing=4,row=alt.Row('label',sort=alt.EncodingSortField(field='meta_scheduled'), 
                                                            header=alt.Header(title=None,labels=False))
  ).configure_axis(grid=False).configure_view(strokeWidth=1)
  
  st.altair_chart(individual_player_chart)
  st.caption('''For the selected team, you can display the playing time of each player for all games in the game dropdown menu with disconnected bar
               charts.  For each game, the presence of a bar represents the time that the selected player was in the game while the absence of a bar
               represents the time that the selected player was on the bench.  Note that not all players play in every game – for this reason, the
               number of games displayed can vary from player to player.''')

