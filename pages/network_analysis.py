
import pickle
import requests

import numpy as np
import pandas as pd
import networkx as nx
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

plt.style.use('ggplot')

def app():
    st.title('Team and Player Performance Evaluation Through Network Analysis')


    st.markdown("## Motivation")
    st.markdown("""
    
    Our primary motivation for applying network analysis to college basketball is that network data structures are able to cleanly express the pairwise nature a basketball
    game. For example, when one team plays another team, the result of that game should update the representation or state of both teams simultaneously. Winning a game, for example, 
    is always at the expense of another team. This has been tried in a few 
    places before in different ways. An excellent exploration of these networks won a [Kaggle analytics competition in 2020](https://www.kaggle.com/code/artvolgin/network-approach-to-basketball-analytics/notebook).
    Although the ideas have been explored before, there hasn't been much work in sythesizing the methods or making them publicly available. 
    Viewing teams as nodes and games as edges allows some traditional network metrics to naturally have interpretable meaning.
    We will elaborate below on how PageRank, as an example, can easily be used to analyze certain qualities of a team. Another way to view basketball through the lens of networks 
    is to view the players as nodes and actions with the basketball as an edge. Passes to a teammate, turnovers to an opponent, or even shooting the basketball (to a 
    [special basket node](https://www.semanticscholar.org/paper/A-PageRank-Model-for-Player-Performance-Assessment-Brown/788cbf39871a297db0afcb240f2b83ae4b5e4170)) is also naturally a network. Centrality measures can then be used to determine how essential players are to their team's network. Unfortunately,
     the primary source of data for knowing what players are on the court together at the same time comes from the NCAA, and they do not allow scraping of their website. 
     Resultingly, we had to limit our analysis of player networks. 

    """)


    st.markdown("## Goal")
    st.markdown("""
    
    Our goal is to demonstrate the feasibility of using networks for college basketball analysis to either aid other methods or perhaps show a degree of superiority 
    in some respects. For some evaluations, we'll simply do sanity checks and compare with heavily referenced public sources. For others, there is easily accessible data
    on predictive performance and so we can compare in more rigorous ways. 

    """)
    st.markdown("### Weighted Undirected Networks")
    st.markdown("""
    
    Undirected networks are networks in which edges are symmetric. They find a natural application in basketball pace rankings. A team's "pace" in basketball is
    how many possessions per game they have. Teams are considered speedy if they run up and down the court creating a lot of possessions per game. The possessions between
    both teams are equal for each individual game however because the ball must go to the opposing team once a team's possession ends. Therefore the edge representing the amount of possessions
    in a graph should be undirected, as it has equivalent magnitude for both teams. Once the edges are weighed by the number of possessions between the teams, the Google PageRank algorithm automatically 
    highlights the high pace teams. PageRank can then be divided by degree (in other words, the number of games played) to create a final ranking. For more interpretable numbers,
    we multiply the PageRank by a constant to avoid working on extremely small scales. Below, we compare our PageRank pace rankings to a popular website (KenPom.com) that uses a completely different
    calculation for pace. Our rankings and KenPom have a 0.96 spearman correlation in 2022 despite using completely different methods.

    """)

    conf_options = ['A10','AAC','ACC','ASUN','American East','Big 10','Big 12','Big East','Big Sky','Big South','Big West','CAA','Conference USA','Horizon','Ivy League','MAAC',
 'MAC','MEAC','MVC','MWC','Northeast','OVC','PAC-12','Patriot League','SEC','SWAC','Southern','Southland','Summit League','Sun Belt','WAC','WCC']
    
    selected_conference = st.selectbox("Select Conference", conf_options, index=0)

    def draw_pace_subgraph(pace_df, conf):
        
        # pace_series
        subteams = pace_df.copy().loc[pace_df['conference_name']==conf].reset_index(drop=True)
        prnk = pace_df.copy().set_index('team_id').to_dict()['pace_rating']
        subnodes = list(subteams['team_id'].unique())

        sub_g = pace_network.subgraph([str(sn) for sn in subnodes])

        fig, axes= plt.subplots(2,1, figsize=(14, 18))
        ax1 = axes[0]
        sub_wedges = sub_g.edges(data="weight")
        sub_edges = sub_g.edges()
        sub_nodes = sub_g.nodes()

        pos = nx.circular_layout(sub_g)
        weights = [e * 5 for u,v,e in sub_wedges]
        colors = [team_dark[int(n)] for n in sub_nodes]
        # fig, ax = plt.subplots(figsize=(22,16))
        nx.draw(sub_g, edge_color=weights, pos=pos, labels={n:teams_id2name[int(n)] for n in sub_nodes}, 
                node_color=[prnk[int(n)] for n in sub_nodes], node_size=[7e2*prnk[int(n)] for n in sub_nodes], font_size=10, font_color="black",
            cmap=plt.cm.bwr, edge_cmap=plt.cm.bwr, ax=ax1)

        ax2=axes[1]
        ax2.set_title("Pace Network vs. KenPom \nPace Ratings",fontsize=24)
        ax2.set_xlabel("Pace Network\nPageRank", fontsize=16)
        ax2.set_ylabel("KenPom Adjusted\n Tempo", fontsize=16)
        ax2.scatter(subteams.pace_rating, subteams.Tempo, c=[prnk[int(n)] for n in subteams.team_id.values],
                cmap=plt.cm.bwr, s=350)
        n = subteams.team_name
        for i, txt in enumerate(n):
            ax2.annotate(txt, (subteams.pace_rating[i]+0.03, subteams.Tempo[i]))

        st.pyplot(fig=fig)
        
        return

    def complementaryColor(my_hex):
        if my_hex[0] == '#':
            my_hex = my_hex[1:]
        rgb = (my_hex[0:2], my_hex[2:4], my_hex[4:6])
        comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
        return ''.join(comp)

    def determine_darker_color(c1, c2):
        r, g, b = c1
        r2, g2, b2 = c2
        hsp1 = 0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b)
        hsp2 = 0.299 * (r2 * r2) + 0.587 * (g2 * g2) + 0.114 * (b2 * b2)
        
        if hsp1 > hsp2:
            # darker is hsp2
            return 0
        elif hsp1 < hsp2:
            return 1
        else:
            print(hsp1, hsp2)
            raise ValueError() # same color


        
    @st.cache
    def load_colors():
        
        team_meta = pd.read_csv('./src/network_viz_data/team_meta.csv')
        teams_id2conf = team_meta.copy().drop_duplicates(subset=['ESPN_team_id'])[['ESPN_team_id','conference_name']].set_index('ESPN_team_id').to_dict()['conference_name']

        # fill nas with complementary
        # don't want these being the same
        team_meta['secondary_color'] = np.where(team_meta['primary_color']==team_meta['secondary_color'], np.nan, team_meta['secondary_color'].copy())
        # one special case
        team_meta.loc[team_meta['ESPN_team_id']==57, 'secondary_color'] = 'FA4616'
        team_meta['rgb_primary'] = team_meta['primary_color'].apply(lambda x: to_rgb('#'+x))
        team_meta['secondary_color'] = team_meta['secondary_color'].fillna(team_meta['primary_color'].apply(lambda x: complementaryColor(x)))
        team_meta['rgb_secondary'] = team_meta['secondary_color'].apply(lambda x: to_rgb('#'+str(x)))
        team_meta['primary_darker'] = team_meta.apply(lambda x: determine_darker_color(x.rgb_primary, x.rgb_secondary), axis=1)

        team_meta['darker_color'] = np.where(team_meta['primary_darker']==1, team_meta['primary_color'].copy(), team_meta['secondary_color'].copy())
        team_meta['lighter_color'] = np.where(team_meta['primary_darker']==0, team_meta['primary_color'].copy(), team_meta['secondary_color'].copy())
        team_meta['darker_color'] = '#' + team_meta['darker_color'].copy()
        team_meta['lighter_color'] = '#' + team_meta['lighter_color'].copy()

        team_dark = team_meta.copy()[['ESPN_team_id','darker_color']].set_index('ESPN_team_id').to_dict()['darker_color']
        team_light = team_meta.copy()[['ESPN_team_id','lighter_color']].set_index('ESPN_team_id').to_dict()['lighter_color']

        return team_dark, team_light
    

    @st.cache
    def load_pace_data():
        network = nx.read_gml('./src/network_viz_data/pace_graph.gml')
        pace_df = pd.read_csv('./src/network_viz_data/pace_df.csv')
        return network, pace_df

    def save_dict(di_, filename_):
        with open(filename_, 'wb') as f:
            pickle.dump(di_, f)

    def load_dict(filename_):
        with open(filename_, 'rb') as f:
            ret_di = pickle.load(f)
        return ret_di

    teams_id2name = load_dict('./src/network_viz_data/teams_id2name')
    
    pace_network,pace_series = load_pace_data()
    team_dark, team_light = load_colors()

    draw_pace_subgraph(pace_series, selected_conference)
    st.markdown("""
    
    You can read more about how KenPom adjusted pace ratings are calculated [here](https://kenpom.com/blog/national-efficiency/) and on his blog. Our goal was
    to simply show the feasibilty of using networks, which we've done here by showing extreme correlation with a heavily referenced and trusted public
    source. It is unclear which system is more useful in prediction or if they can be used
    in conjuction for better ratings than either individually. In future work we could compare stability and the predictive qualities
    of each of the ratings systems. It should be noted KenPom has a temporal element to his ratings, which we do not include here.

    """)

    st.markdown("### Weighted Directed Networks")
    st.markdown("""
    
    Unlike pace, for most basketball stats, there are winners and losers. Rebounds, for example, are directly at the expense of the other team. Similarly, when teams play, there can only
    be one winner and one loser for every game. In order to 
    represent these sort of stats, directed networks work best. If an edge is created from the loser to the winner, PageRank will highlight the best teams and players. The edges can be weighed by
    margin. Again, standardizing by degree effectively turns PageRank into a per game statistic (although more special care is needed with players, since there are
    not always the same amount of opponents). Below, you can see how the nation's leading rebounder, Oscar Tshiebwe, stands out against the other leading rebounders of his conference.
    The size of the node below is scaled by pagerank, while darker edges imply more rebounding difference when the players played against each other.  

    """)

    st.image("./src/network_viz_data/rebounding_pagerank.png")

    st.markdown("""

    There are a few outstanding issues we will discuss below, but at this stage we couldn't resist calculating the pagerank for players of all primary box score statistics 
    for all of our seasons of data and comparing them. Sorting by points, rebounds, and assists all gave reasonable names at the top. To confirm our intuition,
    we took two principal components via PCA. We had no hand in steering the results other than inputing standard boxscore statistics, yet the PCA results were very intuitive.
    Players that ranked highly in principal component one are impressive players. To demonstrate this visually, we highlighted players that won various player of the
    year awards below in green. Players that rank highly in principal component 2 are more center-like, while low principal component 2 implies a point guard role. 
    Our ESPN data had broad position information, which we used to color the scatterplot. Pink implies guards, blue implies forwards, and yellow/green are centers. A PCA biplot
    confirms that guards are correlated with stats like assists while centers are more correlated with blocks and rebounds. 

    
    """)

    st.image("./src/network_viz_data/player_principal_components.png")


    st.markdown("### Improving the Concept")

    st.markdown("""
    
    We noticed some shortcomings as we were experimenting with our version of opposing player networks. One, when a directed tie is created between opponents,
    factors other than the opponents themselves can influence 
    
    
    """)



    ### too big of file size
    # def draw_player_reb(reb_graph, conf):
    
    #     teams = conf_teams[conf]
    #     teams = [t for t in teams if t in teams_id2name.keys()]
    #     players = []
    #     for team in teams:
    #         players.extend(team_players[team])

    #     num_to_plot = 15
    #     players = [p for p in players if p in prnk]
    #     player_pagerank = [(pid, prnk[pid]) for pid in players]
    #     player_pagerank = sorted(player_pagerank, key=lambda x: x[1], reverse=True)
    #     top_n = [p[0] for p in player_pagerank[:num_to_plot]]
        
    #     sub_g = reb_graph.subgraph([str(p) for p in top_n])

    #     # total labelled
    #     sub_nodes = sub_g.nodes()
    #     edges = sub_g.edges()
    #     pos = nx.circular_layout(sub_g)
    #     weights = [g[u][v]['weight'] * 10 for u,v in edges]
    #     edge_colors = [team_dark[teams_name2id[players_id2team[int(e[1])]]] for e in sub_g.edges()] # color edges by receiver
    #     colors = [prnk[int(n)] for n in sub_nodes]
    #     labeldict = {p:players_id2name[int(p)] for p in sub_nodes}

    #     fig, ax = plt.subplots(figsize=(20,10))
    #     nx.draw(sub_g, width=weights, pos=pos, node_color=colors, edge_color=edge_colors, node_size=[1e7*prnk[int(n)] for n in sub_nodes],cmap='RdBu_r')
    #     for j in sub_nodes:
    #         nx.draw_networkx_labels(sub_g.subgraph([j]), pos={j:pos[j]} , labels={j:labeldict[j]}, font_color='white', font_size=12,
    #                             )
    #     st.pyplot(fig=fig)
    #     return


    # conf_teams = load_dict('./src/network_viz_data/conf_teams')
    # team_players = load_dict('./src/network_viz_data/team_players')
    # players_id2team = load_dict('./src/network_viz_data/players_id2team')
    # players_id2name = load_dict('./src/network_viz_data/players_id2name')
    # teams_name2id = load_dict('./src/network_viz_data/teams_name2id')
    # reb_g = nx.read_gml('./src/network_viz_data/reb_graph.gml')

    # reb_selected_conference = st.selectbox("Select Conference For Rebounding Comparison", conf_options, index=0)

    # prnk = nx.pagerank(reb_g, alpha=1)
    # draw_player_reb(reb_g, reb_selected_conference)

    # 
    # st.markdown('### Review of Other Methods')
    # st.markdown("""
    # Before we get into what motivates network analysis, it is important to do a quick survey of other common methods. There are numerous methods that exist for 
    # analyzing both past performance and predicting future team and player performance. The most widely referenced team rankings are the [AP Poll](https://apnews.com/hub/ap-top-25-college-basketball-poll), 
    # which survey mostly media members, and the coaches poll, which surveys head coaches. These seek to use the wisdom of the crowd in order to rank teams. The NCAA itself uses 
    # [NET rankings](https://www.ncaa.com/news/basketball-men/article/2021-12-06/college-basketballs-net-rankings-explained). These are intended to measure a team's resume over the course of a season in order to influence whether or not they are eligible for the postseason.
    # As they weigh the first game the same as the last, they make the conscious choice to be less predictive, as it is a intended to gauge the entire season as a
    # whole. NET rankings are comprised of two main components. One is efficiency per possession, and the other is a win/loss results based metric. There are a couple 
    # of issues that stand out. One, standardizing by possession can benefit certain playstyles over others. For example, If Team A has +0.1 points per possession and averages
    # 60 possessions per game, then Team B averages +0.09 points per possession and 80 possessions per game, we would expect Team A to beat an average oppponent by 
    # +6 points, and Team B to beat an average opponent by +7.2 points (assuming they play their average number of possessions). However, NET would rank team A higher. 
    # The NCAA NET rankings also arbitrarily divide opposing team strength into quadrants. It is unclear why they chose quadrants over fifths or thirds, and this becomes 
    # most problematic when a loss to a team ranked 75th is treated entirely different to a team ranked 76th.  
    # """
    #st.image("spearman_correlation.png")
    # """
    # There are many published predictions that improve upon the NCAA model. [EvanMiya.com](https://evanmiya.com/), for example, uses Bayesian updating to create player ranks from boxscore stats.
    # He then uses lineup +/- information to improve upon those estimates. [Kenpom.com](https://kenpom.com/) is probably the most well-known website, and he adjusts teams for both strength of 
    # schedule and pace before calculating efficiency margin. Notably, he does not rely on regression to create his predictions. Most of these methods have some degree of 
    # opaqueness, but fortunately we can piece together parts of their processes. [thepredictiontracker.com](https://www.thepredictiontracker.com/bbresults.php) records the error of a few of these methods, and the errors
    # found there agree well with Kenpom. Surveying popular public websites, we could not find explicit references to network approaches.

    # We are not the first however to consider network approaches.  Artem Volgin and Ekaterina Melinova won a Kaggle analytics competition by a [network approach to basketball
    # analytics](https://www.kaggle.com/code/artvolgin/network-approach-to-basketball-analytics/notebook). They measured centralization for both lineups and conferences. For lineups, 
    # their measures were able to highlight players that were essential to their team. For conferences, they were able to measure competitiveness. Interestingly,
    # they also were able to find features that correlated with winning via Exponential Random Graph Modelling. The image below is from their work.  
    
    # """
    # #st.image("conference_centrality.png")
    # """
    # Lastly, 
    
    
    # """)



    # DATE_COLUMN = 'date/time'
    # DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
    #         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')
    
    # @st.cache
    # def load_data(nrows):
    #     data = pd.read_csv(DATA_URL, nrows=nrows)
    #     lowercase = lambda x: str(x).lower()
    #     data.rename(lowercase, axis='columns', inplace=True)
    #     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    #     return data

    # data_load_state = st.text('Loading data...')
    # data = load_data(10000)
    # data_load_state.text("Done! (using st.cache)")

    # if st.checkbox('Show raw data'):
    #     st.subheader('Raw data')
    #     st.write(data)

    # st.subheader('Number of pickups by hour')
    # hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
    # st.bar_chart(hist_values)

    # # Some number in the range 0-23
    # hour_to_filter = st.slider('hour', 0, 23, 17)
    # filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

    # st.subheader('Map of all pickups at %s:00' % hour_to_filter)
    # st.map(filtered_data)
