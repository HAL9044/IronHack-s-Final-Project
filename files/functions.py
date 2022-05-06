import requests
import urllib.parse
import streamlit as st
import geopy.distance
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def README():
    markdown = Path("./streamlitreadme.md").read_text()
    st.markdown(markdown, unsafe_allow_html=True)

def house_gps_finder(address): #finds and return gps coord of property
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
    response = requests.get(url).json()
    lat = response[0]["lat"]
    lon = response[0]["lon"]
    return float(lat), float(lon)

### Creates squared area around selected property given a threshold ###
def cluster_area (lat, lon, threshold):
    lat1 = lat + threshold
    lat2 = lat - threshold
    lon1 = lon + threshold
    lon2 = lon - threshold
    return float(lat1), float(lat2), float(lon1), float(lon2)

### Chops main dataframe based on the area created in cluster_area function ###
def dataframe_chopper (dframe, lat1, lat2, lon1, lon2):
    cut = dframe.loc[dframe['Latitude'] < lat1]
    cut = cut.loc[cut['Latitude'] > lat2]
    cut = cut.loc[cut['Longitude'] < lon1]
    cut = cut.loc[cut['Longitude'] > lon2]
    cut.rename(columns = {'Longitude':'longitude', 'Latitude':'latitude'}, inplace = True)
    return cut

### Calculates distance from all surrounding properties
def distance_calculator(dframe, lat, lon):
    lats = list(dframe.latitude)
    lons = list(dframe.longitude)
    final_distances = []
    coord1 = (lat[0], lon[0])
    for i in range(len(lats)):
        coord2 = (lats[i], lons[i])
        final_distances.append(geopy.distance.geodesic(coord1, coord2).km)
    dframe['Distance'] = final_distances
    return dframe

### Chop datafram according to radius
def radius_chop (dframe, radius):
    dframe = dframe.loc[dframe['Distance'] < radius]
    return dframe

### Pretty house :D
def pretty_house():
    return """ 
            `'::.
    _________H ,%%&%,
   /\     _   \%&&%%&%
  /  \___/^\___\%&%%&&
  |  | []   [] |%\Y&%'
  |  |   .-.   | ||  
~~@._|@@_|||_@@|~||~~~~~~~~~~~~~
     `""""""` """

### Encode categorical variables for ML model
def data_encoder(dframe, cluster):
    if cluster is not None:
        prov = pd.get_dummies(dframe.Province, prefix="prov")
        typ = pd.get_dummies(dframe.Type, prefix="typ")
        #clusters = pd.get_dummies(dframe.cluster, prefix= "cluster")
        autcom = pd.get_dummies(dframe['Autonomous Community'], prefix= "ac")
        encoded = pd.concat([dframe.Bathrooms, dframe.Rooms, dframe.Surface, typ, 
        prov, dframe.Latitude, dframe.Longitude, dframe.Pools, dframe['Air Conditioner'], 
        dframe.Terrace, autcom, dframe.cluster], axis=1)
        return encoded
    else:
        prov = pd.get_dummies(dframe.Province, prefix="prov")
        typ = pd.get_dummies(dframe.Type, prefix="typ")
        autcom = pd.get_dummies(dframe['Autonomous Community'], prefix= "ac")
        encoded = pd.concat([dframe.Bathrooms, dframe.Rooms, dframe.Surface, typ, 
        prov, dframe.Latitude, dframe.Longitude, dframe.Pools, dframe['Air Conditioner'], 
        dframe.Terrace, autcom], axis=1)
        return encoded
        
### It predicts
def predictor(X, y, prediction_row_encoded, prediction_index):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipe=Pipeline([("scalar",StandardScaler()),
         ("rf_classifier", XGBRegressor())])
    pipe.fit(X_train, y_train)
    X = X.append(prediction_row_encoded, ignore_index=True)
    prediction = pipe.predict(X)[prediction_index]
    return prediction

def missing_values(data):
    fig = plt.figure(figsize=(15,15))
    plt.imshow(data.isna(), aspect="auto", interpolation="nearest", cmap="gray")
    plt.xlabel("Column")
    plt.ylabel("Index")
    st.pyplot(fig)
    st.write((list(data.columns)))

#cuts dataframe according to selection
def scissors (price, surface, pricem2, rooms, bathrooms, data):
    data = data.loc[data.Price <= price[1]*10**3]
    data = data.loc[data.Price >= price[0]*10**3]
    data = data.loc[data.Surface >= surface[0]] 
    data = data.loc[data.Surface <= surface[1]] 
    data = data.loc[data['Price/m2'] <= pricem2[1]] 
    data = data.loc[data['Price/m2'] >= pricem2[0]] 
    data = data.loc[data.Rooms >= rooms[0]] 
    data = data.loc[data.Rooms <= rooms[1]] 
    data = data.loc[data.Bathrooms <= bathrooms[1]] 
    data = data.loc[data.Bathrooms >= bathrooms[0]]
    return data

#saves images in images folder
def image_save(figs):
    st.subheader("Save images")
    name = st.text_input("Prefix")
    save = st.button("Save")
    if save:
        count = 0
        for fig in figs:
            fig.savefig("../img_exports/" + name + str(count))
            count += 1
