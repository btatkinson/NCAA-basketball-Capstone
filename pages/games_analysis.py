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

    return trunc_line_df

def app():
    
    option_team = st.selectbox(
     'Please choose a team...',
     ['Michigan', 'Michigan State', 'Kentucky', 'Duke', 'North Carolina', 'Kansas', 'Gonzaga', 'Villanova'])
    
    option_game = st.selectbox(
     'Please choose a game...',
     df[(df['play.on_court.away.market'] == option_team) | (df['play.on_court.home.market'] == option_team)]['label'].unique())
    
    #preprocessing
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
    colorbar = alt.Color('point_diff:Q',scale=alt.Scale(scheme='viridis'))
    opacity_cond = alt.condition(sel,alt.value(1),alt.value(.4))
    
    #more preprocessing
    all_times = pd.DataFrame(list(range(2401)),columns=['time'])
    score_id_all = all_times.merge(score_id,how='left').fillna(method='ffill')
    score_id_all = score_id_all.drop_duplicates()
    
    #score difference bar/line
    score_diff_line = alt.Chart(score_id_all).mark_bar(strokeWidth=3).encode(
         x=alt.X('time:Q',scale=alt.Scale(domainMax=2400,domainMin=0,clamp=True), axis = alt.Axis(title = '')),
         y=alt.Y('score_diff', title = 'Score Difference'),
         color = alt.condition("datum.score_diff > 0", alt.value(home_color), alt.value(away_color))
     ).properties(width=650,height=65)

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
         color = alt.Color(field = 'home_market', legend = alt.Legend(title = 'Team'), scale = alt.Scale(range = [h_color]))
    ).properties(width=650)

    away_line = alt.Chart(score_id).mark_line(strokeWidth=4,color=alt.HexColor(a_color)).encode(
         x='time',
         y='away',
         color = alt.Color(field = 'away_market', legend = alt.Legend(title = ''), scale = alt.Scale(range = [a_color]))
    ).properties(width=650)
    
    #home bar chart
    h_bar = alt.Chart(h_change).mark_bar(size=40).encode(
         x = alt.X('from', axis=alt.Axis(title='')),
         x2 = 'to',
         color= alt.Color('point_diff:Q',scale=alt.Scale(scheme='viridis'), legend = alt.Legend(title = 'Score Difference')),
         opacity=opacity_cond,
         tooltip=['lineup','point_diff_stint','point_diff','time_played']
    ).properties(height=50,width=650).add_selection(sel)
    
    #away bar chart
    a_bar = alt.Chart(a_change).mark_bar(size=40).encode(
         x = alt.X('from', axis=alt.Axis(title='')),
         x2 = 'to',
         color=colorbar,
         opacity=opacity_cond,
         tooltip=['lineup','point_diff_stint','point_diff','time_played']
    ).properties(height=50,width=650).add_selection(sel)
    
    final_chart = alt.vconcat((band+home_line+away_line).resolve_scale(color='independent'),(h_bar&score_diff_line&a_bar)).configure_axis(gridOpacity=.5).configure_view(strokeWidth=0)
    st.altair_chart(final_chart)
    
    team = team_pbp_df(option_team, 2021)
      
    option_player = st.selectbox(
     'Please choose a player...',
     team[(team['play.on_court.team.market'].isnull()) | (team['play.on_court.team.market'] == option_team)][['play.on_court.team.player1.full_name', \
     'play.on_court.team.player2.full_name','play.on_court.team.player3.full_name', 'play.on_court.team.player4.full_name', \
     'play.on_court.team.player5.full_name']].melt().value.unique())
   
    individual_player_times = player_oncourt_season(team, option_team, option_player)
      
    individual_player_chart = alt.Chart(individual_player_times).mark_bar().encode(
                              x = 'from',
                              x2 = 'to',
                              y = alt.Y('label',sort=alt.EncodingSortField(field='meta.scheduled')))
    
    st.altair_chart(individual_player_chart)
