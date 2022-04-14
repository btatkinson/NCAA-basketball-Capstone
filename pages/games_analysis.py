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
    
    score = df[df['label'] == option]
    score = score[['play.home_points','play.away_points','play.clock.seconds_game','play.on_court.away.market','play.on_court.away.name',
       'play.on_court.home.market','play.on_court.home.name','meta.home.color','meta.away.color']]
    score.columns = ['home','away','time','home_market','home_name','away_market','away_name','home_color','away_color']
    score['time'] = abs(2400 - score['time'])
    score = score.fillna(method='ffill')
    
    home_color = score['home_color'].iloc[0]
    away_color = score['away_color'].iloc[0]
    
    band = alt.Chart(score).mark_area(opacity=.4,color='gray').encode(
        x='time',
        y='home',
        y2='away'
    ).properties(width=500)

    home_line = alt.Chart(score).mark_line(strokeWidth=3,color=alt.HexColor(home_color)).encode(
        x='time',
        y='home',
    ).properties(width=500)

    away_line = alt.Chart(score).mark_line(strokeWidth=3,color=alt.HexColor(away_color)).encode(
        x='time',
        y='away',
    ).properties(width=500)

    st.altair_chart(band+home_line+away_line)
