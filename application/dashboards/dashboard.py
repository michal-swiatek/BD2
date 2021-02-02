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
    #
    fig = px.histogram(cost_data, x="koszt")

    top10_df = get_data_count_res_aggr_geo(cursor, top_n=10)
    fig_top_10 = px.bar(top10_df, x='miasto', y='liczba rezerwacji')


    top_firms = get_top_suppliers(cursor)
    top_firms_bar = px.bar(top_firms, x='firma', y='money spent')


    top_spend_comp_fig=None

    # time_series = px.line(get_data_time_series(cursor), x='data_rozpoczecia', y='koszt')


    app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

        html.H1(
            children='Aplikacja raportowa',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),


        html.Div(children='', style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        dcc.Graph(id="res_cost_histogram", figure=fig),

        # dcc.DatePickerRange(
        #     id='date_picker',
        #     min_date_allowed=date(2017, 1, 1),
        #     max_date_allowed=date(2023, 12, 31),
        #     start_date=date(2019, 1, 1),
        #     end_date=date(2020, 1, 1)
        # ),

        dcc.Dropdown(
            id='agg_ts_picker',
            options=[
                {'label': 'Po dniach', 'value': 'day'},
                {'label': 'Po miesiącach', 'value': 'month'},
            ],
            value='day'
        ),

        dcc.Graph(id='avg_res_cost_ts'),

        # dcc.Dropdown(
        #     id='top_n_picker',
        #     options=[ {'label': i, 'value': i} for i in range(5, 50, 5)],
        #     value=10
        # ),

        dcc.Graph(id='count_bar_plot', figure=fig_top_10),

        dcc.Graph(id='money_spent_per_company', figure=top_firms_bar)
    ])

    @app.callback(
        Output("avg_res_cost_ts", "figure"),
        [Input("agg_ts_picker", "value")]
    )
    def display_time_series(value):
        time_series = px.line(get_data_time_series(cursor, group_by_param=value), x='data_rozpoczecia', y='koszt')
        return time_series

    # @app.callback(
    #     Output("count_bar_plot", "figure"),
    #     [Input("top_n_picker", "value")]
    # )
    # def select_top_n(value):
    #     fig_top_n = px.bar(get_data_count_res_aggr_geo(cursor, top_n=value), x='miasto', y='liczba rezerwacji')
    #     return fig_top_n

    # @app.callback(
    #     Output('avg_res_cost_ts', 'figure'),
    #     Input('agg_ts_picker', 'value'),
    #     Input("date_picker", "start_date"),
    #     Input("date_picker", "end_date"),
    #     prevent_initial_callbacks=True
    # )
    # def restrict_date(value, start_date, end_date):
    #     time_series = px.line (
    #         get_data_time_series(cursor, group_by_param=value, start_date=start_date, end_date=end_date),
    #         x='data_rozpoczecia',
    #         y='koszt'
    #     )
    #
    #     return time_series

    return app


def get_top_suppliers(cursor):

    cursor.execute("SELECT firma_cateringowa.nazwa, SUM(pozycja.liczba * produkt_spozywczy.cena) AS total_sum FROM \
                    pozycja JOIN produkt_spozywczy ON pozycja.produkt_spozywczy_id = produkt_spozywczy.id \
                    JOIN firma_cateringowa ON firma_cateringowa.id=produkt_spozywczy.firma_cateringowa_id \
                    GROUP BY firma_cateringowa.nazwa \
                    ORDER BY total_sum DESC;")

    data = cursor.fetchall()

    return pd.DataFrame(data=data, columns=["firma", "money spent"]).head(10)



def get_top_deps_rev(cursor):
    cursor.execute("SELECT SUM(rezerwacja.koszt), komorka_organizacyjna.nazwa FROM rezerwacja \
                    JOIN projekt ON rezerwacja.projekt_id=projekt.id \
                    JOIN komorka_organizacyjna on projekt.komorka_organizacyjna_id=komorka_organizacyjna.id \
                    GROUP BY komorka_organizacyjna.nazwa;")

    data = cursor.fetchall()

    return pd.DataFrame(data=data, columns=["sum", "department"])


# TODO: move it to another file
def get_data_histogram(cursor):

    cursor.execute("SELECT koszt FROM rezerwacja")
    data = [item[0] for item in cursor.fetchall()]
    cost_data = pd.Series(data=data)
    return cost_data

# TODO: move it to another file
def get_data_count_res_aggr_geo(cursor, **kwargs):


    if 'top_n' not in kwargs.keys():
        top_n = 10
    else:
        top_n = kwargs['top_n']

    cursor.execute("SELECT COUNT(*), miasto.nazwa \
                    FROM rezerwacja \
                    JOIN sala \
                    ON rezerwacja.sala_id = sala.id \
                    JOIN budynek \
                    ON budynek.id = sala.budynek_id \
                    JOIN miasto \
                    ON budynek.miasto_id = miasto.id \
                    GROUP BY miasto.nazwa \
                    ORDER BY COUNT(*) DESC;")


    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=['liczba rezerwacji', 'miasto']).head(top_n)

    return df

# TODO: move it to another file
def get_data_time_series(cursor, **kwargs):


    if 'group_by_param' in kwargs.keys() and kwargs['group_by_param'] == 'day':
        grouping = 'day'
        format = "'%d-%m-%Y'"
    elif 'group_by_param' in kwargs.keys() and kwargs['group_by_param'] == 'month':
        grouping = 'month'
        format = "'%m-%Y'"

    string_to_insert = ""
    if 'start_date' in kwargs.keys() and 'end_date' in kwargs.keys():
        start_date_obj = date.fromisoformat(kwargs['start_date'])
        end_date_obj = date.fromisoformat(kwargs['end_date'])
        start_date_str = start_date_obj.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')

        string_to_insert = f'WHERE (rezerwacja.rozpoczecie BETWEEN "{start_date_str}" AND "{end_date_str}")'

    cursor.execute(f'SELECT DATE_FORMAT(rezerwacja.rozpoczecie, {format}), AVG(rezerwacja.koszt) \
                    FROM rezerwacja \
                    JOIN sala \
                    ON rezerwacja.sala_id = sala.id \
                    JOIN budynek \
                    ON budynek.id = sala.budynek_id \
                    JOIN miasto \
                    ON budynek.miasto_id = miasto.id \
                    {string_to_insert} \
                    GROUP BY {grouping}(rezerwacja.rozpoczecie) \
                    ORDER BY rezerwacja.rozpoczecie;')

    data = [(item[0], item[1]) for item in cursor.fetchall()]
    cost_data = pd.DataFrame(data=data, columns=["data_rozpoczecia", "koszt"])

    return cost_data

def update_app():
    pass