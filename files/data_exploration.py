import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def data_metrics (data): #Shows data metrics
    data = data.drop("ZipCode", axis=1)
    data = data.drop("Unnamed: 0", axis=1)
    filesize = os.path.getsize("./data.csv")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(data), )
    col2.metric("Columns", len(data.columns))
    col3.metric("File size (MB)", round(filesize/10**6, 2))

    completedf = st.checkbox("See complete dataframe")
    if completedf:
        st.dataframe(data)

    colnames = st.checkbox("Column names")
    if colnames:
        st.write(data.columns)

def data_info(data):
    data = data.drop("ZipCode", axis=1)
    data = data.drop("Unnamed: 0", axis=1)
    options = ['Price', 'Bathrooms', 'Rooms', 'Surface', 'Pools', 'Air Conditioner',
       'Conservation State', 'Terrace', 'Latitude', 'Longitude', 'Price/m2']
    ### title  ###
    st.header("Data description")
    colselection = st.selectbox("Numeric column", options=options)
    st.subheader(colselection)

    ### metrics ###
    col1, col2 = st.columns(2)
    col1.metric("Mean", round(data[colselection].describe()[1], 2))
    col2.metric("Standard devation", round(data[colselection].describe()[2], 2))
    col3, col4 = st.columns(2)
    col3.metric("Min", round(data[colselection].describe()[3], 2))
    col4.metric("Max", round(data[colselection].describe()[7], 2))
    
    col5, col6, col7 = st.columns(3)
    col5.metric("25%", round(data[colselection].describe()[4], 2))
    col6.metric("50%", round(data[colselection].describe()[5], 2))
    col7.metric("75%", round(data[colselection].describe()[6], 2))

    completedescribe = st.checkbox ("See complete description")
    if completedescribe:
        optionsdes = ['All Columns', 'Price', 'Bathrooms', 'Rooms', 'Surface', 'Pools', 'Air Conditioner',
       'Conservation State', 'Terrace', 'Latitude', 'Longitude', 'Price/m2']
        columnselect = st.multiselect("Columns", optionsdes, default='All Columns')
        ### if all columns in selection show all ###
        if 'All Columns' in columnselect:
            display = data.describe()
            st.dataframe(display)

        ### in case no column is selected, hide dataframe ###
        elif columnselect == []:
            None
        ### display selection ###
        else:
            display = data[columnselect].describe()
            st.dataframe(display)

    nonnumericoptions = ['Autonomous Community', 'Province', 'City', 'Municipality', 'Type', 'Agency']
    colselection2 = st.selectbox("Non-numeric column", options=nonnumericoptions)
    st.subheader(colselection2)

    col1, col2 = st.columns(2)
    col1.metric("Count", data[colselection2].describe()[0])
    col2.metric("Unique", data[colselection2].describe()[1])
    col3, col4 = st.columns(2)
    col3.metric("Top", data[colselection2].describe()[2])
    col4.metric("Top's frequency", data[colselection2].describe()[3])

def map (data):
    st.header ("Map")
    datanonnum = data.describe(exclude="number")
    col4, col5, col6 = st.columns(3)
    col4.metric("Autonomous Communities", datanonnum['Autonomous Community'][1] )
    col5.metric("Provinces", datanonnum['Province'][1])
    col6.metric("Cities", datanonnum['City'][1])
    data.rename(columns = {'Longitude':'longitude', 'Latitude':'latitude'}, inplace = True)

    ciudades = data.City.unique()
    provincias = data.Province.unique()
    comunidades = data['Autonomous Community'].unique()

    main_choice = st.selectbox("Select format for selection:", ["City", "Province", "Autonomous Community"], index=0)
    province_data = data.set_index(main_choice)
    if main_choice == "City":
        values_list = ciudades
    elif main_choice == "Province":
        values_list = provincias
    elif main_choice == "Autonomous Community":
        values_list = comunidades

    ### Choice ###
    choices = st.selectbox(main_choice, values_list,)
    prov = province_data.loc[choices]
    #Values for metrics
    provprice = int((prov.Price.mean()))
    provsurf = int(prov.Surface.mean())
    provroom = round((prov.Rooms.mean()),2)
    provbath = round(prov.Bathrooms.mean(),2)
    provsq = int(prov['Price/m2'].mean())
    ### Comparison ###
    comparebutton, compareprovince =st.columns(2)
    compareselected = comparebutton.checkbox("Compare")
    everything = comparebutton.checkbox("Show me all properties")
    compareprov = compareprovince.selectbox("Comparison " + main_choice, values_list)
    #calculate metrics and compute metrics differences for comparison
    if compareselected:
        compprov = province_data.loc[compareprov]   
        comprovprice = int((compprov.Price.mean()))
        comprovsurf = int(compprov.Surface.mean())
        comprovroom = round((compprov.Rooms.mean()),2)
        comprovbath = round(compprov.Bathrooms.mean(),2)
        comprovsq = int(compprov['Price/m2'].mean())
        ### Comparison computation ###
        com2 = provprice - comprovprice
        com3 = provsurf - comprovsurf
        com4 = provroom - comprovroom
        com5 = provbath - comprovbath
        com6 = provsq - comprovsq
        com1 = len(prov) - len(compprov)
    #If no comparison area is selected difference equals 0
    else:
        com1 = 0
        com2 = 0
        com3 = 0
        com4 = 0
        com5 = 0
        com6 = 0
    if everything:
        prov = data
    ### Map and metrics ###
    st.map(prov)
    col1, col2, col3 = st.columns(3)
    col1.metric("Properties count", len(prov), com1)
    col2.metric("Avrg. Price", provprice, com2)
    col3.metric("Avrg. Surface", provsurf, com3)

    col4, col5, col6 = st.columns(3)
    col4.metric("Avrg. Rooms", provroom, round(com4, 2))
    col5.metric("Avrg. Bathrooms", provbath, round(com5, 2))
    col6.metric("Avrg. Price/m2", provsq, com6)

    message = ("Selected area average price differs " + str(com2) + " from selected comparison area.")
    st.caption(message)
    ### Dataframe display ###
    dfdisplay = st.checkbox("Show Dataframe")
    if dfdisplay:
        st.dataframe(prov)



    
