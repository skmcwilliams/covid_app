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


# Read in data from public sources
pop = int(330593072)
data = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'
data = pd.read_csv(data)
data['date'] = pd.to_datetime(data['date'])

# create columns based on provided data relative to individual weekly numbers and US population
data['new_cases'] = data['cases'].diff(periods=1)
data['new_deaths'] = data['deaths'].diff(periods=1)
data['cases_per_pop'] = [(cases/pop)*100 for cases in data['cases']]
data['deaths_per_pop'] = [(deaths/pop)*100 for deaths in data['deaths']]
data['mortality_rate'] = data['deaths']/data['cases']
data['mortality_rate'] = [dpc*100 for dpc in data['mortality_rate']]
data['case_rate'] = ((data.new_cases - data.new_cases.shift(1)) / data.new_cases.shift(1))*100

pd.set_option('use_inf_as_na', True)
data.fillna(0, inplace=True)

#Set 7, 14, and 30-day moving averages
EMA7 = data.new_cases.ewm(span=7, adjust=False).mean()
EMA14 = data.new_cases.ewm(span=14, adjust=False).mean()
EMA30 = data.new_cases.ewm(span=30, adjust=False).mean()

fig = go.Figure()
fig.add_trace(go.Scatter(x=data['date'],y=data['new_cases'],fill='tonexty',name='New Cases'))
fig.add_trace(go.Scatter(x=data['date'],y=EMA7,mode='lines',name='7-day Moving Average',line=dict(color='black')))
fig.add_trace(go.Scatter(x=data['date'],y=EMA14,name='14-day Moving Average',line=dict(color='turquoise')))
fig.add_trace(go.Scatter(x=data['date'],y=EMA30,name='30-day Moving Average',line=dict(color='hotpink')))
fig.update_layout(title='Daily Covid-19 Cases in the US',yaxis_title='Cases',xaxis_title='Date',
                   xaxis={'rangeslider': {'visible':True,}})

#Create histogram of cases
fig2 = px.histogram(data,x='new_cases',marginal='box')
fig2.update_layout(title='New Case Distribution and Violin Plot',
                   yaxis_title='Count',xaxis_title='Daily New Cases')

#Plot total cases over time
fig3 = px.line(data,x='date',y='cases')
fig3.update_layout(title='Covid-19 in the US',yaxis_title='Cases',xaxis_title='Date')

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
            figure=fig
        ),  
    ]),

    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children=''),

        html.Div(children='''
            
        '''),

        dcc.Graph(
            id='total',
            figure=fig2
        ),  
    ]),

    html.Div([
        html.H1(children=''),

        html.Div(children='''
            
        '''),

        dcc.Graph(
            id='box',
            figure=fig3
        ),  
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)