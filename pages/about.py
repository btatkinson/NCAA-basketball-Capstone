import streamlit as st
import pandas as pd

def app():
  
  ########## LANDING PAGE CODE ##########
  st.title('SIADS 697/698 Capstone Project')
  st.header('About')
  st.subheader('Team Members')
  st.markdown('''
  * Blake Atkinson (btatkins@umich.edu)
  * Max Cohen (maxwc@umich.edu)
  * Zachary Kramer (zakramer@umich.edu)
  * Matthew Zimolzak (zimolzak@umich.edu)''')
  
  st.subheader('Play-by-Play + Substitution')
  st.markdown('''
  Using on-court player data, we’ve created a new way to visualize and understand how team’s succeed and fail during a given game based on the lineups
  that are on the court. Our lineup visualization could be used in game box dashboards scores to attribute team success or failure to given lineups 
  throughout a game. Additionally, we’ve created unique plots that will show a player’s playing time patterns throughout a season.''')
  
  st.subheader('Network Analysis')
  st.markdown('''
  Applying network analysis to college basketball is a relatively new concept and our team has expanded on initial explorations, setting a strong 
  framework for future network analyses on other sports. We’ve used weighted undirected networks to analyze and examine team pace, with equivalent 
  performance to current industry-leading rankings like KenPom. We’ve also applied weighted directed networks to individual player performance, using 
  on-court adversarial interactions to effectively rank player performance against each opponent.''')
  
  st.subheader('Player Performance Prediction')
  st.markdown('''
  Our player performance model seeks to create a predictive mechanism for player points. The model scores very well overall, with a Mean Absolute Error
  (MAE) of 3.78 for all players in our sample. This model allows for a general understanding of the mechanism behind player performance, including 
  opponent impacts, but could be used by players, coaches, scouting, and for betting purposes.''')
  
  st.markdown('''
  Check out our GitHub repository for more: [NCAA Basketball Capstone](https://github.com/btatkinson/NCAA-basketball-Capstone)''')
  
  ########## STATEMENT OF WORK SECTION CODE ##########
  st.header('Statement of Work')
  st.markdown('''
  All 4 group members worked on gathering data through website scraping and API connections as well as general exploratory data analysis, data cleaning,
  and visualization. Matthew Zimolzak worked to implement our streamlit connection and designed much of the front-end user experience. Zachary Kramer
  spearheaded the work on the player points model. Blake Atkinson owned the network analysis from end-to-end. Max Cohen executed the Play-by-play and
  lineup analysis.''')
  
  ########## REFERENCES SECTION CODE ##########
  st.header('References')
  st.markdown('''App Layout
  * **Medium Blog Post:** https://towardsdatascience.com/creating-multipage-applications-using-streamlit-efficiently-b58a58134030
  * **GitHub Repository:** https://github.com/prakharrathi25/data-storyteller.
  ''')
