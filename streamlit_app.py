import streamlit as st
import pandas as pd
import numpy as np
import requests

# Create a page dropdown 
page = st.sidebar.selectbox("Choose your page", ["Page 1", "Page 2", "Page 3"]) 

if page == "Page 1":
    # Display details of page 1

    st.title('Uber pickups in NYC')

    DATE_COLUMN = 'date/time'
    DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

    @st.cache
    def load_data(nrows):
        data = pd.read_csv(DATA_URL, nrows=nrows)
        lowercase = lambda x: str(x).lower()
        data.rename(lowercase, axis='columns', inplace=True)
        data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
        return data

    data_load_state = st.text('Loading data...')
    data = load_data(10000)
    data_load_state.text("Done! (using st.cache)")

    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(data)

    st.subheader('Number of pickups by hour')
    hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
    st.bar_chart(hist_values)

    # Some number in the range 0-23
    hour_to_filter = st.slider('hour', 0, 23, 17)
    filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

    st.subheader('Map of all pickups at %s:00' % hour_to_filter)
    st.map(filtered_data)

elif page == "Page 2":

    #url = 'https://drive.google.com/file/d/1-9IdrqHE420_xqg7ngPW1Gd-S9WAMyAk/view?usp=sharing'
    #path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
    r = requests.get('https://drive.google.com/file/d/1-9IdrqHE420_xqg7ngPW1Gd-S9WAMyAk')
    df = pd.read_csv(r.content)
    st.write(df)
