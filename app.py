# COVID-19 EDA Analysis

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 
import pydeck as pdk
import plotly.graph_objs as gobj
import calendar

@st.cache(persist=True)
def load_data_global():
	URL = "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
	df = pd.read_csv(URL)
	df['dateRep'] = pd.to_datetime(df['dateRep'] , format = "%d/%m/%Y")
	#df.drop(columns=['day','month','year'],inplace=True)
	return df

@st.cache(persist=True)
def load_data_india():
	URL = "https://www.mygov.in/covid-19"
	df = pd.read_html(URL)
	df = df[0].rename(columns = {'State/UTs': 'States'})
	return df

def plotBarFunc(df):
	fig = go.Figure()
	fig.add_trace(go.Bar(
	    x=df.index,
	    y=df.cases,
	    name='Confirmed',
	    marker_color='ORANGE'
	))
	fig.add_trace(go.Bar(
	    x=df.index,
	    y=df.deaths,
	    name='Deceased',
	    marker_color='PURPLE'
	))

	# Here we modify the tickangle of the xaxis, resulting in rotated labels.
	fig.update_layout(
	                    barmode='group',
	                    xaxis_tickangle=-90,
	                    title = "COVID-19 Pandemic affected Continents",
	                    plot_bgcolor = '#FFEEFF'
	                )

	st.write(fig)


def plot_country_map(countries,continent,figure):

	countries = [x.replace('_',' ') for x in countries]
	text,title,z = 'Deceased','No. of Deaths',np.array(figure.deaths)

	if(get_status() == "Confirmed Cases"):
		text,title,z = 'Confirmed','No. of Confirmed Cases',np.array(figure.cases)

	data = dict(type = 'choropleth',
            locations = countries,
            locationmode = 'country names',
            colorscale= 'Portland',
            text= text,
            z=z,
            colorbar = {'title':title, 'len':200,'lenmode':'pixels' }
            )
	
	#initializing the layout variable
	continent = continent.lower()
	if continent == 'america' or continent == 'oceania':
		continent = 'world'
		
	layout = dict(geo = {'scope':continent})
	
	# Initializing the Figure object by passing data and layout as arguments.
	col_map = gobj.Figure(data = [data],layout = layout)

	st.write(col_map)

def get_status():
	return status

def get_status2():
	return status2

def get_status4():
	return status4

def draw_scatter(df):
	fig = go.Figure(data=go.Scatter(x=df.index,
                                y=df,
                                mode='markers+lines',
                                marker=dict(
                                    size=13,
                                    color=np.random.randn(len(df)), #set color equal to a variable
                                    colorscale='reds' # one of plotly colorscales
                                    )
                                ))

	fig.update_layout(title="Top {} Affected Countries".format(number))
	st.write(fig)

def plot_states(df , caseType):
	y, title = df.Confirmed, 'Confirmed COVID-19 Cases Till Now in India'
	if caseType == 'a':
		y, title = df.Active, 'Active COVID-19 Cases Till Now in India'
	elif caseType == 'd':
		y, title = df.Deceased, 'Deceased COVID-19 Cases Till Now in India'
	elif caseType == 'r':
		y, title = df.Recovered, 'Recovered COVID-19 Cases Till Now in India'

	fig = go.Figure(data=go.Scatter(x=df.States,
                                y=y,
                                mode='markers+lines',
                                marker=dict(
                                    size=10,
                                    color=np.random.randn(len(df)), #set color equal to a variable
                                    colorscale='inferno', # one of plotly colorscales
                                    )
                                ))

	fig.update_layout(title=title)
	st.write(fig)


data_global = load_data_global()

st.title("COVID-19 UPDATES AND INSIGHTS")
st.markdown("Get latest updates on COVID-19 WorldWide")
st.image("cv19s.jpg")

# --------------------CONTINENTS-------------------------------------------------------
st.title("Continents affected due to COVID-19")
continent_grp = data_global.groupby("continentExp")
figure = continent_grp[['cases','deaths']].sum()

list_cont = ['All']
list_cont.extend(sorted(figure.index.to_list()))
list_cont.remove('Other')

country=""
status=""
select = st.selectbox("Select Continent",list_cont)

if select != 'All':
	list_cntry = ['All']
	list_cntry.extend(continent_grp.get_group(select).countriesAndTerritories.unique())

	country = st.selectbox("Select Country",list_cntry)
	
	figure = data_global.groupby(['continentExp','countriesAndTerritories'])
	
	status = st.radio("See the count of",("Confirmed Cases","No. of Deaths"))

	if country == 'All':
		figure = figure[['cases','deaths']].sum().loc[(select), :]
		plot_country_map(list_cntry[1:],select,figure)

	else:
		figure = figure[['cases','deaths']].sum().loc[(select,country)]
		plot_country_map([country],select,figure)

else:
	plotBarFunc(figure);
	

if st.checkbox("See figures",False):
	st.subheader("Confirmed and Deceased cases in Different Continents")
	#figure = figure.sort_values(by='cases',ascending = False)
	st.table(figure)


#-------------------CONTINENTS-------------------------------------------

#-----------------TOP AFFECTED COUNTRIES-------------------------------------

st.title("Top Affected Countries In The World")
status2 = st.radio("See the count of",("Confirmed Cases","No. of Deaths"),key='num')
number = st.slider("no. of countries", 5, 20)
country_grp = data_global.groupby("countriesAndTerritories")
country_cases = country_grp.cases.sum().nlargest(number)
country_deaths = country_grp.deaths.sum().nlargest(number)

