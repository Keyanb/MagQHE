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


available_indicators = ["Grand potential", "Magnetization"]

app.layout = html.Div(
    children=[
        html.H1(children="Magnetization in Quantum Hall regime"),
        html.Div(
            children="""
        App to calculate magnetization in Quantum Hall regime
    """
        ),
        html.Label(
            r"The source code of the app and function to perform calculation is available on Git: https://github.com/Keyanb/MagQHE"
        ),
        html.Label(
            r"Choose the type of calcluation you want. Note that anlytical calculation are only for"
            "the spin degenerate case. Numerical calculation can take few second. Both can be selected"
        ),
        dcc.Checklist(
            id="calc",
            className="checklist orange",
            options=[
                {"label": "Analytical calculation  ", "value": "an"},
                {"label": "Numerical calculation", "value": "nu"},
            ],
            value=["an"],
        ),
        html.Div([dcc.Graph(id="vardens-graph")]),
        html.Div(
            className="grid-x",
            children=[
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        html.Label(
                            r"Chose the electron density of your 2DEG in $m^{-2}$:"
                        ),
                        dcc.Slider(
                            id="nelec",
                            min=0,
                            max=1e16,
                            marks={
                                i: "{:.1E}".format(i)
                                for i in range(0, int(1e16), int(1e15))
                            },
                            value=3e15,
                            step=1e14,
                        ),
                    ],
                ),
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        html.Label(
                            r"Energy broadening of Landau levels by disorder in Kelvin"
                        ),
                        dcc.Slider(
                            id="gamma",
                            min=0.5,
                            max=40,
                            value=5,
                            marks={i: "{}".format(i) for i in range(0, 50, 5)},
                            step=1 / 10,
                        ),
                    ],
                ),
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        html.Label(r"Constant density broadening %"),
                        dcc.Slider(
                            id="Xi",
                            min=0,
                            max=1,
                            value=0.1,
                            marks={i: "{:.2E}".format(i) for i in range(0, 100, 10)},
                            step=1 / 50,
                        ),
                    ],
                ),
                html.Div(
                    className="cell small-12 medium-6",
                    children=[
                        html.Label(r"Disorder type"),
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
                        html.Label(r"x axis:"),
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
                            r"At what magnetic field (Tesla) do you see spin splitting? (to compute de exange enhencement of Zeeman splitting)"
                            ),
                        dcc.Input(id="Bsplit", value=0,),
                        
            ]
                        ),
                
            ],
        ),
        # html.Div([
        #     html.Label(r'Density of state calculated numerically (allow spin splitting'),
        #     dcc.Graph(
        #         id='density-graph') ]),
        #     html.H1('Progress bar'),
        # dbc.Progress(id="progress", value=50, striped=True, animated=True)]),
        
        html.Div(
            [
                html.Button(
                    id="gocal",
                    className="checklist",
                    children="Start thermodynamic grand potential calculation "
                    
                   
                    )
            ]
        ),
        html.Div(
            [
                dcc.Graph(id="GranPot-graph"),
                # dcc.Graph(
                #     id = 'Granpot-graphC'),
                html.Button(
                    id="gocal2",
                    className="checklist",
                    children="Start Magnetization Calculation (only after grand potential has been calculated)"
                ),
                dcc.Graph(id="Mag-graph", figure=go.Figure(data=[], layout=figure_layout)),
            ]
        )
        # html.Div([
        #     html.Div(id='my-div') ])
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
    gEA = Ma.gEA(ns=nel, Gam=gam * k.k, Xi=float(Xi), GL=int(GLo))
    dfA["DOSA"] = gEA
    ca = []
    if isin("an", cal):
        ca.append("DOSA")
    if isin("nu", cal):
        g = Mc.gESS(ns=nel, Gam=gam * k.k, Xi=float(Xi), GL=int(GLo), Bs=float(bsp))
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
                # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                # customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                # mode='markers',
                marker={
                    "size": 15,
                    "opacity": 0.5,
                    "line": {"width": 0.5, "color": "white"},
                },
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
    ]
)
def update_graph2(cal, bfs, n_click):
    co = []
    if n_click is not None:
        if isin("an", cal):
            OmA = Ma.OmegaA()
            # dfA = pd.DataFrame({'OmegaA': OmA})
            dfA["OmegaA"] = OmA
            co.append("OmegaA")
        if isin("nu", cal):
            OmC = Mc.OmegaC()
            dfA["OmegaC"] = OmC
            co.append("OmegaC")
        if bfs == "Bf":
            dfA["Bfield"] = Ma._B
            fi = "B(Tesla)"
        else:
            dfA["Bfield"] = 1 / Ma._B
            fi = "1/B(1/Tesla)"
    else:
        raise PreventUpdate
    return {
        "data": [
            dict(
                x=dfA["Bfield"],
                y=dfA[i],
                # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                # customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                # mode='markers',
                marker={
                    "size": 15,
                    "opacity": 0.5,
                    "line": {"width": 0.5, "color": "white"},
                },
            )
            for i in co
        ],
        "layout": dict(
            xaxis={"title": fi},
            yaxis={"title": "Grand Thermodynamic Potential"},
            **figure_layout
        ),
    }


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
    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id']
        print(prop_id)



    cm = []
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
                    # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    # customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    # mode='markers',
                    marker={
                        "size": 15,
                        "opacity": 0.5,
                        "line": {"width": 0.5, "color": "white"},
                    },
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
