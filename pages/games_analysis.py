import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import requests

def app():
    
    df = pd.read_csv('src/test_games.csv')
    
    option = st.selectbox(
     'Please choose a game...',
     df['label'].unique())
    
    #preprocessing
    score = df[df['label'] == option]
    score = score[['play.home_points','play.away_points','play.clock.seconds_game','play.on_court.away.market','play.on_court.away.name',
       'play.on_court.home.market','play.on_court.home.name','meta.home.color','meta.away.color']]
    score.columns = ['home','away','time','home_market','home_name','away_market','away_name','home_color','away_color']
    score['time'] = abs(2400 - score['time'])
    score = score.fillna(method='ffill')
    
    score['score_diff'] = score['home'] - score['away']
    score['leading_team'] = np.where(score['score_diff'] > 0,'home','away')
    
    home_color = score['home_color'].iloc[0]
    away_color = score['away_color'].iloc[0] 
    
    lineups = df[df['label'] == option]

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
    sel = alt.selection_multi(on='mouseover', encodings = ['time'])
    colorbar = alt.Color('point_diff:Q',scale=alt.Scale(scheme='viridis'))
    opacity_cond = alt.condition(sel,alt.value(1),alt.value(.4))
    
    #more preprocessing
    all_times = pd.DataFrame(list(range(2401)),columns=['time'])
    score_id_all = all_times.merge(score_id,how='left').fillna(method='ffill')
    score_id_all = score_id_all.drop_duplicates()
    
    #score difference bar/line
    score_diff_line = alt.Chart(score_id_all).mark_bar(strokeWidth=3).encode(
        x=alt.X('time:Q',scale=alt.Scale(domainMax=2400,domainMin=0,clamp=True)),
        y='score_diff',
        color = alt.condition("datum.score_diff > 0", alt.value(home_color), alt.value(away_color))
    ).properties(width=650,height=65)

    #score line plot
    band = alt.Chart(score_id).mark_area(opacity=.5).encode(
        x='time',
        y='home',
        y2='away',
        color = alt.value('lightblue')
    ).properties(width=650)

    home_line = alt.Chart(score_id).mark_line(strokeWidth=4,color=alt.HexColor(h_color)).encode(
        x='time',
        y='home'
    ).properties(width=650)

    away_line = alt.Chart(score_id).mark_line(strokeWidth=4,color=alt.HexColor(a_color)).encode(
        x='time',
        y='away'
    ).properties(width=650)
    
    #home bar chart
    h_bar = alt.Chart(h_change).mark_bar(size=40).encode(
        x = alt.X('from',axis=alt.Axis(title='')),
        x2 = 'to',
        color=colorbar,
        opacity=opacity_cond,
        tooltip=['lineup','point_diff_stint','point_diff','time_played']
    ).properties(height=50,width=650).add_selection(sel)
    
    #away bar chart
    a_bar = alt.Chart(a_change).mark_bar(size=40).encode(
        x = alt.X('from',axis=alt.Axis(title='Minutes into Game')),
        x2 = 'to',
        color=colorbar,
        opacity=opacity_cond,
        tooltip=['lineup','point_diff_stint','point_diff','time_played']
    ).properties(height=50,width=650).add_selection(sel)
    
    final_chart = alt.vconcat((band+home_line+away_line),(h_bar&score_diff_line&a_bar)).configure_axis(gridOpacity=.5).configure_view(strokeWidth=0)
    st.dataframe(score_id)
    st.dataframe(a_change)
    st.altair_chart(final_chart)
