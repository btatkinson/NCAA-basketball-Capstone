import os
import streamlit as st

# Custom imports 
from multipage import MultiPage
from pages import about, network_analysis, player_performance_prediction, clustering # import your pages here

# Create an instance of the app 
app = MultiPage()

# Title of the main page
#display = Image.open('Logo.png')
#display = np.array(display)
# st.image(display, width = 400)
# st.title("Data Storyteller Application")
#col1, col2 = st.beta_columns(2)
#col1.image(display, width = 400)
#col2.title("Data Storyteller Application")

# Add all your application here
app.add_page("About", about.app)
#app.add_page("Play-by-Play + Substitution", games_analysis.app)
app.add_page("Network Analysis", network_analysis.app)
app.add_page("Player Performance Prediction", player_performance_prediction.app)
app.add_page("Clustering", clustering.app)

# The main app
app.run()
