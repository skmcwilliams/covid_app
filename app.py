#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 09:41:41 2021

@author: skm
"""

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


# Read in data from public sources
pop = int(330593072)
states = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'
counties_str = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
fips = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})

states = pd.read_csv(states)
counties_df = pd.read_csv(counties_str)
states['date'] = pd.to_datetime(states['date'])
counties_df['date'] = pd.to_datetime(counties_df['date'])
counties_df = pd.merge(counties_df,fips, on='fips',how='left')

# create columns based on provided data relative to individual weekly numbers and US population
states['new_cases'] = states['cases'].diff(periods=1)
states['new_deaths'] = states['deaths'].diff(periods=1)
states['cases_per_pop'] = states['cases'].apply(lambda x: (x/pop)*100)
states['deaths_per_pop'] = states['deaths'].apply(lambda x: (x/pop)*100)
states['mortality_rate'] = (states['deaths']/states['cases'])*100
states['case_rate'] = ((states.new_cases - states.new_cases.shift(1)) / states.new_cases.shift(1))*100

pd.set_option('use_inf_as_na', True)
states.fillna(0, inplace=True)

#Set 7, 14, and 30-day moving averages
EMA7 = states.new_cases.ewm(span=7, adjust=False).mean()
EMA14 = states.new_cases.ewm(span=14, adjust=False).mean()
EMA30 = states.new_cases.ewm(span=30, adjust=False).mean()

cases = go.Figure()
cases.add_trace(go.Bar(x=states['date'],y=states['new_cases'],name='Daily Cases'))
cases.add_trace(go.Scatter(x=states['date'],y=EMA7,mode='lines',name='7-day Moving Average',line=dict(color='yellow')))
cases.add_trace(go.Scatter(x=states['date'],y=EMA14,name='14-day Moving Average',line=dict(color='turquoise')))
cases.add_trace(go.Scatter(x=states['date'],y=EMA30,name='30-day Moving Average',line=dict(color='hotpink')))
cases.update_layout(title='Daily Covid-19 Cases in the US',yaxis_title='Cases',xaxis_title='Date',
                   xaxis={'rangeslider': {'visible':True,}})

#Create histogram of cases
box = px.histogram(states,x='new_cases',marginal='box')
box.update_layout(title='Daily Case Distribution and Violin Plot',
                   yaxis_title='Count',xaxis_title='Daily New Cases')

#Plot total cases over time
total = px.line(states,x='date',y='cases')
total.update_layout(title='Covid-19 in the US',yaxis_title='Daily Cases',xaxis_title='Date')

pct = go.Figure()
pct.add_trace(go.Scatter(x=states['date'],y=states['cases_per_pop'],name='Cases',line=dict(color='yellow'),fill='tonexty'))
pct.add_trace(go.Scatter(x=states['date'],y=states['deaths_per_pop'],name='Deaths',line=dict(color='turquoise'),fill='tozeroy'))
pct.add_trace(go.Scatter(x=states['date'],y=states['mortality_rate'],name='Mortality Rate',line=dict(color='hotpink'),fill='tonexty'))
pct.update_layout(title='Metrics as Percentage of Population',
                   yaxis_title='Percent',xaxis_title='Date',
                   xaxis={'rangeslider': {'visible':True,}})

mapfig = px.choropleth(counties_df, geojson=counties, locations='fips', color='cases',
                           color_continuous_scale="Viridis",
                           scope="usa",
                           labels={'cases':'Daily Cases'}
                          )
mapfig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},title='COVID-19 Cases by Couny')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


server = app.server


app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='COVID-19 Dashboard'),

        html.Div(children='''
            Data provided by the New York Times - https://github.com/nytimes/covid-19-data/blob/master/us.csv
        '''),

        html.H3(children='Code can be found here - https://github.com/skmcwilliams/covid_app'),

        dcc.Graph(
            id='EMA',
            figure=cases
        ),  
    ]),

    # New Div for all elements in the new 'row' of the page
    html.Div([
        dcc.Graph(
            id='percentages',
            figure=pct
        ),  
    ]),
     html.Div([
        dcc.Graph(
            id='map',
            figure=mapfig
        ),  
    ]),
    html.Div([
        dcc.Graph(
            id='total',
            figure=total
        ),  
    ]),
    html.Div([
        dcc.Graph(
            id='box',
            figure=box
        ),  
    ]),

])

if __name__ == '__main__':
    app.run_server(debug=True)