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


B1 = linspace(0.125,1.5,2500)
Bf = 1/B1
NLL = 50
Ma = MagneT.MagneT( NLL = NLL, Bfield = Bf, N_sum_E = 500) 
Mc = MagneT.MagneT( NLL = NLL, Bfield = Bf, N_sum_E = 500) 
dfA = pd.DataFrame({'Bfield':Bf})
# Let's calculate the density of state:
# g = M.gESS(Bs = 2)


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets=[dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

available_indicators = ['Grand potential','Magnetization']

app.layout = html.Div(children=[
    html.H1(children='Magnetization in Quantum Hall regime'),
      html.Div(children='''
        Visualization to understand magnetization
    '''),
    
      dcc.Checklist(
          id='calc',
          options=[
            {'label': 'Analytical calculation  ', 'value': 'an'},
            {'label': 'Numérical calculation', 'value': 'nu'}],
          value='an'),
           
      html.Div([
       dcc.Graph(
            id='vardens-graph')]),
    
    html.Div([
        html.Label(r'Chose the electron density of your 2DEG in $m^{-2}$:'),
         dcc.Slider(
             id='nelec',
             min = 0,
             max = 1e16,
             marks={i: '{:.1E}'.format(i) for i in range(0,int(1e16),int(1e15))},
             value= 3e15,
             step = 1e14
            ),
        html.Label(r'disorder type'),
        dcc.Dropdown(
             id='GL',
             options=[
            {'label': 'Gaussian', 'value': '1'},
            {'label': u'Lorentzian', 'value': '0'},          
            ],
            value='0'
             
            ),
        html.Label(r'x axis:'),
        dcc.RadioItems(
            id='Bfstyle',
             options=[
            {'label': 'Magnetic field  ', 'value': 'Bf'},
            {'label': u'inverse magnetic field', 'value': 'B1f'},          
            ],
            value='Bf'
             
            )
        ], style={'width': '48%',  'display': 'inline-block'}),
    
    html.Div([    
        html.Label(r'Energy broadening of Landau levels by disorder in Kelvin'),
        dcc.Slider(         
            id = 'gamma',
            min = 0.5,
            max = 40,
            value = 5,
            marks = {i: '{}'.format(i) for i in range(0,50,5)},
            step = 1/10),
        html.Label(r'Constant density broadening %'),
        dcc.Slider(
            id = 'Xi',
            min = 0,
            max = 1,
            value = 0.1,
            marks = {i: '{:.2E}'.format(i) for i in range(0,100,10)},
            step = 1/50)
         
        ], 
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    
    # html.Div([
    #     html.Label(r'Density of state calculated numerically (allow spin splitting'),
    #     dcc.Graph(
    #         id='density-graph') ]),
    #     html.H1('Progress bar'),
    # dbc.Progress(id="progress", value=50, striped=True, animated=True)]),
        
    html.Div([
        html.Label(r'At what magnetic field do you see spin splitting? (to compute de exange enhencement of Zeeman splitting)'),
        dcc.Input(
             id='Bsplit',             
             value= 0,          
            ),
        html.Label(r'Tesla') ]),
    
    html.Div([
        dcc.Checklist(
            id = 'gocal',
            options = [
                {'label': 'Grand potential calculation (takes few seconds)', 'value': 'Go'}],
            value = '') ]),
    
    html.Div([
        dcc.Graph(
            id='GranPot-graph'),
        # dcc.Graph(
        #     id = 'Granpot-graphC'),
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
    dash.dependencies.Output('vardens-graph', 'figure'),
    [dash.dependencies.Input('nelec', 'value'),
    dash.dependencies.Input('gamma', 'value'),
    dash.dependencies.Input('Xi', 'value'),
    dash.dependencies.Input('GL', 'value'),
    dash.dependencies.Input('calc', 'value'),
    dash.dependencies.Input('Bsplit', 'value'),
    dash.dependencies.Input('Bfstyle', 'value')]
    )
def update_graph(nel,gam, Xi, GLo, cal, bsp, bfs): 
    gEA = Ma.gEA(ns = nel, Gam = gam*k.k, Xi = float(Xi), GL = int(GLo))
    # dfA = pd.DataFrame({'Bfield':Ma._B, 'DOSA': gEA})
    dfA['DOSA'] =  gEA
    ca = []
    if isin('an', cal):
        ca.append('DOSA')
    if isin('nu', cal):
        g = Mc.gESS(ns = nel, Gam = gam*k.k, Xi = float(Xi), GL = int(GLo), Bs = float(bsp) )
        dfA['DOSC'] = g[shape(g)[0]//2]
        ca.append('DOSC')
    if bfs == 'Bf':
        dfA['Bfield'] = Ma._B
    else:
         dfA['Bfield'] = 1/Ma._B
    return {
        'data': [dict(
                x=dfA['Bfield'],
                y=dfA[i],
                # x=dfA['Bfield'],
                # y=dfA['DOSEF'],
           # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            #customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            #mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        ) for i in ca ]
    }



@app.callback(
    dash.dependencies.Output('GranPot-graph', 'figure'),
    [dash.dependencies.Input('nelec', 'value'),
    dash.dependencies.Input('gamma', 'value'),
    dash.dependencies.Input('Xi', 'value'),
    dash.dependencies.Input('GL', 'value'),
    dash.dependencies.Input('calc', 'value'),
    dash.dependencies.Input('Bsplit', 'value'),
    dash.dependencies.Input('Bfstyle', 'value'),
    dash.dependencies.Input('gocal', 'value')]
    )
def update_graph2(nel,gam, Xi, GLo,cal, bsp,  bfs, val): 
    co = []
    if 'Go' in val : 
        if isin('an', cal):     
            OmA = Ma.OmegaA()
            # dfA = pd.DataFrame({'OmegaA': OmA})
            dfA['OmegaA'] = OmA
            co.append('OmegaA')         
        if isin('nu', cal):
            OmC = Mc.OmegaC()
            dfA['OmegaC'] = OmC
            co.append('OmegaC')
        if bfs == 'Bf':
            dfA['Bfield'] = Ma._B
        else:
            dfA['Bfield'] = 1/Ma._B
    return {
        'data': [dict(
            x=dfA['Bfield'],
            y=dfA[i],
           # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            #customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            #mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )for i in co ]
    }


# @app.callback(
#     dash.dependencies.Output('Granpot-graphC', 'figure'),
#     [dash.dependencies.Input('gocal', 'value'),
#     dash.dependencies.Input('nelec', 'value')])
# def update_graph2(val, nel): 
       
#     Om = np.zeros(np.shape(shape(Mc._B)[0]))
#     dfo = pd.DataFrame({'Bfield':Mc._B, 'GrandPotential': Om}) 
#     if 'Go' in val : 
#         # Mc.gESS(ns = nel)
#         Om = Mc.OmegaC()
#         dfo = pd.DataFrame({'Bfield':Mc._B, 'GrandPotential': Om})
#     return {
#         'data': [dict(
#               x=dfo['Bfield'],
#               y=dfo['GrandPotential'],
#               text= 'Density',
#                 #customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
#                 #mode='markers',
#               marker={
#                   'size': 15,
#                   'opacity': 0.5,
#                   'line': {'width': 0.5, 'color': 'white'}
#             }
#         )]
#     }

@app.callback(
    dash.dependencies.Output('Mag-graph', 'figure'),
     [dash.dependencies.Input('nelec', 'value'),
    dash.dependencies.Input('gamma', 'value'),
    dash.dependencies.Input('Xi', 'value'),
    dash.dependencies.Input('GL', 'value'),
    dash.dependencies.Input('calc', 'value'),
    dash.dependencies.Input('Bsplit', 'value'),
    dash.dependencies.Input('Bfstyle', 'value'),
    dash.dependencies.Input('gocal2', 'value')])
def update_graph3(nel, gam, Xi, GLo, cal, bsp,  bfs, val2): 
    Mag = np.zeros(np.shape(Mc._B)[0])
    dfA['MagnetizationA']  = Mag
    dfA['MagnetizationC']  = Mag
    cm = []
    if 'Go' in val2 : 
        if isin('an', cal):
            MagA = Ma.MagA()
            dfA['MagnetizationA']  = MagA
            cm.append('MagnetizationA')
        if isin('nu', cal):             
            MagC = Mc.MagC()
            MagC = np.append(MagC,MagC[-1])
            dfA['MagnetizationC']  = MagC
            cm.append('MagnetizationC')
    return {
        'data': [dict(
              x=dfA['Bfield'],
              y=dfA[i],
                # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                #customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                #mode='markers',
              marker={
                  'size': 15,
                  'opacity': 0.5,
                  'line': {'width': 0.5, 'color': 'white'}
            }
        ) for i in cm]
    }

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='GL', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)


if __name__ == '__main__':
    app.run_server(debug=False)
    
    
