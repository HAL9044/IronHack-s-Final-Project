from types import NoneType
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import functions as func
import eda

def info_input(data):
    ##########################################################################################
    ###Prediction value input 
    ##########################################################################################
    #Get unique values
    houseType = data.Type.unique()
    provs = data.Province.unique()
    autCom= data['Autonomous Community'].unique()
    #Make columns and generate selection boxes
    col1, col2, col3 = st.columns(3)
    type = col1.selectbox("House type", houseType[:len(houseType)-1])
    province = col2.selectbox("Province", provs)
    autcom = col3.selectbox("Autonomous Community", autCom)

    col4, col5, col6 = st.columns(3)
    rooms = col4.slider("Rooms", 0, data.Rooms.max())
    bathrooms = col5.slider("Bathrooms", data.Bathrooms.min(), data.Bathrooms.max())
    surface = col6.number_input('Surface (m2)')

    col7, col8, col9 = st.columns(3)
    terrace = col7.checkbox("Terrace")
    pool = col8.checkbox("Pool")
    ac = col9.checkbox("Air Conditioner")

    #Add prediction values to a list
    property_values = [type, province, autcom, rooms, bathrooms, surface, terrace, pool, ac]

    ##########################################################################################
    ###Address input           
    ##########################################################################################
    address = st.text_input("Address:")
    if address == "":
        return None, property_values
    else:
        try:
            lat, lon = func.house_gps_finder(address) ### get lat and lon of property ###
            st.write(lat, lon)
            coordinates = pd.DataFrame()    ### create dataframe in order to append values ###
            coordinates = coordinates.append({"lon": lon, "lat": lat}, ignore_index=True)
            st.map(coordinates)
            return coordinates, property_values ### return coordinates in order to use them in cluster_finder function (see Streamlit.py) ###
        except:
            st.write("No location found, please try again")
            return None, None
    
def cluster_finder(coordinates, data):
    ###THIS FUNCTION WILL SUGGEST PRICE CLUSTERS IN ORDER TO HELP ML MODEL
    st.header("Cluster finder")
    if type(coordinates) == int or type(coordinates) == NoneType:
        st.write("Input an address in order to start looking for clusters")
    else:
        ### Note that lat and lon will be used consistently as variables of the selected +
        ### + property, lat1, lat2, lon1, lon2, are used in order to chop the dataframe
        lat = coordinates.lat
        lon = coordinates.lon
        threshold = st.slider("Threshold", 1, 100, step=1, value = 40)
        threshold = threshold/1000
        lat1, lat2, lon1, lon2 = func.cluster_area(lat, lon, threshold) #OBTAIN COORDINATE LIMITS IN ORDER TO CHOP DATAFRAME
        cut = func.dataframe_chopper(data, lat1, lat2, lon1, lon2)      #CHOP DATAFRAME TO GET PROPERTIES WITHIN AREA
        st.map(cut)
        area_dframe = st.checkbox("See selected area dataframe")
        if area_dframe:
            st.dataframe(cut)

        ##########################################################################################
        ### Cluster generator
        ##########################################################################################
        clus_amount = st.slider("Price/m2 cluster amount", 0, 20, step=1, value=10)
        data['Price cluster'] = pd.qcut(data['Price/m2'], clus_amount, labels=False) #Create cluster column
        cut = func.dataframe_chopper(data, lat1, lat2, lon1, lon2)                   #Make cut dataframe again with added cluster column
        cut.reset_index()
        ##########################################################################################
        ### Circle area 
        ##########################################################################################
        ### Variable point_lat & point_lon will be used to calculate the properties that fall within the selected property radius
        radius = st.slider("Final radius (Km):", 0.1, 10.0, step=0.1, value=10.0)
        cut = func.distance_calculator(cut, lat, lon)   #Calculate distance between points
        cut = func.radius_chop(cut, radius)             #Delete rows that fall outside radius
        ##########################################################################################
        ### Plotting
        ##########################################################################################
        fig = plt.Figure(figsize=(15,15))
        ax = fig.add_subplot(111)
        scatter = ax.scatter(cut.longitude, cut.latitude, c=cut['Price cluster'])
        ax.scatter(lon, lat, c="red", s=400 ,label="Label2")
        ax.legend(*scatter.legend_elements(),loc="upper right", title="Price/m2 clusters (0<9)")
        st.pyplot(fig)

        col1, col2, col3 = st.columns(3)
        col1.metric("Properties count", len(cut))
        col2.metric("Avrg. Price", int(round(cut.Price.mean(), 0)))
        col3.metric("Avrg. Surface", round(cut.Surface.mean(), 2))

        col4, col5, col6 = st.columns(3)
        col4.metric("Avrg. Rooms", round(cut.Rooms.mean(), 2))
        col5.metric("Avrg. Bathrooms", round(cut.Bathrooms.mean(),2))
        col6.metric("Avrg. Price/m2", round(cut['Price/m2'].mean(),2))

        col1, col2, col3 = st.columns(3)
        col1.metric("Cluster mean", round(cut['Price cluster'].mean(), 2))
        col2.metric("Cluster median", cut['Price cluster'].median())
        col3.metric("Cluster mode", cut['Price cluster'].mode())
        numerics = eda.numerics_generator(cut)
        barchart = st.checkbox("Show cluster bar chart")
        if barchart:
            st.bar_chart(cut[['Price cluster', 'Price']].groupby("Price cluster").count())
        eda.plotter(cut, numerics)
        ##########################################################################################
        ### Final values selection and returning
        ##########################################################################################
        st.subheader("Select final cluster:")
        choice = st.radio("Pick final cluster value:", [round(cut['Price cluster'].mean(), 2),
                cut['Price cluster'].median(), cut['Price cluster'].mode()[0], "Input custom cluster", "Do not use cluster" ], index=4)
        if choice == "Input custom cluster":
            cluster = st.number_input("Input cluster", 0, cut['Price cluster'].max())
        elif choice == "Do not use cluster":
            cluster = None
            clus_amount = None
        else:
            cluster = choice
        return cluster, clus_amount