if(get_status2() == "Confirmed Cases"):
	draw_scatter(country_cases)
	if st.checkbox("See figures",False,2):
		st.subheader("Top {} Affected Countries".format(number))
		#figure = figure.sort_values(by='cases',ascending = False)
		st.table(country_cases)
else:
	draw_scatter(country_deaths)
	if st.checkbox("See figures",False,2):
		st.subheader("Top {} Affected Countries".format(number))
		#figure = figure.sort_values(by='cases',ascending = False)
		st.table(country_deaths)

#-----------------TOP AFFECTED------------------------------------------------------------------

#-----------------INDIA SPECIFIC-------------------------------------------------------------

ind_grp = country_grp.get_group("India")
st.title("COVID-19 Outbreak in India")
choice = st.radio("",("Daywise Analysis","Monthwise Analysis"), key="wise")

if choice == "Daywise Analysis":
	status3 = st.radio("See the count of",("Confirmed Cases","No. of Deaths"),key='Daywise')
	
	case_or_death, name, title = ind_grp['deaths'], 'deaths per day', 'COVID-19 Daywise deaths'
	
	if status3 == "Confirmed Cases":
		case_or_death, name, title = ind_grp['cases'], 'new cases per day', 'COVID-19 Daywise Confirmed Cases'

	fig = go.Figure(go.Scatter(x = ind_grp['dateRep'], y = case_or_death,name=name))

	fig.update_layout(title=title,
	                   plot_bgcolor='#FFEEFF', colorway = ['#000000'],
	                   showlegend=True)

	st.write(fig)

else:
	monthwise = ind_grp.groupby(['year','month'])
	monthwise['cases'].sum()
	mnt = monthwise['cases'].sum().loc[2020]
	mnt.cumsum()
	mnt_deaths = monthwise['deaths'].sum().loc[2020]

	month=[calendar.month_name[x] for x in mnt.index]

	fig = go.Figure(data=[
	    go.Bar(name='Cases', x=month, y=mnt.cumsum()),
	    go.Bar(name='Deaths', x=month, y=mnt_deaths.cumsum())
	])
	# Change the bar mode
	fig.update_layout(title = 'Monthly Analysis of COVID-19 India for the year 2020',
	                  barmode='group' ,
	                  plot_bgcolor = '#FFEEFF',
	                  colorway = ['BLUE' , 'GREEN']
	                 )
	st.write(fig)

#-------------INDIA SPECIFIC-----------------------------------------------------------------------------


#------------STATE WISE----------------------------------------------------------------------------------

web_table_list = pd.read_html("https://www.mygov.in/covid-19")
st.title("Indian States/UT's vs COVID-19")

allStatesData = load_data_india()

filter1 = allStatesData.Confirmed != 0
web_df = allStatesData[filter1]

st.header("Top Most Affected State/UT")

status4 = st.radio("See the count of",("Confirmed Cases", "Active Cases", "Recovered Cases", "No. of Deaths"),key='statewise')

num2 = st.slider("", 10, len(web_df),key="states")

if get_status4() == "Confirmed Cases":
	temp_df = web_df.sort_values(by='Confirmed' , ascending = False)
	plot_states(temp_df.iloc[0:num2],'c')

elif get_status4() == "No. of Deaths":
	temp_df = web_df.sort_values(by='Deceased' , ascending = False)
	plot_states(temp_df.iloc[0:num2],'d')

elif get_status4() == "Active Cases":
	temp_df = web_df.sort_values(by='Active' , ascending = False)
	plot_states(temp_df.iloc[0:num2],'a')

else:
	temp_df = web_df.sort_values(by='Recovered' , ascending = False)
	plot_states(temp_df.iloc[0:num2],'r')

if st.checkbox("See figures",False, key="statewise"):
	st.subheader("Statewise Data")
	#figure = figure.sort_values(by='cases',ascending = False)
	st.table(web_df)


#************* CORONA FREE STATE/UT*************************************************

st.title("COVID-19 Free State/UT in India")
st.subheader("List of all those State/UT where there is no active case at present.")

filter2 = allStatesData.Active == 0
free_states = allStatesData[filter2]
free_states.sort_values(by ='Confirmed' , ascending = False , inplace = True)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=free_states.States,
    y=free_states.Confirmed,
    name='Confirmed',
    marker_color='RED'
))
fig.add_trace(go.Bar(
    x=free_states.States,
    y=free_states.Recovered,
    name='Recovered',
    marker_color='GREEN'
))
fig.add_trace(go.Bar(
    x=free_states.States,
    y=free_states.Deceased,
    name='Deceased',
    marker_color='BLUE'
))

	# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(
                    barmode='group',
                    xaxis_tickangle=-45,
                    title = "Corona Free States/UT's",
                    plot_bgcolor = '#FFEEFF'
                )
st.write(fig)

if st.checkbox("See figures",False, key="free_states"):
	st.subheader("COVID-19 Free State/UT")
	if len(free_states) > 0:
		st.table(free_states.set_index('States'))
	else:
		st.markdown("Sorry, At Present None of the States/UT's are unaffected.")

	#************************************************************************************

#-------------------------STATEWISE--------------------------------------------------------------------
