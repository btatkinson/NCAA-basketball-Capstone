# NCAA-basketball-Capstone

Link to app:
https://share.streamlit.io/btatkinson/ncaa-basketball-capstone/main

This repo is for our Masters of Applied Data Science 2022 Capstone project. We decided to investigate various ways to explore and analyze college basketball data. The repo overall can be divided into three main parts.

### 1. Play by Play and Substitution

On court lineup data is difficult to come by, but we were able to download and extract play-by-play data that includes lineup data from the SportsRadar API. We created visualizations that highlight when a lineup is on the court and playing particularly well. Additionally, we’ve created unique plots that will show a player’s playing time patterns throughout a season. 

Relevant code:  
    - pages/games_analysis.py: app page  

### 2. Network Analysis

We were able to use network techniques and properties in a college basketball setting to create intuitive metrics. The concepts of PageRank and betweenness can go a long way in valuing players. We found uses for both directed networks and undirected networks. We were able to add a temporal component to our PageRank calculations which would help downstream prediction tasks. Lastly, we calculate the entropy of our networks over time which could be used in various ways, e.g, helping quantifying uncertainty.  

Relevant code:  
    - pages/network_analysis.py: app page  
    - notebooks/blake_exploratory/player_pagerank: focuses on quantifying player skills through pagerank  
    - notebooks/visualizations/streamlit_network_page: creates pace undirected network  
    - notebooks/visualizations/streamlit_historical_players: player pagerank visualization, temporal network viz  

### 3. Player Prediction

We sought to predict player points on a game-by-game level. The model scores very well overall, with a Mean Absolute Error (MAE) of 3.78 for all players in our sample. This model allows for a general understanding of the mechanism behind player performance, including opponent impacts, but could be used by players, coaches, scouting, and for betting purposes.  

Relevant code:  
    - notebooks/models/Game_log_points_model: primary model code  
    - Data Cleaning and Feature Engineering: prep work for model  
    - pages/player_performance_prediction.py: visualizes model  





