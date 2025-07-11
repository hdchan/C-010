from dash import Dash, dcc, html, dash_table, Input, Output, State, callback

import base64
import datetime
import io

import pandas as pd
import plotly.express as px
external_stylesheets = ['./bWLwgP.css']

# Incorporate data
df = pd.read_csv('./Standings-tournament-194241(1).csv')
# test = df['Decklists1DecklistName'].str.split('-')
selected_columns = df[['TeamPlayers1DisplayName', 'Points', 'GameCount', 'GameDraws', 'GameLosses', 'GameWins', 'MatchCount', 'MatchDraws', 'MatchLosses', 'MatchWins', 'Decklists1DecklistName']]
selected_columns['Decklists1DecklistName'].fillna('Empty - Empty', inplace=True)
selected_columns[['Leader', 'Base']] = selected_columns['Decklists1DecklistName'].str.split(' - ', n=1, expand=True)
app = Dash(__name__, external_stylesheets=external_stylesheets)


meta_grouping = {
    'Aggro': [
        'Sabine Wren, Galvanized Revolutionary',
        'Leia Organa, Alliance General'
    ],
    'Soft Control': [
        'Darth Vader, Dark Lord of the Sith',
        'Kylo Ren, Rash and Deadly',
    ],
    'Midrange': [
        'Iden Versio, Inferno Squad Commander',
        'Rey, More Than A Scavenger',
        'Hera Syndulla, Spectre Two'
    ],
    'Tempo': []
}

def getquotetoday(val):
    for idx, key in enumerate(meta_grouping):
        if val in meta_grouping[key]:
            return key
    return 'other'

selected_columns['meta_group'] = selected_columns['Leader'].apply(getquotetoday)

group_by_base_wins = selected_columns.groupby('Base').sum()

unique_leaders = pd.DataFrame({'Leader': selected_columns['Leader'].unique()})
unique_bases = pd.DataFrame({'Base': selected_columns['Base'].unique()})

grouped_data = selected_columns.groupby('meta_group')

category_aggregations = {
    'GameCount': 'sum',
    'GameWins': 'sum',
    'MatchCount': 'sum',
    'MatchWins': 'sum'
}
aggregated_df = selected_columns.groupby('meta_group', as_index=False).agg(category_aggregations)
aggregated_df['WinRate'] = (aggregated_df['GameWins'] / aggregated_df['GameCount'] * 100).astype(int)
# aggregated_df[['Leader']] = grouped_data[['Leader']]
user_defined_categoes = pd.DataFrame(list(meta_grouping.keys()))
category_count = grouped_data['meta_group'].count()

for i in meta_grouping.keys():
    if category_count.index.isin([i]).any() == False:
        category_count = pd.concat([category_count, pd.Series([0], index=[i], name=category_count.name)])

# df2 = pd.DataFrame({'Animal': ['Falcon', 'Falcon',

#                               'Parrot', 'Parrot'],

#                    'Max Speed': [380., 370., 24., 26.]})
# testing = df2.groupby(['Animal']).mean()
app.layout = html.Div([
    # dcc.Upload(
    #     id='upload-data',
    #     children=html.Div([
    #         'Drag and Drop or ',
    #         html.A('Select Files')
    #     ]),
    #     style={
    #         'width': '100%',
    #         'height': '60px',
    #         'lineHeight': '60px',
    #         'borderWidth': '1px',
    #         'borderStyle': 'dashed',
    #         'borderRadius': '5px',
    #         'textAlign': 'center',
    #         'margin': '10px'
    #     },
    #     # Allow multiple files to be uploaded
    #     multiple=True
    # ),
    # html.Div(id='output-data-upload'),
    # html.H1("hi"),
    # https://stackoverflow.com/questions/48082138/is-it-possible-to-disable-the-zoom-pan-window-on-a-plotly-py-candlestick-chart
    
    dcc.Graph(figure=px.bar(group_by_base_wins, x=group_by_base_wins.index, y='GameWins'), config={'displayModeBar': False}),
    dcc.Graph(figure=px.histogram(selected_columns, x='Leader', y='GameWins', barmode='group').update_xaxes(categoryorder="sum descending")),
    dcc.Graph(figure=px.bar(category_count, x='meta_group', y=category_count.index)),
    # dash_table.DataTable(data=unique_leaders.to_dict('records')),
    # dash_table.DataTable(data=unique_bases.to_dict('records')),
    dash_table.DataTable(data=selected_columns.to_dict('records')),
    dash_table.DataTable(data=aggregated_df.to_dict('records')),
    dcc.Graph(figure=px.line_polar(aggregated_df, r='WinRate', theta='meta_group', line_close=True, range_r=[0, 100]))
    # dash_table.DataTable(data=grouped_data.to_dict('records'))
    # html.Div(id='output-data-upload')
])

# @callback(
#     Output(component_id='controls-and-graph', component_property='figure'),
#     Input(component_id='controls-and-radio-item', component_property='value')
# )
# def update_graph(col_chosen):
#     fig = px.histogram(df, x='continent', y=col_chosen, histfunc='avg')
#     return fig

# def parse_contents(contents, filename, date):
#     content_type, content_string = contents.split(',')

#     decoded = base64.b64decode(content_string)
#     try:
#         if 'csv' in filename:
#             # Assume that the user uploaded a CSV file
#             df = pd.read_csv(
#                 io.StringIO(decoded.decode('utf-8')))
#         elif 'xls' in filename:
#             # Assume that the user uploaded an excel file
#             df = pd.read_excel(io.BytesIO(decoded))
#     except Exception as e:
#         print(e)
#         return html.Div([
#             'There was an error processing this file.'
#         ])

#     return html.Div([
#         html.H5(filename),
#         html.H6(datetime.datetime.fromtimestamp(date)),

#         dash_table.DataTable(
#             df.to_dict('records'),
#             [{'name': i, 'id': i} for i in df.columns]
#         ),

#         html.Hr(),  # horizontal line

#         # For debugging, display the raw contents provided by the web browser
#         html.Div('Raw Content'),
#         html.Pre(contents[0:200] + '...', style={
#             'whiteSpace': 'pre-wrap',
#             'wordBreak': 'break-all'
#         })
#     ])

# @callback(Output('output-data-upload', 'children'))

# def update_output():
#     return "test"

# @callback(Output('output-data-upload', 'children'),
#               Input('upload-data', 'contents'),
#               State('upload-data', 'filename'),
#               State('upload-data', 'last_modified'))
# def update_output(list_of_contents, list_of_names, list_of_dates):
#     if list_of_contents is not None:
#         children = [
#             parse_contents(c, n, d) for c, n, d in
#             zip(list_of_contents, list_of_names, list_of_dates)]
#         return children

if __name__ == '__main__':
    app.run(debug=True)
