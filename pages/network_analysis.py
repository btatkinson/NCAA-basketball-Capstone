import streamlit as st
import pandas as pd

def app():
  
  ########## LANDING PAGE CODE ##########
  st.title('Landing Page Title Goes Here')
  st.markdown('This is where I envision the required blog post will go (perhaps extended throughout the subheader sections).')
  
  ########## PLAY-BY-PLAY + SUBSTITUTION SECTION CODE ##########
  st.header('Play-by-Play + Substitution')
  
  st.markdown('Insert brief description about page')
  
  st.subheader('Preliminary Data Sample')
  df = pd.read_csv('src/test_games.csv', nrows = 1000)
  df.drop(columns = ['Unnamed: 0'], inplace = True)
  st.dataframe(df)
  
  ########## NETWORK ANALYSIS SECTION CODE ##########
  st.header('Network Analysis')
  st.markdown('Insert brief description about page')
  
  ########## PLAYER PERFORMANCE PREDICTION SECTION CODE ##########
  st.header('Player Performance Prediction')
  st.markdown('Insert brief description about page')
  
  ########## CLUSTERING SECTION CODE ##########
  st.header('Clustering')
  st.markdown('Insert brief description about page')
  
  ########## STATEMENT OF WORK SECTION CODE ##########
  st.header('Statement of Work')
  st.markdown('Blake statement of work.')
  st.markdown('Max statement of work.')
  st.markdown('Zachary statement of work.')
  st.markdown('Matthew statement of work.')
  
  ########## REFERENCES SECTION CODE ##########
  st.header('References?')
  st.markdown('List references here')
