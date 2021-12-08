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



# data prcessing for country data 

df_countries = pd.read_csv("./COW_Trade_4.0/COW_Trade_4.0/National_COW_4.0.csv")
df_countries.drop(['alt_imports', 'alt_exports', 'source1', 'source2', 'version'],axis='columns', inplace=True)

df_countries.columns
df_countries["imports"].fillna(1,inplace= True)
df_countries["exports"].fillna(1, inplace = True)

c_codes = df_countries["ccode"].unique()
c_data = df_countries.loc[:, ['statename','stateabb','ccode']].drop_duplicates()
c_data.set_index("ccode",drop= True, inplace=True)
countries = c_data.to_dict(orient="index")

df_countries["Log_imports"] = np.log2(df_countries["imports"])
df_countries["Log_exports"] = np.log2(df_countries["exports"])

def changeCountry(countryName,df_countries):
    data = df_countries.loc[df_countries["statename"] == countryName]
    raw_data = data.loc[:, ['year','imports','exports']]
    return raw_data

def getCountryName(countryCode):
    return countries[countryCode]["statename"]

def plotTradeDef(countryName):
    raw_data = changeCountry(countryName,df_countries)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=raw_data['year'], y=raw_data['imports']*-1,
                base=0,
                marker_color='crimson',
                name='imports'))
    fig.add_trace(go.Bar(x=raw_data['year'], y=raw_data['exports'],
                base=0,
                marker_color='green',
                name='exports'
                ))
    fig.add_trace(go.Bar(x=raw_data['year'], y=raw_data['exports'] - raw_data['imports'],
                base=0,
                marker_color='blue',
                name='Trade deficit'
                ))
                
    fig.update_layout(
    title="Trade of "+ countryName,
    xaxis_title="Year",
    yaxis_title="Millions of Dollars",
    legend_title="Quantity")

    return fig


app = dash.Dash(__name__,
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
                    html.Div([
                        dcc.Dropdown(
                            id='property',
                            options = [{'label':'imports', 'value': 'imports'}, {'label':'exports', 'value':'exports'}],
                            value='imports'
                        )
                    ],
                    className="two columns"),
                    html.Div([
                        dcc.Graph(
                            id='NationalBubbleChart'
                        )
                    ],
                    className="ten columns")                    
                ])
            ])
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
        height=450,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig


@app.callback(
    Output('dualBarPlot', 'figure'),
    Input('NationalBubbleChart','clickData')
)
def update(clickdata):
    if clickdata==None:
        countryName = "India"
    else:
        countryName = clickdata['points'][0]['location']
    raw_data = changeCountry(countryName,df_countries)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=raw_data['year'], y=raw_data['imports']*-1,
                base=0,
                marker_color='crimson',
                name='imports'))
    fig.add_trace(go.Bar(x=raw_data['year'], y=raw_data['exports'],
                base=0,
                marker_color='green',
                name='exports'
                ))
    fig.add_trace(go.Bar(x=raw_data['year'], y=raw_data['exports'] - raw_data['imports'],
                base=0,
                marker_color='blue',
                name='Trade deficit'
                ))

    fig.update_layout(
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    fig.update_layout(
    title="Trade of "+ countryName,
    xaxis_title="Year",
    yaxis_title="Millions of Dollars",
    legend_title="Quantity")

    fig.update_xaxes(side="top")
    
    return fig




if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True, port="8080")   