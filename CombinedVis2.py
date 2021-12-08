import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from inspect import trace
import plotly.graph_objects as go
import numpy as np

df_dyadic = pd.read_csv("./COW_Trade_4.0/COW_Trade_4.0/Dyadic_COW_4.0.csv")

df_dyadic['PathName'] = df_dyadic['importer1'] + "_" + df_dyadic['importer2']

df_national = pd.read_csv("./COW_Trade_4.0/COW_Trade_4.0/National_COW_4.0.csv")

timePeriod = [i+ 1870 for i in range(2010-1870)]
propertyList = {"Country1 imports from Country2":"flow1", 
                "Country2 imports from Country1":"flow2",
                "Smoothed Total Trade": "smoothtotrade"}
country1_unique = df_dyadic["importer1"].unique()

app = dash.Dash(__name__,
                title="Dyadic Visualisations")

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(
                id="world-map"
            )
        ], className="eight columns"), # World Map View
        html.Div([
            html.Div(
                dcc.Graph(
                    id="top-ten"
                )
            ) # Top 10
        ], className="four columns") 
    ], className="row"),
    html.Div([
        dcc.Slider(
            id='year-selector',
            min=1870,
            max=2010,
            value=1970,
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ],className="row"),
    html.Div([
        html.Div([
            html.P("Select Country 1"),
            html.Div([
                dcc.Dropdown(
                    id='country1',
                    options=[{'label':k, 'value':k} for k in country1_unique],
                    value='India'
                )
            ], className="dropdown"), # Dropdown to select Country one
            html.P("Select the Country 2"),
            html.Div([dcc.Dropdown(
                id='country2'
            )], className="dropdown"),
            html.P("Select Property to Visualise"),
            html.Div([dcc.Dropdown(
                id='property',
                options=[{'label':k, 'value':propertyList[k]} for k in propertyList],
                value='flow1'
            )],className="dropdown")
        ], className="two columns"), # Drop Downs  
        html.Div([
            dcc.Graph(
                id='Line-chart-twoCountries'
            )
        ], className="ten columns"), # Line Chart
    ], className="row")
], className="container")


#---------------------------Setting the World Map Plot----------------------------------
def insert_row(idx, df, df_insert):
    dfA = df.iloc[:idx, ]
    dfB = df.iloc[idx:, ]
    df = dfA.append(df_insert).append(dfB).reset_index(drop = True)
    return df

@app.callback(
    Output('world-map', 'figure'),
    [Input('country1', 'value'),
    Input('property','value'),
    Input('year-selector','value')])
def update_world_map(country1, property, year):
    fig = go.Figure()
    df_trades = df_dyadic[df_dyadic['year'] == year].copy()
    temp_locations = df_trades[df_trades["importer1"] == country1].reset_index().copy()
    final_locations = pd.DataFrame([],columns = df_trades.columns)

    for i in range(len(temp_locations)): 
        to_insert = pd.DataFrame([],columns = df_trades.columns) 
        to_insert_orig = to_insert.append(temp_locations.loc[i])
        to_insert_rev = temp_locations.loc[i].copy()
        temp = to_insert_rev["importer2"]
        to_insert_rev["importer2"] = to_insert_rev["importer1"]
        to_insert_rev["importer1"] = temp
        to_insert_orig = to_insert_orig.append(to_insert_rev)
        final_locations = insert_row(i*2, final_locations, to_insert_orig)

    for i in range(0,len(final_locations) - 2,2):
        item = final_locations.iloc[i:i+2].reset_index()
        max_val = final_locations[final_locations["importer1"] == country1][property].max() + 9
        flow_amt = (item[item["importer1"] == country1][property].values[0] + 9) / max_val
        fig.add_trace(
            go.Scattergeo(
                name=item['importer1'][1],
                locationmode = 'country names',
                locations = item['importer1'],
                mode = 'lines',
                line = dict(width = 1 + flow_amt * 10,color = 'red'),
                opacity = flow_amt
            )
        )
    fig.update_layout(
        geo=dict(
            showcountries=True,
        ),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig

#--------------------------------------Setting the Line Charts-----------------------------------------
@app.callback(
    Output('country2', 'options'),
    Input('country1', 'value'))
def set_country2_countries(selected_country):
    return [{'label':i, 'value':i} for i in df_dyadic.loc[df_dyadic["importer1"]==selected_country]["importer2"].unique()]

@app.callback(
    Output('country2','value'),
    Input('country2','options')
)
def set_country2_values(available_options):
    return available_options[0]['value']

@app.callback(
    Output('Line-chart-twoCountries','figure'),
    Input('country1','value'),
    Input('country2', 'value')
)
def update_line_chart(importer1, importer2):
    df = df_dyadic.loc[(df_dyadic["importer1"] == importer1) & (df_dyadic["importer2"]==importer2)].copy()
    
    fig = go.Figure(go.Scatter(x=df["year"], y=df['flow1']))
    fig.update_layout(
        xaxis_range=[1870, 2009],
        yaxis_range=[-20000, 60000],
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return fig

#-----------------------Setting the Top Ten Plot---------------------------------------

@app.callback(
    Output('top-ten', 'figure'),
    [Input('country1', 'value'),
    Input('property','value'),
    Input('year-selector','value')])
def update_topten(country1, property, year):
    df_trades = df_dyadic[df_dyadic['year'] == year].copy()
    new_locations = df_trades[df_trades["importer1"] == country1].reset_index().copy()

    bar_graph_values = new_locations.sort_values(by=[property]).copy()[-10:]

    fig = go.Figure(go.Bar(
                x= bar_graph_values[property],
                y= bar_graph_values['importer2'],
                orientation='h'))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)