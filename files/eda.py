from time import asctime
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import functions as func
import matplotlib.colors as mcolors

def main (data):
    st.subheader("Data information and cleaning")
    col1, col2, col3 = st.columns(3)
    seeDataframe = col1.checkbox("See Dataframe")
    if seeDataframe:
        st.dataframe(data)
    missingcheck = col2.checkbox("See missing values")
    if missingcheck:
        func.missing_values(data)

def dataCleanFilter(data):
    st.subheader("Data cleaning & filtering")
    ##########################################################################################
    #Gets unique values for selection list
    ciudades = data.City.unique()
    provincias = data.Province.unique()
    comunidades = data['Autonomous Community'].unique()
    #User selects area type
    main_choice = st.selectbox("Select area type:", ["City", "Province", "Autonomous Community"], index=0)
    data = data.set_index(main_choice)
    #Values are defined according to area type selected
    if main_choice == "City":
        values_list = ciudades
    elif main_choice == "Province":
        values_list = provincias
    elif main_choice == "Autonomous Community":
        values_list = comunidades
    #User picks values previously defined
    choices = st.multiselect(main_choice, values_list)
    ##########################################################################################
    useAll = st.checkbox("Use everything", value = True)
    data.rename(columns = {'Longitude':'longitude', 'Latitude':'latitude'}, inplace = True) #rename columns for map function
    if not useAll:
        data = data.loc[choices]    #If use all is not selected use choices defined above
    ##########################################################################################
    #Selectors display
    ##########################################################################################
    col4, col5 = st.columns(2)
    price = col4.slider('Price (in thousands)', 0, 1000, (0, 600), step=1)
    surface = col5.slider('Surface ', 0.0, 1000.0, (0.0, 1000.0), step=1.0)
    pricem2 = st.slider('Price/m2 ', 0.0, 10000.0, (0.0, 10000.0), step=1.0)
    rooms = col4.slider('Rooms: ', 0, 20, (0, 19), step=1)
    bathrooms = col5.slider('Bathrooms: ', 0, 10, (0,9), step=1)
    ##########################################################################################
    col1, col2, col3= st.columns(3)
    col1.write('Prices from: ' + str(price[0] * 10**3) + " to " + str(price[1] * 10**3))
    col1.write('Surface : ' + str(surface[0]) + " to " + str(surface[1]))
    col2.write('Price/m2 : ' + str(surface[0]) + " to " + str(surface[1]))
    col2.write('Rooms : ' + str(rooms[0]) + " to " + str(rooms[1]))
    col3.write('Bathrooms : ' + str(bathrooms[0]) + " to " + str(bathrooms[1]))
    col3.write('Area : ' + str(choices))
    ##########################################################################################
    #Cut data according to selction and display
    data = func.scissors(price, surface, pricem2, rooms, bathrooms, data)
    st.map(data)
    ##########################################################################################
    #Show metrics
    ##########################################################################################
    col1, col2, col3 = st.columns(3)
    col1.metric("Properties count", len(data))
    col2.metric("Avrg. Price", int(round(data.Price.mean(), 0)))
    col3.metric("Avrg. Surface", round(data.Surface.mean(), 2))
    ##########################################################################################
    col4, col5, col6 = st.columns(3)
    col4.metric("Avrg. Rooms", round(data.Rooms.mean(), 2))
    col5.metric("Avrg. Bathrooms", round(data.Bathrooms.mean(),2))
    col6.metric("Avrg. Price/m2", round(data['Price/m2'].mean(),2))
    ##########################################################################################
    #data save as .csv
    filegenerator = st.checkbox("Save as csv")
    if filegenerator:
        name = st.text_input("File name")
        saveselection = st.button("Save file")
        if saveselection:
            data.to_csv("../csv_exports/" + name)
    return data

def numerics_generator(data): #picks numerical columns only
    data.rename(columns = {'Longitude':'longitude', 'Latitude':'latitude'}, inplace = True)
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    numericdf = data.select_dtypes(include=numerics)
    numeric_columns = list(numericdf.columns)
    return numeric_columns

