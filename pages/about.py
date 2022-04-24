import streamlit as st
import pandas as pd

def app():
  
  ########## LANDING PAGE CODE ##########
  st.title('SIADS 697/698 Capstone Project')
  st.header('About')
  st.subheader('Team Members')
  st.markdown('''* Blake Atkinson (btatkins@umich.edu)
  * Max Cohen (maxwc@umich.edu)
  * Zachary Kramer (zakramer@umich.edu)
  *Matthew Zimolzak (zimolzak@umich.edu)''')
  
  
  
  ########## STATEMENT OF WORK SECTION CODE ##########
  st.header('Statement of Work')
  st.markdown('Blake statement of work.')
  st.markdown('Max statement of work.')
  st.markdown('Zachary statement of work.')
  st.markdown('Matthew statement of work.')
  
  ########## REFERENCES SECTION CODE ##########
  st.header('References')
  st.markdown('''App Layout
  * **Medium Blog Post:** https://towardsdatascience.com/creating-multipage-applications-using-streamlit-efficiently-b58a58134030
  * **GitHub Repository:** https://github.com/prakharrathi25/data-storyteller.
  ''')
