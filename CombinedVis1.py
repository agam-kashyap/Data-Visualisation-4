import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from inspect import trace
import plotly.graph_objects as go
import numpy as np

df_trades = pd.read_csv("./COW_Trade_4.0/COW_Trade_4.0/Dyadic_COW_4.0.csv")

df_trades['PathName'] = df_trades['importer1'] + "_" + df_trades['importer2']

year = 2000

df_countries = pd.read_csv("./COW_Trade_4.0/COW_Trade_4.0/National_COW_4.0.csv")


app = dash.Dash(__name__,
                # external_stylesheets=external_stylesheets,
                title="Trade Data")

app.layout = html.Div([
    # html.Div(
    #     className='app-header',
    #     children=[
    #         html.Div('National Trade View', className="app-header--title")
    #     ]
    # ),
    html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='property',
                        options = [{'label':'imports', 'value': 'imports'}, {'label':'exports', 'value':'exports'}],
                        value='imports'
                    ),
                    dcc.Graph(
                        id='NationalBubbleChart'
                    )
                ])
            ],
            className="twelve columns")
        ],
        className="row"
    ),
    html.Div([
        dcc.RangeSlider(
            id='year-range-slider',
            min=1870,
            max=2010,
            step=1,
            value=[1970, 2000],
            allowCross=False,
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ]),
    html.Div([
        dcc.Graph(
            id='dualBarPlot'
        )
    ],
        className="row"
    )
],
className="container")



@app.callback(
    Output('NationalBubbleChart', 'figure'),
    [Input('year-range-slider', 'value'),
    Input('property','value')])
def update_graph(year, property):
    df_new_countries = df_countries[(df_countries['year'] >= year[0]) & (df_countries['year'] <= year[1])].copy()
    df_new_countries = df_new_countries[df_new_countries[property].notna()].copy()
    
    series_temp = df_new_countries.groupby(['statename', property])[property].sum().groupby(['statename']).sum().copy()
    df_temp = pd.DataFrame({'statename': series_temp.index, property: series_temp.values})
    
    # Formula for what the Cirles should represent using the National COW 
    sizes = df_temp[property].copy()
    sizes = 2 + sizes/df_temp[property].max() * 50

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
                        locationmode = 'country names',
                        locations = df_temp['statename'],
                        text = df_temp[property].to_numpy(),
                        mode = 'markers',
                        marker = dict(
                            size = np.array(sizes) ,
                            color = 'rgb(255, 0, 0)'
                        )))
    
    fig.update_layout(
        geo=dict(
            showcountries=True,
        ),
        height=500,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig


@app.callback(
    Output('dualBarPlot', 'figure'),
    Input('NationalBubbleChart','clickData')
)
def update(clickdata):
    countryName = clickdata['points'][0]['location']
    df_new_countries = df_countries[df_countries['statename']==countryName].copy()
    df_new_countries[pd.isna(df_new_countries["imports"])]=0

    timePeriod = [i+ 1870 for i in range(2010-1870)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=timePeriod, y = df_new_countries['imports']))
    fig.add_trace(go.Bar(x=timePeriod, y = -1*df_new_countries['exports']))
    
    return fig




if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True, port="8080")   