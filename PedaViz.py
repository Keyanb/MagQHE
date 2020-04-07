# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:46:13 2020

@author: USER
"""

import numpy as np
import matplotlib.pyplot as plt
import MagneT 
import pandas as pd


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


M = MagneT.MagneT(density = 4e15) 


# Let's calculate the density of state:
g = M.gESS()


# Then the grand thermodynamic potential



Om = M.OmegaC()
# Oms = Ms.OmegaC()


# # Finally, we can calculate the magnetization:


# Mag = M.MagC()
# Mags = Ms.MagC()

# df = pd.DataFrame({'Bfield':B, 'DOS': g[-1,:-1], 'Grand Potential': Om[:-1], 'Magnetization': Mag})


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

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
            id='density-graph')]),
    html.Div([
        dcc.Checklist(
            id = 'gocal',
            options = [
                {'label': 'Grand potential calculation', 'value': 'Go'}],
            value = '')
        ]),
    html.Div([
        dcc.Graph(
            id='GranPot-graph')]
        
    )])
           

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
    dfo = pd.DataFrame({'Bfield':M._B, 'GrandPotential': g[0]})
    if 'Go' in val : 
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


if __name__ == '__main__':
    app.run_server(debug=False)
    
    
