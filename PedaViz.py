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
       
        
        # html.Div(
        #     [
        #         html.Button(
        #             id="gocal",
        #             className="checklist",
        #             children="Start thermodynamic grand potential calculation "
                    
                   
        #             )
        #     ]
        # ),
        html.Div(
            className='graph',
            children = [
                 html.Button(
                    id="gocal",
                    className="checklist",
                    children="Start thermodynamic grand potential calculation "
                    
                   
                    ),
                dcc.Graph(id="GranPot-graph", figure=go.Figure(data=[], layout=figure_layout)),
                # dcc.Graph(
                #     id = 'Granpot-graphC'),
                html.Button(
                    id="gocal2",
                    className="checklist",
                    children="Start Magnetization Calculation (only after grand potential has been calculated)"
                ),
                dcc.Graph(id="Mag-graph", figure=go.Figure(data=[], layout=figure_layout)),
            ]
        ),
        # html.Div([
        #     html.Div(id='my-div') ])
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
    dash.dependencies.Output("vardens-graph", "figure"),
    [
        dash.dependencies.Input("nelec", "value"),
        dash.dependencies.Input("gamma", "value"),
        dash.dependencies.Input("Xi", "value"),
        dash.dependencies.Input("GL", "value"),
        dash.dependencies.Input("calc", "value"),
        dash.dependencies.Input("Bsplit", "value"),
        dash.dependencies.Input("Bfstyle", "value"),
    ],
)
def update_graph(nel, gam, Xi, GLo, cal, bsp, bfs):
    gEA = Ma.gEA(ns=nel, Gam=gam * k.k, Xi=float(Xi)/100, GL=int(GLo))
    dfA["DOSA"] = gEA
    ca = []
    na = {"DOSA": "Analytical", "DOSC": "Numerical" }
    if isin("an", cal):
        ca.append("DOSA")        
    if isin("nu", cal):
        g = Mc.gESS(ns=nel, Gam=gam * k.k, Xi=float(Xi)/100, GL=int(GLo), Bs=float(bsp))
        print(Xi)
        dfA["DOSC"] = g[shape(g)[0] // 2]
        ca.append("DOSC")
    if bfs == "Bf":
        dfA["Bfield"] = Ma._B
        fi = "B(Tesla)"
    else:
        dfA["Bfield"] = 1 / Ma._B
        fi = "1/B(1/Tesla)"
    return {
        "data": [
            dict(
                x=dfA["Bfield"],
                y=dfA[i],
                text= i,
                # customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                # mode='markers',
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
            
        ),
    }


@app.callback(
    dash.dependencies.Output("GranPot-graph", "figure"),
    [
        dash.dependencies.Input("calc", "value"),
        dash.dependencies.Input("Bfstyle", "value"),
        dash.dependencies.Input("gocal", "n_clicks"),
    ],
    [dash.dependencies.State("GranPot-graph", "figure")]
)
def update_graph2(cal, bfs, n_click, fig):
    co = []
    na = {"OmegaA": "Analytical", "OmegaC": "Numerical" }
    if n_click is not None:
        if isin("an", cal):
            OmA = Ma.OmegaA()
            # dfA = pd.DataFrame({'OmegaA': OmA})
            dfA["OmegaA"] = OmA
            co.append("OmegaA")
        if isin("nu", cal):
            OmC = Mc.OmegaC()
            print(Mc._GL)
            dfA["OmegaC"] = OmC
            co.append("OmegaC")
        if bfs == "Bf":
            dfA["Bfield"] = Ma._B
            fi = "B(Tesla)"
        else:
            dfA["Bfield"] = 1 / Ma._B
            fi = "1/B(1/Tesla)"
    # else:
    #     raise PreventUpdate
    fig.update({
        "data": [
            dict(
                x=dfA["Bfield"],
                y=dfA[i],
                # text = 'bou',
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

    return fig


@app.callback(
    dash.dependencies.Output("Mag-graph", "figure"),
    [
        dash.dependencies.Input("calc", "value"),
        dash.dependencies.Input("Bfstyle", "value"),
        dash.dependencies.Input("gocal2", "n_clicks"),
    ],
    [dash.dependencies.State("Mag-graph", "figure")]
)
def update_graph3(cal, bfs, n_click, fig):
    ctx = dash.callback_context
    # if ctx.triggered:
    #     prop_id = ctx.triggered[0]['prop_id']
    #     print(prop_id)

    cm = []
    na = {"MagnetizationA": "Analytical", "MagnetizationC": "Numerical" }
    if n_click is not None:
        if isin("an", cal):
            MagA = Ma.MagA()
            dfA["MagnetizationA"] = MagA
            cm.append("MagnetizationA")
        if isin("nu", cal):
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

        fig.update({
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
                for i in cm
            ],
            "layout": dict(
                xaxis={"title": fi},
                yaxis={"title": r"Magnetisation"},
            ),
        })

    return fig


# @app.callback(
#     Output(component_id='my-div', component_property='children'),
#     [Input(component_id='GL', component_property='value')]
# )
# def update_output_div(input_value):
#     return 'value "{}"'.format(input_value)


if __name__ == "__main__":
    app.run_server(debug=False)
