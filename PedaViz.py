# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:46:13 2020

@author: USER
"""

import numpy as np
from pylab import *
import matplotlib.pyplot as plt
import MagneT 
import pandas as pd
from scipy import constants as k


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

ni = 4e15
M = MagneT.MagneT(density = ni) 


# Let's calculate the density of state:
g = M.gESS()


# Then the grand thermodynamic potential




# Oms = Ms.OmegaC()


# # Finally, we can calculate the magnetization:


# Mag = M.MagC()
# Mags = Ms.MagC()

# df = pd.DataFrame({'Bfield':B, 'DOS': g[-1,:-1], 'Grand Potential': Om[:-1], 'Magnetization': Mag})


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets=[dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

available_indicators = ['Grand potential','Magnetization']

app.layout = html.Div(children=[
    html.H1(children='Magnetization in Quantum Hall regime'),
      html.Div(children='''
        Visualization to understand magnetization
    '''),
     html.Div([
         dcc.Slider(
             id='nelec',
             min = 0,
             max = np.shape(g)[0],
             value= 500,
             step = 10
            )]),

    html.Div([
        dcc.Graph(
            id='density-graph'),
        html.H1('Progress bar'),
    dbc.Progress(id="progress", value=50, striped=True, animated=True)]),
    html.Div([
        dcc.Checklist(
            id = 'gocal',
            options = [
                {'label': 'Grand potential calculation (takes about 30s)', 'value': 'Go'}],
            value = '')
        ]),
    html.Div([
        dcc.Graph(
            id='GranPot-graph'),
        dcc.Checklist(
            id = 'gocal2',
            options = [
                {'label': 'Mag Calculation', 'value': 'Go'}],
            value = ''),
        dcc.Graph(
            id='Mag-graph')]),
    html.Div([
        html.Div(id='my-div') ])
        
    ])
           

@app.callback(
    dash.dependencies.Output('density-graph', 'figure'),
    [dash.dependencies.Input('nelec', 'value')])
def update_graph(nel):    
    df = pd.DataFrame({'Bfield':M._B, 'DOS': g[nel]})
    return {
        'data': [dict(
            x=df['Bfield'],
            y=df['DOS'],
           # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            #customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            #mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )]
    }




@app.callback(
    dash.dependencies.Output('GranPot-graph', 'figure'),
    [dash.dependencies.Input('gocal', 'value'),
    dash.dependencies.Input('nelec', 'value')])
def update_graph2(val, nel): 
    # ns = M._m/(np.pi*k.hbar**2)*nel 
    nsc  = nel/1002*ni    
    Om = np.zeros(np.shape(shape(M._B)[0]))
    dfo = pd.DataFrame({'Bfield':M._B, 'GrandPotential': Om}) 
    if 'Go' in val : 
        M.gESS(ns = nsc)
        Om = M.OmegaC()
        dfo = pd.DataFrame({'Bfield':M._B, 'GrandPotential': Om})
    return {
        'data': [dict(
              x=dfo['Bfield'],
              y=dfo['GrandPotential'],
                # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                #customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                #mode='markers',
              marker={
                  'size': 15,
                  'opacity': 0.5,
                  'line': {'width': 0.5, 'color': 'white'}
            }
        )]
    }

@app.callback(
    dash.dependencies.Output('Mag-graph', 'figure'),
    [dash.dependencies.Input('gocal2', 'value')])
def update_graph3(val2): 
    Mag = np.zeros(np.shape(M._B)[0]-1)
    dfm = pd.DataFrame({'Bfield':M._B[:-1], 'Magnetization': Mag})
    if 'Go' in val2 :         
        Mag = M.MagC()
        dfm = pd.DataFrame({'Bfield':M._B[:-1], 'Magnetization': Mag})
    return {
        'data': [dict(
              x=dfm['Bfield'],
              y=dfm['Magnetization'],
                # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                #customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                #mode='markers',
              marker={
                  'size': 15,
                  'opacity': 0.5,
                  'line': {'width': 0.5, 'color': 'white'}
            }
        )]
    }

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='gocal', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)


if __name__ == '__main__':
    app.run_server(debug=False)
    
    
