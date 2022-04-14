import streamlit as st
import numpy as np
import pandas as pd
import requests

def app():
    option = st.selectbox(
     'Please choose a game...',
     ('Email', 'Home phone', 'Mobile phone'))
