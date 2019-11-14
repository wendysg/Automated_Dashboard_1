import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import base64
import io
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

app.layout = html.Div([
                # adding a header and a paragraph
                 html.Div([
                           html.H1("Automatic Insight Generator"),
                           html.P("ALY6080 XN Project")
                          ],
                     style = {'padding' : '25px' ,
                             'backgroundColor' : '#3aaab2'}),
               # adding a upload object
                html.Div([
                     dcc.Upload(
                            id='upload_data',
                            children=html.Div([
                                 'Drag and Drop or ',
                                 html.A('Select Files')
                            ]),
                            style={
                                 'width': '100%',
                                 'height': '60px',
                                 'lineHeight': '60px',
                                 'borderWidth': '1px',
                                 'borderStyle': 'dashed',
                                 'borderRadius': '5px',
                                 'textAlign': 'center',
                                 'margin': '10px'
                            }
                        )
                 ],
                 style={'width':'100%',
                        'display': 'flex',
                        'align-items':'center',
                        'justify-content':'center'
                        }
                ),
             # adding a graph object
               dcc.Graph(id='mygraph'),
             # adding an insight object
               html.Div([
                     html.Pre(
                           id='insight',
                           children='Insights from data:'
                        )
              ],
              style={
                   'fontSize':20,
                   'color':'blue'
                   }
            ),
           # Hidden div inside the app that stores the intermediate value
              html.Div(id='intermediate-value', style={'display': 'none'})
])


@app.callback(
            Output('intermediate-value','children'),
            [Input('upload_data','contents')]
)
def process_data(contents):
    if contents is not None:
        type,data  = contents.split(',')
        decoded = base64.b64decode(data)

        dataset = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
        dataset = dataset.to_json(orient='split', date_format='iso')
        return json.dumps(dataset)

    else:
        return None

@app.callback(
            Output('mygraph','figure'),
            [Input('intermediate-value','children')]
)
def update_graph(json_data):
    if json_data is not None:
        dataset = json.loads(json_data)
        df = pd.read_json(dataset, orient='split')

        traces = []
        for source_name in df['source'].unique():
            df_by_source = df[df['source'] == source_name]
            traces.append(go.Scatter(
                    x=df_by_source['month'],
                    y=df_by_source['net_sentiment'],
                    text=df_by_source['net_sentiment'],
                    mode='lines+markers',
                    opacity=0.7,
                    marker={'size': 15},
                    name=source_name
                    ))

        return {
                'data': traces,
                'layout': go.Layout(
                            xaxis={'title': 'Time of the Year'},
                            yaxis={'title': 'Net Sentiment Count'},
                            hovermode='closest',
                            plot_bgcolor=colors["graphBackground"],
                            paper_bgcolor=colors["graphBackground"]
                            )
                    }

    else:
        return {
                'data':[]
                }

@app.callback(
            Output('insight','children'),
            [Input('intermediate-value','children')]
)
def update_insight(json_data):
    if json_data is not None:
        dataset = json.loads(json_data)
        df = pd.read_json(dataset, orient='split')

        source_list = []
        sent_sum = []
        for source_name in df['source'].unique():
            df_by_source = df[df['source'] == source_name]
            total_sent = df_by_source['net_sentiment'].sum()
            sent_sum.append(total_sent)
            source_list.append(source_name)
        summary_df = pd.DataFrame({'source':source_list, 'net_sent_sum':sent_sum})
        max_sum_sent = summary_df['net_sent_sum'].max()
        best_source = summary_df[summary_df['net_sent_sum']==max_sum_sent]['source']

        best_source_df = df[df['source'].values == best_source.values].reset_index(drop=True)
        max_net_sent = best_source_df['net_sentiment'].max()
        best_month = best_source_df[best_source_df['net_sentiment']==max_net_sent]['month']

        return ('Insights from Data:' + '\n' +
                best_source + ' has the highest impact on the brand.' + '\n' +
                'The peak is ' + str(max_net_sent) + ' net sentiments in ' + best_month.values + '.')

    else:
        return 'Insights from Data: Not available'


if __name__ == '__main__':
    app.run_server(debug=True)
