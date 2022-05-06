# IronHack's Final Project

# About
## What is this all about? 
Hi there! 
What I've built here is a little app based on information about properties on sale within the Spanish territory. The final product is a streamlit app that holds three different pages: 

* **Preliminary Data Exploration** : 
This section offers basic information on the dataset and allows the user to experiment a bit with its distribution on a map. You can check the complete dataframe used, or scroll down to make comparison between different cities, provinces or autonomous communities. 

* **Exploratory Data Analysis**:
On this page, you'll be able to do some basic data exploration using charts and other statistical markers. The program also allows the selection of specific regions in Spain and other filtering of attributes. You could for example select all properties in Cataluña with prices below a certain number and then plot a histogram based on bathrooms number.  You can then save a csv with the selected properties in 'csv_exports' folder and plotted images as a .png in "img_exports" folder. 
* **Machine learning**:
This page will allow you to make predictions on the price of a property. At first the program will demand key values about the property, like house type, amount of rooms and bathrooms, surface or (at least) an approximate address in order to let the program get coordinates. Once this is done, you can choose to get a prediction based solely on that information or you can determine a "price cluster" based on the surrounding properties already present in the dataset. This adds a dimension of human knowledge (and of course human error) to the prediction. This function will be described in greater detail later. 
## How to use 
To start the program simply `$ streamlit run main.py` !
## Folder structure
<pre>
└── IronHack's Final Project/
    ├── csv_exports
    ├── files/
    │   ├── main.py
    │   ├── data_exploration.py
    │   ├── eda.py
    │   ├── ml.py
    │   ├── functions.py
    │   ├── data.csv
    │   └── streamlitreadme.md
    ├── img_exports
    ├── notebooks/
    │   ├── EDA.ipynb
    │   ├── Info_scrapper.ipynb
    │   └── WebHarvester.ipynb
    └── README.md
    </pre>
## Status
The main aspects of the project are finished. There are still some minor bugs that will be fixed, and more features might be added in the future.
## To do
* Add more columns to the dataset (floor, elevator...)
* Add more rows to the dataset (100k-200k)
* Improve machine learning model
## Technology stack
Libraries used: 
* Python
* Pandas
* Scikit-learn
* Streamlit
* Matplotlib
* Seaborn
* Geopy
* XGBoost
* Requests
* TOR network
* Socks5
*(See requirements.txt in main folder)*

### The info obtained
When I was done with the scrapping process, I was left with a total of 3476 files. From those files, I filtered the information to get data on: 
* Price
* Rooms
* Bathrooms
* Surface
* Price/m² 
* Pools (boolean)
* Air conditioner (boolean)
* Type (Flat, House chalet...)
* IsNewConstruction (boolean)
* Terrace (boolean)
* Autonomous Community
* Province
* City
* Municipality
* ZipCode
* Latitude
* Longitude

### How the information was obtained
To get the information I needed I scrapped a real estate web. I won't be disclosing its name in order to avoid getting in any sort of trouble. But in short, I managed to scrap around one hundred thousand properties from said web and not getting blacklisted rotating the IP address using TOR's network, changing my user-agent and adding a random amount of time between requests to make it seem more as if a human was making them. You can read about the process in bigger detail in this [first Medium story I wrote.](https://medium.com/@diegomesamarrero/how-i-managed-to-scrap-over-100k-properties-from-a-spanish-real-estate-website-be3cb14be594)

