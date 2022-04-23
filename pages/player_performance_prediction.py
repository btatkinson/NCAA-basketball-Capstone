import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error,make_scorer

st.title('NCAA Player Points Prediction Model')
st.markdown("""
This app predicts how many points a player will score each game on a sample of teams due to file size limits.
* **Main Features:** Player Cumulative Average, Player Rolling Averages, Opponent Points Allowed to Role and Position. 
* **Model Used:** Linear Regression Model
* **Python libraries:** pandas, streamlit, numpy, altair, sklearn
* **Data source:** [sportsdataverse-py](https://sportsdataverse-py.sportsdataverse.org/).
""")

sample_df_box_score_and_features= pd.read_csv("src/sample_player_and_opp_stats_with_position.csv",index_col=0)

### Using 2022 as test year. Train on a sample of the other years  
training_df =  sample_df_box_score_and_features[sample_df_box_score_and_features["season"]<2022].sample(5000,random_state=698)
testing_df = sample_df_box_score_and_features[sample_df_box_score_and_features["season"]==2022]
### fill in colors for missing teams - Dark Grey 
testing_df["team_color"] = testing_df.loc[:,"team_color"].fillna(value='#555555')


#### Columns to use for model 
def transform_training_testing(dataframe):
    columns = ["prev_player_ppg","prev_player_points_per_min",	"game_number",
    "cum_average_opp_points_to_role","cum_average_opp_min_allowed_to_role",
    "prev_3_games_opp_min_allowed_to_role",
    "prev_3_games__opp_points_allowed_to_role",
    "prev_total_opp_ppg","Home","Starter_numeric",	
    "prev_avg_pts_to_role_pos","prev_avg_min_to_role_position",
    "Big_man","Guard",
    "pts"]

    points_df_model =dataframe.loc[:,columns] 
    points_df_model = points_df_model.rename(columns = {"prev_player_ppg":"prev_avg_player_ppg","prev_player_points_per_min":"prev_avg_player_points_per_min"})
    points_df_model = points_df_model.dropna()
    return points_df_model

training_df_processed = transform_training_testing(training_df)
testing_df_processed = transform_training_testing(testing_df)


def convert_to_training_testing(training_df_processed,testing_df_processed):
    X_train= training_df_processed.loc[:, ~training_df_processed.columns.isin(['pts'])]               
    y_train = training_df_processed["pts"]
    X_test= testing_df_processed.loc[:, ~testing_df_processed.columns.isin(['pts'])]               
    y_test = testing_df_processed["pts"]

    # X_train, X_test, y_train, y_test = train_test_split(X,y,random_state=0)
    X_train_scaled = MinMaxScaler().fit_transform(X_train)
    X_test_scaled= MinMaxScaler().fit_transform(X_test)
    return X_train,y_train,X_test,y_test,X_train_scaled,X_test_scaled
X_train,y_train,X_test,y_test,X_train_scaled,X_test_scaled = convert_to_training_testing(training_df_processed,testing_df_processed)

linear_reg = LinearRegression().fit(X_train_scaled,y_train)
y_pred = linear_reg.predict(X_test_scaled)
mae = mean_absolute_error(y_test, y_pred)

pts_predictions_df = y_test.to_frame().rename(columns={"pts":"pts_label"})
pts_predictions_df['points_prediction'] = y_pred
merged_predictions = pd.merge(pts_predictions_df,sample_df_box_score_and_features,left_index= True, right_index= True)

def display_prediction_graph(player_pred):#line= True, bars=True,head=True,logo= True):
  # player_pred = merged_predictions[merged_predictions.athlete_display_name == player]

  line = alt.Chart(player_pred).mark_line(strokeDash=[1,1],color= 'black').encode(
      x='game_date:T',
      y=alt.Y('points_prediction'),
      tooltip = ["game_date:T",'points_prediction','pts',"min","starter"]
      )
  bars = alt.Chart(player_pred).mark_bar().encode(
      x=alt.X('game_date:T', title = 'Game Date'),
      y=alt.Y('pts', title = "Points"),
      color = alt.Color('team_color', legend = None),
      tooltip = ["game_date:T",'points_prediction','pts',"min","starter"]
      )
  try:
    logo = alt.Chart(player_pred).mark_image().encode(
          x=alt.value(0), x2=alt.value(75),  # pixels from left
          y=alt.value(0), y2=alt.value(75),  # pixels from top
          url='team_logo',
          tooltip = "team_name"
        )
  except:
    return (line+bars)
  
  try:
    head_shot_image = alt.Chart(player_pred).mark_image().encode(
        x=alt.value(375), x2=alt.value(475),  # from left
        y=alt.value(0), y2=alt.value(75),  # from top
        url='athlete_headshot_href',
        tooltip = 'athlete_display_name'
        ).properties(
            width = 500,
            height  =500,
            title = "Points (Bars) and Predicted Points (Dashed line)"
        )
    return (line+bars+logo+head_shot_image)
  except:
    return (line+bars+logo)  

st.subheader("Team Dataframe")

option_team = st.selectbox(
    'Please choose a team...',
    list(merged_predictions.team_short_display_name.unique())
)
### Filter on team, player, 
team_predictions = merged_predictions[merged_predictions.team_short_display_name==option_team]
st.write(team_predictions) 
# player = "Ochai Agbaji"

st.subheader("Player Dataframe")
option_player = st.selectbox(
    'Please choose a player...',
    list(team_predictions.athlete_display_name.unique())
)

#### If statements when the images are null. 
player_pred = team_predictions[team_predictions.athlete_display_name == option_player]
st.write(player_pred)

st.subheader('Points Model Chart')
st.markdown('''The graph below illustrates a sample of the points model using 
                the dashed lines as predictions and bars for the number of points 
                a player scored each game. 
            .''')
rounded_mae = round(mae,2)
st.markdown('''Mean Absolute Error was used for both interpretability and 
                treating overestimates and underestimates the same.
                The metric used (on all the sampled players) provides us 
                an understanding of how many points on average our predicted points 
                differed from the actual points scored.
            ''')
st.markdown("Mean Absolute Error on sample: {}".format(rounded_mae))
st.altair_chart(display_prediction_graph(player_pred))

