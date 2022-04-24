import os
import streamlit as st

# Custom imports 
from multipage import MultiPage
from pages import about, games_analysis, network_analysis, player_performance_prediction# import your pages here

# Create an instance of the app 
app = MultiPage()

# Add all your application here
app.add_page("About", about.app)
app.add_page("Play-by-Play + Substitution", games_analysis.app)
app.add_page("Network Analysis", network_analysis.app)
app.add_page("Player Performance Prediction", player_performance_prediction.app)

# The main app
app.run()