def scatter(data, numerics): #Scatter plot generator
    st.subheader("Scatter plot")
    cmaps = mcolors.LinearSegmentedColormap.from_list("n", ["crimson", "gold","steelblue"])
    data['color_code'] = pd.Categorical(data.index)
    data['color_code'] = data['color_code'].cat.codes
    title = st.text_input("Scatter title: ")
    data['Selection'] = pd.Categorical(data.index)
    data['Selection'] = data.Selection.cat.codes
    col1, col2, col3 = st.columns(3)
    xAxis =col1.selectbox("X axis: ", numerics, index=4)
    yAxis =col2.selectbox("Y axis: ", numerics, index = 1)
    fig = plt.figure(figsize=(30,30))
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.tick_params(axis='both', which='major', labelsize=25)
    plt.scatter(data[xAxis], data[yAxis], cmap=cmaps, c=data.color_code)
    plt.title(title, fontsize = 40)
    plt.legend()
    st.pyplot(fig)
    st.write(data.index.unique())
    return fig

def histograms(data):   #Histogram generator
    st.subheader("Histogram")
    title = st.text_input("Histogram title: ")
    col1, col2 = st.columns(2)
    selection =col1.selectbox("Column: ", list(data.columns), index=1)
    bins = col2.slider("Bins :", 1, 20, step=1, value=6)
    fig = plt.figure(figsize=(15,15))
    plt.hist(data[selection], stacked=False, bins=bins)
    plt.xticks(rotation='vertical')
    plt.xlabel(selection)
    plt.ylabel("Count")
    plt.title(title, fontsize = 40)
    st.pyplot(fig)
    return fig

def barCharts(data):    #Bar chart generator
    st.subheader("Bar chart")
    title = st.text_input("Bar Chart title: ")
    fig = plt.figure(figsize=(20,20))
    gbtype = ['Count', 'Mean', 'Median']
    col1, col2, col3 = st.columns(3)
    selectionX = col1.selectbox("x", data.columns, index=2)
    selectionY = col2.selectbox("Y", data.columns)
    selectionType = col3.selectbox("Group by using: ", gbtype)
    if selectionType == 'Count':
        df = data.groupby(selectionX).count()
    elif selectionType == 'Mean':
        df = data.groupby(selectionX).mean()
    else: 
        df = data.groupby(selectionX).median()
    sort = col1.checkbox("Sort")
    if sort:
        df = df.sort_values(by=selectionY, ascending=False)
    plt.bar(df.index, df[selectionY], color='green')
    plt.xticks(rotation='vertical')
    plt.xlabel(selectionX)
    plt.ylabel(selectionY)
    plt.title(title, fontsize = 40)
    st.pyplot(fig)
    return fig

def boxPlot(data, numerics):    #Box Plot generator
    st.subheader("Box Plot")
    title = st.text_input("Box Plot title: ")
    selection = st.selectbox("Column", numerics, index=1)
    autcomselection = st.checkbox("Compare areas of selection")
    
    if autcomselection:
        fig = plt.figure(figsize=(20,20))
        sns.set_theme(style="whitegrid")
        plt.xticks(rotation=90)
        sns.boxplot(x=data.index, y=selection, data=data)
    else:
        fig = plt.figure(figsize=(15,15))
        plt.boxplot(data[selection])
        plt.xlabel(selection)
    plt.tick_params(axis='both', which='major', labelsize=20)
    plt.title(title, fontsize = 40)
    st.pyplot(fig)
    return fig

def pieChart(data):
    None

def correlation_matrix(data):   #Correlation Matrix generator
    fig = plt.figure(figsize=(20,20))
    title = st.text_input("Correlation matrix title: ")
    plt.tick_params(axis='both', which='major', labelsize=20)
    corr_ma = data.corr()
    sns.heatmap(corr_ma, annot=True)
    plt.title(title, fontsize = 40)
    st.pyplot(fig)
    return fig
    
def plotter(data, numerics):    #It plots and saves images
    st.subheader("Plotting")
    col1, col2, col3, col4, col5 = st.columns(5)
    scattercheck = col1.checkbox("Scatter")
    histocheck = col2.checkbox("Histogram")
    barcheck = col3.checkbox("Bar Chart")
    boxcheck = col4.checkbox("Box Plot")
    coorcheck = col5.checkbox("Correlation Matrix")
    figuresList= []
    if scattercheck:
        figscatter = scatter(data, numerics)
        figuresList.append(figscatter)
    if histocheck:
        fighist = histograms(data)
        figuresList.append(fighist)
    if barcheck:
        figbar = barCharts(data)
        figuresList.append(figbar)
    if boxcheck:
        figbox = boxPlot(data, numerics)
        figuresList.append(figbox)
    if coorcheck:
        figxoor = correlation_matrix(data)
        figuresList.append(figxoor)
    func.image_save(figuresList)    



    


    


     
