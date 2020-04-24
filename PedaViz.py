# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:46:13 2020

@author: USER
"""
import os

import numpy as np
from pylab import *
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import MagneT
import pandas as pd
from scipy import constants as k


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

external_scripts = [
    {
        "src": "https://cdnjs.cloudflare.com/ajax/libs/foundation/6.6.3/js/foundation.min.js",
        "integrity": "sha256-pRF3zifJRA9jXGv++b06qwtSqX1byFQOLjqa2PTEb2o=",
        "crossorigin": "anonymous",
    }
]

external_stylesheets = [
    {
        "href": "https://cdnjs.cloudflare.com/ajax/libs/foundation/6.6.3/css/foundation.min.css",
        "rel": "stylesheet",
        "integrity": "sha256-ogmFxjqiTMnZhxCqVmcqTvjfe1Y/ec4WaRj/aQPvn+I",
        "crossorigin": "anonymous",
    }
]

app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
)
server = app.server


app.config.suppress_callback_exceptions=True

figure_layout = dict(

    margin={"l": 100, "b": 40, "t": 10, "r": 0},
    hovermode="closest",
)

B1 = linspace(0.125, 1, 1000)
Bf = 1 / B1
NLL = 30
Ma = MagneT.MagneT(NLL=NLL, Bfield=Bf, N_sum_E=150)
Mc = MagneT.MagneT(NLL=NLL, Bfield=Bf, N_sum_E=300)
dfA = pd.DataFrame({"Bfield": Bf})

#
#

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
            
        </footer>
    </body>
</html>
'''


available_indicators = ["Analytical", "Numerical"]

app.layout = html.Div(
    id = 'intro',
    children=[
        html.H1(children="Magnetization in Quantum Hall regime"),
        html.H5(
            children="""
        App to calculate the magnetization in Quantum Hall regime
    """
        ),
        
        
        html.Div(
            id = 'choosCalc',
            children=[
            html.P(
                r"Choose the type of calcluation you want. Note that analytical calculation are only for"
                " the spin degenerate case. Numerical calculation can take few second.",
                id = 'TexBox',
                ),
            dcc.Checklist(            
                # className="checklist orange",
                id = 'calc',
                options=[
                    {"label": "Analytical calculation  ", "value": "an"},
                    {"label": "Numerical calculation", "value": "nu"},
                    ],
                value=["an"],
                ),]
            ),
        html.Div(
            className = "graph",
            children = [
                html.H4('Density of states'),
                dcc.Graph(id="vardens-graph")]),
        html.Div(
            className="grid-x",
            children=[
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        dcc.Markdown(
                            dangerously_allow_html=True,
                            children=dedent(
                                "Chose the electron density of your 2DEG in m<sup>-2</sup>:"
                                )),
                        dcc.Slider(
                            id="nelec",
                            min=0,
                            max=1e16,
                            marks={
                                i: "{:.1E}".format(i)
                                for i in range(0, int(1.1e16), int(2e15))
                            },
                            value=3e15,
                            step=1e14,
                        ),
                    ],
                ),
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        dcc.Markdown(
                            r"Energy broadening of Landau levels by disorder in Kelvin"
                        ),
                        dcc.Slider(
                            id="gamma",
                            min=0.5,
                            max=30,
                            value=5,
                            marks={i: "{}".format(i) for i in range(0, 31, 5)},
                            step=1 / 10,
                        ),
                    ],
                ),
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        dcc.Markdown(r"Constant density broadening %"),
                        dcc.Slider(
                            id="Xi",
                            min=0,
                            max=100,
                            value=10,
                            marks={i: "{}".format(i) for i in range(0, 101, 20)},
                            step=1 ,
                        ),
                    ],
                ),
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        dcc.Markdown(r"Disorder type"),
                        dcc.Dropdown(
                            id="GL",
                            options=[
                                {"label": "Gaussian", "value": "1"},
                                {"label": u"Lorentzian", "value": "0"},
                            ],
                            value="0",
                        ),
                    ],
                ),
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        dcc.Markdown(r"Choose the x axis:"),
                        dcc.RadioItems(
                            id="Bfstyle",
                            options=[
                                {"label": "Magnetic field  ", "value": "Bf"},
                                {"label": u"inverse magnetic field", "value": "B1f"},
                            ],
                            value="Bf",
                        ),
                    ],
                ),
                
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        html.Label(
                            r"At what magnetic field (Tesla) do you see spin splitting? This is for"
                                " computing the exchange term of Zeeman splitting. (works only with numerical calculation)"
                            ),
                        dcc.Input(id="Bsplit", value=0,),
                        
            ]
                        ),
                
            ],
        ),
        
       
        html.Div(
            className='graph',
            children = [
                 html.Button(
                    id="gocal",
                    className="checklist",
                    children="Start thermodynamic grand potential and Magnetization calculation "
                    
                   
                    ),
               
                dcc.Graph(id="GranPot-graph", figure=go.Figure(data=[], layout=figure_layout)),
                html.H4('Grand thermodynamic potential'),
                dcc.Graph(id="Mag-graph", figure=go.Figure(data=[], layout=figure_layout)),
                html.H4('Magnetization'),
            ]
        ),
        
        
        
        html.Div(
            children = [
            html.Label(
            r"The source code of the app and functions to perform calculations are available on Github:"
            ),
            dcc.Link('https://github.com/Keyanb/MagQHE',
                     href = "https://github.com/Keyanb/MagQHE"
        )])
    ]
)



@app.callback(
    Output("vardens-graph", "figure") 
    ,[Input("nelec", "value"),
     Input("gamma", "value"),
     Input("Xi", "value"),
     Input("GL", "value"),
     Input("calc", "value"),
     Input("Bsplit", "value"),
     Input("Bfstyle", "value")])

def update_graph(nel, gam, Xi, GLo, cal, bsp, bfs):
    gEA = Ma.gEA(ns=nel, Gam=gam * k.k, Xi=float(Xi)/100, GL=int(GLo))
    dfA["DOSA"] = gEA
    fi = []
    ca = []
    na = {"DOSA": "Analytical", "DOSC": "Numerical" }
    if isin("an", cal):
        ca.append("DOSA")        
    if isin("nu", cal):
        g = Mc.gESS(ns=nel, Gam=gam * k.k, Xi=float(Xi)/100, GL=int(GLo), Bs=float(bsp))
        dfA["DOSC"] = g[shape(g)[0] // 2]
        ca.append("DOSC")
    if bfs == "Bf":
        dfA["Bfield"] = Ma._B
        fi = "B(Tesla)"
    else:
        dfA["Bfield"] = 1 / Ma._B
        fi = "1/B(1/Tesla)"
    figure = {
        "data": [
            dict(
                x=dfA["Bfield"],
                y=dfA[i],
                text= na[i],
                marker={
                    "size": 15,
                    "opacity": 0.5,
                    "line": {"width": 0.5, "color": "white"},
                },
                name=na[i]
            )
            for i in ca
        ],
        "layout": dict(
            xaxis={"title": fi},
            yaxis={"title": "DOS"},
            
        )
    }
    
    return figure


@app.callback([dash.dependencies.Output("Mag-graph", "figure"),
    Output("GranPot-graph", "figure")],
    [
        Input("calc", "value"),
        Input("Bfstyle", "value"),
        Input("gocal", "n_clicks"),
        Input("nelec", "value"),
        Input("gamma", "value"),
        Input("Xi", "value"),
        Input("GL", "value"),
        Input("Bsplit", "value"),
    ],
    [dash.dependencies.State("GranPot-graph", "figure"), 
     dash.dependencies.State("Mag-graph", "figure")]
)
def update_graph2(cal, bfs, n_click, ne, gam, xi, gl, bs, fig1, fig2):
    co = []
    cm = []
    fi = []
    na = {"OmegaA": "Analytical", "OmegaC": "Numerical" }
    na2 = {"MagnetizationA": "Analytical", "MagnetizationC": "Numerical" }
    # print(g)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if changed_id == "gocal.n_clicks":
        
        if isin("an", cal):
            OmA = Ma.OmegaA(ns = ne, Gam = gam * k.k, Xi=float(xi)/100, GL=int(gl) )
            dfA["OmegaA"] = OmA
            co.append("OmegaA")
            MagA = Ma.MagA()
            dfA["MagnetizationA"] = MagA
            cm.append("MagnetizationA")
        if isin("nu", cal):
            OmC = Mc.OmegaC(ns = ne, Gam = gam * k.k, Xi=float(xi)/100, GL=int(gl), Bs = bs)
            dfA["OmegaC"] = OmC
            co.append("OmegaC")
            MagC = Mc.MagC()
            MagC = np.append(MagC, MagC[-1])
            dfA["MagnetizationC"] = MagC
            cm.append("MagnetizationC")
        if bfs == "Bf":
            dfA["Bfield"] = Ma._B
            fi = "B(Tesla)"
        else:
            dfA["Bfield"] = 1 / Ma._B
            fi = "1/B(1/Tesla)"
         
    else:
        raise PreventUpdate
    fig1.update({
        "data": [
            dict(
                x=dfA["Bfield"],
                y=dfA[i],
              
                marker={
                    "size": 15,
                    "opacity": 0.5,
                    "line": {"width": 0.5, "color": "white"},
                },
                name=na[i]
            )
            for i in co
        ],
        "layout": dict(
            xaxis={"title": fi},
            yaxis={"title": "Grand Thermodynamic Potential"},
            **figure_layout
        ),
     })
    fig2.update({
           "data": [
                dict(
                    x=dfA["Bfield"],
                    y=dfA[i],
                    marker={
                        "size": 15,
                        "opacity": 0.5,
                        "line": {"width": 0.5, "color": "white"},
                    },
                    name=na2[i]
                )
                for i in cm
            ],
            "layout": dict(
                xaxis={"title": fi},
                yaxis={"title": r"Magnetisation"},
            ),
        })

    return fig2, fig1


#


# @app.callback(
#     Output('my-div', 'children'),
#     [Input('denos', 'data')]
# )
# def update_output_div(input_value):
#     print(input_value)
#     return 'value "{}"'.format(input_value)



if __name__ == "__main__":
    app.run_server(debug=False)
