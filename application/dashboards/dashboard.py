from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html

colors = {
        'background': '#FFFFFF',
        'text': '#7FDBFF'
    }

def create_app(server_app):


    app = dash.Dash(
        server=server_app,
        routes_pathname_prefix='/dashboard/'
    )

    app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

        html.H1(
            children='Aplikacja raportowa',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        dcc.Dropdown(
            id='agg_picker',
            options=[
                {'label': 'Warszawa', 'value': 'WWA'},
                {'label': 'Kraków', 'value': 'KRK'},
                {'label': 'Łódź', 'value': 'LDZ'}
            ]
        ),

        dcc.DatePickerRange(
            id='date_picker',
            min_date_allowed=date(2019, 1, 1),
            max_date_allowed=date(2023, 12, 31)
        ),

        html.Div(children='', style={
            'textAlign': 'center',
            'color': colors['text']
        }),



        dcc.Graph(
            id='Graph1',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    }
                }
            })




    ])

    return app


def update_app():
    pass