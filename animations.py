import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd



dataFrame = pd.read_csv("./COW_Trade_4.0/COW_Trade_4.0/National_COW_4.0.csv")
dataFrame.drop(['alt_imports', 'alt_exports', 'source1', 'source2', 'version'],axis='columns', inplace=True)

c_codes = dataFrame["ccode"].unique()
c_data = dataFrame.loc[:, ['statename','stateabb','ccode']].drop_duplicates()
c_data.set_index("ccode",drop= True, inplace=True)

countries = c_data.to_dict(orient="index")

df = dataFrame



animations = {
    'Scatter': px.scatter(df, x="imports", y="exports", animation_frame="year", animation_group="statename", hover_name="statename")
}

app = dash.Dash(__name__)


app.layout = html.Div([
    html.P("Select an animation:"),
    dcc.RadioItems(
        id='selection',
        options=[{'label': x, 'value': x} for x in animations],
        value='Scatter'
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"), 
    [Input("selection", "value")])
def display_animated_graph(s):
    return animations[s]


if __name__ == "__main__":
    app.run_server(debug=True)
