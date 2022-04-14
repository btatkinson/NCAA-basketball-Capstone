import streamlit as st
import numpy as np
import pandas as pd
import requests

def app():
    df = pd.read_csv('src/test_games.csv')
    
    option = st.selectbox(
     'Please choose a game...',
     df['label'].unique())