def prediction_data(property_values, cluster, coordinates): #Shows data for prediction and gets "actual price" input 
    st.subheader("Prediction info")
    col1, col2 = st.columns(2)
    col1.text("Property type: " + property_values[0]
    + "\nRooms: " + str(property_values[3]) + "\nBathrooms: " + str(property_values[4]) + 
    "\nSurface: " + str(property_values[5]) + "\nAutonomous Community: " + property_values[2]
    + "\nProvince: " + property_values[1] + "\nTerrace: " + str(property_values[6]) + "\nPool: " 
    + str(property_values[7]) + "\nAir Conditioner: " + str(property_values[8]) +
    "\nCluster: " + str(cluster) + "\nLatitude: " + str(coordinates.lat[0]) +
     "\nLongitude: " + str(coordinates.lon[0]))
    actual_price = st.number_input("I know the actual price: ", 0, 1000000, value=0)
    col2.text(func.pretty_house()) #shows pretty house :D
    return actual_price

def predict(data, coordinates, values, cluster, clus_amount, actual_price):
    ##########################################################################################
    # Preparing data from ML model
    ##########################################################################################
    st.subheader("Result")
    mldata = data[['Price', 'Bathrooms', 'Rooms', 
        'Surface', 'Pools', 'Air Conditioner', 'Type', 
        'Terrace', 'Autonomous Community', 'Province', 
        'Latitude', 'Longitude']]
    if clus_amount is not None:
        mldata['cluster'] = pd.qcut(data['Price/m2'], clus_amount, labels=False)

    prediction_data_dict = {'Bathrooms': values[4], 'Rooms': values[3],
        'Surface': values[5], 'Pools': int(values[7]), 'Air Conditioner': int(values[8]),
        'Type': values[0], 'Terrace': int(values[6]), 'Autonomous Community': values[2],
        'Province': values[1], 'Latitude': coordinates.lat[0], 'Longitude': coordinates.lon[0], 'cluster': cluster}
    prediction_row = pd.Series(prediction_data_dict) #Create row
    prediction_index = len(mldata)                   #Get new row index
    X_raw = mldata.drop("Price", axis=1)             #Non encoded X 
    y = mldata.Price                                 
    X_raw = X_raw.append(prediction_row, ignore_index=True)     #We append prediction row to X
    X = func.data_encoder(X_raw, cluster)                       #We encode X
    prediction_row_encoded = X.loc[prediction_index]            #We get our prediction row encoded
    X.drop(labels=prediction_index, axis=0, inplace=True)       #We remove the row to train model with prices
    
    ##########################################################################################
    # Prediction
    ##########################################################################################
    col1, col2 = st.columns(2)
    prediction = func.predictor(X, y, prediction_row_encoded, prediction_index) #Train model and get prediction back

    col1.subheader("Prediction: " + str(prediction))
    if actual_price != 0:
        error = prediction - actual_price
        col2.subheader("Error: " + str(error))
        if error < actual_price*0.1:
            st.balloons()

    #Machine learning info input process
def machine_learning(coordinates, property_values, data): 
    if coordinates is not None:
        clusterCheck = st.checkbox("Use clustering")
        if clusterCheck:
            cluster, clus_amount = cluster_finder(coordinates, data) 
            actual_price = prediction_data(property_values, cluster, coordinates)
        else:
            cluster = None
            clus_amount = None
            actual_price = prediction_data(property_values, cluster, coordinates)
        predictbutton = st.button("Predict")
        if predictbutton:
            predict(data, coordinates, property_values, cluster, clus_amount, actual_price)

        




    


    

