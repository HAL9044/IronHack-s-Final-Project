import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import data_exploration as ex
import eda 
import ml
import functions as func

data = pd.read_csv("./data.csv", low_memory=False)
#data.drop("Unnamed: 0", axis=1, inplace =True)

st.title("Spanish Properties Project")
st.write("by Diego Mesa")

page = st.selectbox("Pages", ["Read Me", "Preliminary Data Exploration", "Exploratory Data Analysis", "Machine Learning"])
#page = "Exploratory Data Analysis"
if page == "Read Me":
       func.README()  
elif page == "Preliminary Data Exploration":
       st.title(page)
       ex.data_metrics(data)
       ex.data_info(data)
       ex.map(data)
elif page == "Exploratory Data Analysis":
       st.title(page)
       eda.main(data)
       numerics = eda.numerics_generator(data)
       data = eda.dataCleanFilter(data)
       eda.plotter(data, numerics)
elif page == "Machine Learning":
       data = pd.read_csv("./data.csv", low_memory=False)
       st.write(len(data))
       st.title("Machine learning & predictions")
       coordinates, property_values = ml.info_input(data)
       ml.machine_learning(coordinates, property_values, data)

       