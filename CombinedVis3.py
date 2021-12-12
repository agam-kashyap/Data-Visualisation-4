import dash
from dash import dcc
from dash import html
from dash.dcc.Dropdown import Dropdown
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from inspect import trace
import plotly.graph_objects as go
import numpy as np

dataFrame = pd.read_csv("./COW_Trade_4.0/COW_Trade_4.0/National_COW_4.0.csv")
dataFrame.drop(['alt_imports', 'alt_exports', 'source1', 'source2', 'version'],axis='columns', inplace=True)
dataFrame["imports"].fillna(1,inplace= True)
dataFrame["exports"].fillna(1, inplace = True)

# World War 2 countries


app = dash.Dash(__name__, title="World War")

app.layout = html.Div([
    html.P("Select the Forces"),
    dcc.Dropdown(
        id="forces",
        options=[{"label": x, "value": x} 
                 for x in ["Allied", "Axis"]],
        value="Allied"
    ),
    html.P("Select World War Year"),
    dcc.Dropdown(
        id="wwyear",
        options=[{"label": x, "value": x} 
                 for x in ["1", "2"]],
        value="1"
    ),
    dcc.Graph(id="ww")
])

@app.callback(
    Output("ww", "figure"), 
    Input("forces", "value"),
    Input("wwyear","value"))
def update_chart(force, year):
    alliedForces = []
    axisForces = []
    if(year==2):
        alliedForces = ["France", "United Kingdom", "Russia", "United States of America"]
        axisForces = ["Germany", "Italy", "Japan"]
    else:
        alliedForces = ["France", "United Kingdom", "Russia", "Italy", "Japan", "United States of America"]
        axisForces = ["Germany","Austria-Hungary", "Ottoman","Bulgaria"]
    
    if(force=="Allied"): df = dataFrame[dataFrame['statename'].isin(alliedForces)].copy()
    else : df = dataFrame[dataFrame['statename'].isin(axisForces)].copy()

    df["Log_imports"] = np.log2(df["imports"]).copy()
    df["Log_exports"] = np.log2(df["exports"]).copy()

    fig = px.scatter(df, x="Log_imports", y="Log_exports", animation_frame="year", animation_group="statename", hover_name="statename" , text = "statename" )
    return fig

app.run_server(debug=True, port="8090")