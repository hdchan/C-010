from dash import Dash, dcc, html, dash_table, Input, Output, State, callback

import base64
import datetime
import io
import json

import pandas as pd
import plotly.express as px
external_stylesheets = ['./bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
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
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    dcc.Textarea(
        id='textarea-example',
        value="""
        {
        "Aggro": [
            "Sabine Wren, Galvanized Revolutionary",
            "Leia Organa, Alliance General"
        ],
        "Soft Control": [
            "Darth Vader, Dark Lord of the Sith",
            "Kylo Ren, Rash and Deadly"
        ],
        "Midrange": [
            "Iden Versio, Inferno Squad Commander",
            "Rey, More Than A Scavenger",
            "Hera Syndulla, Spectre Two"
        ],
        "Tempos": []
        }
        """,
        style={'width': '100%', 'height': 300},
    ),
    html.Div(children=html.Div([
        "Meta player count",
        html.Div(id="meta_player_count")
        ])),
    html.Div(children=html.Div([
        "Meta win rate",
        html.Div(id="meta_win_rate")
        ])),
    html.Div(children=html.Div([
        "Base count",
        html.Div(id="base_count")
        ])),
    html.Div(children=html.Div([
        "Leader count",
        html.Div(id="leader_count")
        ])),
    html.Div(children=html.Div([
        "Meta-Leader breakdown",
        html.Div(id="meta_leader_breakdown")
        ])),
    html.Div(id='output-data-upload')
])

def get_data_frame(contents, filename, date, meta_grouping = None):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            
    except Exception as e:
        print(e)
        return None
    
    selected_columns = df[['TeamPlayers1DisplayName', 'Points', 'GameCount', 'GameDraws', 'GameLosses', 'GameWins', 'MatchCount', 'MatchDraws', 'MatchLosses', 'MatchWins', 'Decklists1DecklistName']]
    selected_columns['Decklists1DecklistName'].fillna('Empty - Empty', inplace=True)
    selected_columns[['Leader', 'Base']] = selected_columns['Decklists1DecklistName'].str.split(' - ', n=1, expand=True)
    selected_columns['meta_group'] = None
    if meta_grouping is not None:
        def getquotetoday(val):
            for idx, key in enumerate(meta_grouping):
                if val in meta_grouping[key]:
                    return key
            return 'other'

        selected_columns['meta_group'] = selected_columns['Leader'].apply(getquotetoday)
    selected_columns['meta_group'].fillna('other', inplace=True)
    selected_columns['temp'] = None
    selected_columns['temp'].fillna(1, inplace=True)
    return selected_columns


def parse_contents(contents, filename, date):
    
    df = get_data_frame(contents, filename, date)
    
    if df is None:
        return html.Div([
            'There was an error processing this file.'
        ])
        
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

def meta_player_count_output(df, meta_grouping):
    grouped_data = df.groupby('meta_group')
    category_count = grouped_data['meta_group'].count()
    
    try:
        for i in meta_grouping.keys():
            if category_count.index.isin([i]).any() == False:
                category_count = pd.concat([category_count, pd.Series([0], index=[i], name=category_count.name)])
    except:
        # nothing
        pass
        
    category_count = category_count.sort_values()
    
    fig = px.bar(category_count, x='meta_group', y=category_count.index)
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return html.Div([
        dcc.Graph(figure=fig, config={'displayModeBar': False})
    ])

def meta_win_rate_output(df, meta_grouping):
    grouped_data = df.groupby('meta_group')
    match_wins = grouped_data['MatchWins'].sum()
    match_count = grouped_data['MatchCount'].sum()
    win_rate = match_wins / match_count * 100
    
    try:
        for i in win_rate.keys():
            if win_rate.index.isin([i]).any() == False:
                win_rate = pd.concat([win_rate, pd.Series([0], index=[i], name=win_rate.name)])
    except:
        # nothing
        pass
        
    win_rate = win_rate.sort_values()
    
    fig = px.bar(win_rate, x=win_rate[0], y=win_rate.index)
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return html.Div([
        dcc.Graph(figure=fig, config={'displayModeBar': False})
    ])

def base_count(df):
    grouped_data = df.groupby('Base')
    base_count = grouped_data['Base'].count()
    
    base_count = base_count.sort_values()
    
    fig = px.bar(base_count, x='Base', y=base_count.index)
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return html.Div([
        dcc.Graph(figure=fig, config={'displayModeBar': False})
    ])

def leader_count(df):
    grouped_data = df.groupby('Leader')
    base_count = grouped_data['Leader'].count()
    
    base_count = base_count.sort_values()
    
    fig = px.bar(base_count, x='Leader', y=base_count.index)
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return html.Div([
        dcc.Graph(figure=fig, config={'displayModeBar': False})
    ])

def meta_leader_breakdown(df, meta_grouping):
    grouped_data = df.groupby('Leader')
    base_count = grouped_data['Leader'].count()
    
    # base_count = base_count.sort_values()
    
    # fig = px.bar(base_count, x='Leader', y=base_count.index)
    fig = px.treemap(df, path=[px.Constant("all"), 'meta_group', 'Leader'], values='temp')
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return html.Div([
        dcc.Graph(figure=fig, config={'displayModeBar': False})
    ])

def table_output(df, contents, filename, date):
    if df is None:
        return html.Div([
            'There was an error processing this file.'
        ])
        
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@callback(Output('meta_player_count', 'children'),
          Output('meta_win_rate', 'children'),
          Output('base_count', 'children'),
          Output('leader_count', 'children'),
          Output('meta_leader_breakdown', 'children'),
          Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              Input('textarea-example', 'value'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(contents, meta_grouping_string, filename, date):
    if contents is not None:
        try:
            meta_grouping = json.loads(meta_grouping_string)
        except ValueError as e:
            meta_grouping = None
            
        df = get_data_frame(contents, filename, date, meta_grouping)
        
        return (meta_player_count_output(df, meta_grouping),
                meta_win_rate_output(df, meta_grouping),
                base_count(df),
                leader_count(df),
                meta_leader_breakdown(df, meta_grouping),
                table_output(df, contents, filename, date))
    return (None, 
            None, 
            None,
            None,
            None,
            None)
        
if __name__ == '__main__':
    app.run(debug=True)