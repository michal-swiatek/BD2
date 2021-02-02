from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import pandas as pd

# from application import cursor

colors = {
        'background': '#FFFFFF',
        'text': '#7FDBFF'
    }

def create_app(server_app, cursor):


    app = dash.Dash(
        server=server_app,
        routes_pathname_prefix='/dashboard/'
    )

    cost_data = pd.DataFrame(get_data_histogram(cursor)).rename(columns={0: 'koszt'})

    fig = px.histogram(cost_data, x="koszt")
    #
    # time_series = px.line(get_data_time_series(cursor), x='data_rozpoczecia', y='koszt')


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


        # dcc.Graph(
        #     id='Graph1',
        #     figure={
        #         'data': [
        #             {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
        #             {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
        #         ],
        #         'layout': {
        #             'plot_bgcolor': colors['background'],
        #             'paper_bgcolor': colors['background'],
        #             'font': {
        #                 'color': colors['text']
        #             }
        #         }
        #     }
        # ),

        dcc.Graph(id="res_cost_histogram", figure=fig),

        dcc.Dropdown(
            id='agg_ts_picker',
            options=[
                {'label': 'Po dniach', 'value': 'day'},
                {'label': 'Po miesiącach', 'value': 'month'},
            ],
            value='day'
        ),

        dcc.Graph(id='avg_res_cost_ts')
    ])


    @app.callback(
        Output("avg_res_cost_ts", "figure"),
        [Input("agg_ts_picker", "value")]
    )
    def display_time_series(value):
        time_series = px.line(get_data_time_series(cursor, group_by_param=value), x='data_rozpoczecia', y='koszt')
        return time_series

    return app


# TODO: move it to another file
def get_data_histogram(cursor):

    cursor.execute("SELECT koszt FROM rezerwacja")
    data = [item[0] for item in cursor.fetchall()]
    cost_data = pd.Series(data=data)
    return cost_data

# TODO: move it to another file
def get_data_avg_res_cost_aggr_geo(cursor):

    cursor.execute("SELECT AVG(KOSZT), miasto.nazwa \
                        FROM rezerwacja \
                        JOIN sala \
                        ON rezerwacja.sala_id = sala.id \
                        JOIN budynek \
                        ON budynek.id = sala.budynek_id \
                        JOIN miasto \
                        ON budynek.miasto_id = miasto.id \
                        GROUP BY miasto.nazwa")



    breakpoint()

# TODO: move it to another file
def get_data_time_series(cursor, group_by_param):

    if group_by_param == 'day':
        grouping = 'day'
        format = "'%d-%m-%Y'"
    elif group_by_param == 'month':
        grouping = 'month'
        format = "'%d-%m-%Y'"

    cursor.execute(f'SELECT DATE_FORMAT(rezerwacja.rozpoczecie, {format}), AVG(rezerwacja.koszt) \
                    FROM rezerwacja \
                    JOIN sala \
                    ON rezerwacja.sala_id = sala.id \
                    JOIN budynek \
                    ON budynek.id = sala.budynek_id \
                    JOIN miasto \
                    ON budynek.miasto_id = miasto.id \
                    GROUP BY {grouping}(rezerwacja.rozpoczecie) \
                    ORDER BY rezerwacja.rozpoczecie;')

    data = [(item[0], item[1]) for item in cursor.fetchall()]
    cost_data = pd.DataFrame(data=data, columns=["data_rozpoczecia", "koszt"])

    return cost_data

def update_app():
    pass