# import streamlit as st
# import pandas as pd

# def app():
  
#   ########## LANDING PAGE CODE ##########
#   st.title('Landing Page Title Goes Here')
#   st.markdown('This is where I envision the required blog post will go (perhaps extended throughout the subheader sections).')
  
#   ########## PLAY-BY-PLAY + SUBSTITUTION SECTION CODE ##########
#   st.header('Play-by-Play + Substitution')
  
#   st.markdown('Insert brief description about page')
  
#   st.subheader('Preliminary Data Sample')
#   df = pd.read_csv('src/test_games.csv', nrows = 1000)
#   df.drop(columns = ['Unnamed: 0'], inplace = True)
#   st.dataframe(df)
  
#   ########## NETWORK ANALYSIS SECTION CODE ##########
#   st.header('Network Analysis')
#   st.markdown('Insert brief description about page')
  
#   ########## PLAYER PERFORMANCE PREDICTION SECTION CODE ##########
#   st.header('Player Performance Prediction')
#   st.markdown('Insert brief description about page')
  
#   ########## CLUSTERING SECTION CODE ##########
#   st.header('Clustering')
#   st.markdown('Insert brief description about page')
  
#   ########## STATEMENT OF WORK SECTION CODE ##########
#   st.header('Statement of Work')
#   st.markdown('Blake statement of work.')
#   st.markdown('Max statement of work.')
#   st.markdown('Zachary statement of work.')
#   st.markdown('Matthew statement of work.')
  
#   ########## REFERENCES SECTION CODE ##########
#   st.header('References?')
#   st.markdown('List references here')
