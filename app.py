import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from datetime import datetime, date, timedelta
import json, csv, dash_table, time, operator
from connect import norm_records, rec_lows, rec_highs, all_temps
import pandas as pd
from numpy import arange,array,ones
from scipy import stats 
import psycopg2

df_all_temps = pd.DataFrame(all_temps,columns=['dow','sta','Date','TMAX','TMIN'])

df_norms = pd.DataFrame(norm_records)

df_rec_lows = pd.DataFrame(rec_lows)

df_rec_highs = pd.DataFrame(rec_highs)

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")
startyr = 1950
year_count = current_year-startyr

def get_layout():
    return html.Div(
        [
            html.Div([
                html.H1(
                    'DENVER TEMPERATURE RECORD',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.H4(
                    id='title-date-range',
                    className='twelve columns',
                    style={'text-align': 'center'}
                ),
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Label('Select Product'),
                    dcc.RadioItems(
                        id='product',
                        options=[
                            {'label':'Temperature graphs', 'value':'temp-graph'},
                            {'label':'Climatology for a day', 'value':'climate-for-day'},
                            {'label':'5 Year Moving Avgs', 'value':'fyma-graph'},
                        ],
                        # value='temp-graph',
                        labelStyle={'display': 'block'},
                    ),
                ],
                    className='three columns',
                ),
                html.Div([
                    html.Label('Options'),
                    html.Div(
                        id='year-picker'
                    ),
                    html.Div(
                        id='period-picker'
                    ),
                    html.Div(
                        id='date-picker'
                    ),
                ],
                    className='four columns',
                ),  
            ],
                className='row'
            ),
            html.Div([
                html.Div([
                    html.Div(
                        id='graph'
                    ),
                ],
                    className='eight columns'
                ),    
            ],
                className='row'
            ),
            html.Div([
            html.Div([
                html.Div(
                    id='climate-day-table'
                ),
            ],
                className='five columns'
            ),
            html.Div([
                html.Div([
                    html.Div(id='daily-max-t'),
                ],
                    className='twelve columns'
                ),
                html.Div([
                    html.Div(id='daily-min-t'),
                ],
                    className='twelve columns'
                ), 
            ],
                className='seven columns'
            ),     
        ],
            className='row'
        ),
            
            html.Div(id='all-data', style={'display': 'none'}),
            html.Div(id='rec-highs', style={'display': 'none'}),
            html.Div(id='rec-lows', style={'display': 'none'}),
            html.Div(id='norms', style={'display': 'none'}),
            html.Div(id='temp-data', style={'display': 'none'}),
            html.Div(id='df5', style={'display': 'none'}),
            html.Div(id='max-trend', style={'display': 'none'}),
            html.Div(id='min-trend', style={'display': 'none'}),
            html.Div(id='d-max-max', style={'display': 'none'}),
            html.Div(id='avg-of-dly-highs', style={'display': 'none'}),
            html.Div(id='d-min-max', style={'display': 'none'}),
            html.Div(id='d-min-min', style={'display': 'none'}),
            html.Div(id='avg-of-dly-lows', style={'display': 'none'}),
            html.Div(id='d-max-min', style={'display': 'none'}),
        ]
    )

app = dash.Dash(__name__)
app.layout = get_layout
app.config['suppress_callback_exceptions']=True

@app.callback(
            Output('daily-max-t', 'children'),
            [Input('product', 'value'),
            Input('d-max-max', 'children'),
            Input('avg-of-dly-highs', 'children'),
            Input('d-min-max', 'children')])
def max_stats(product, d_max_max, admaxh, d_min_max):
    dly_max_max = d_max_max
    admaxh = admaxh
    dly_min_max = d_min_max
    print(dly_max_max)
    if product == 'climate-for-day':
        return html.Div([
            html.Div([
                html.H6('Maximum Temperatures', style={'text-align':'center', 'color':'red'})
            ]),
            html.Div([
                html.Div([
                    html.Div([
                        html.H6('Maximum', style={'text-align':'center', 'color': 'red'}),
                        html.H6('{}'.format(dly_max_max), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                    html.Div([
                        html.H6('Average', style={'text-align':'center', 'color': 'red'}),
                        html.H6('{:.0f}'.format(admaxh), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                    html.Div([
                        html.H6('Minimum', style={'text-align':'center', 'color': 'red'}),
                        html.H6('{}'.format(dly_min_max), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                ],
                    className='row'
                ),
            ],
                className='pretty_container'
            ),
                
        ],
            # className='twelve columns'
        ),

@app.callback(
            Output('daily-min-t', 'children'),
            [Input('product', 'value'),
            Input('d-min-min', 'children'),
            Input('avg-of-dly-lows', 'children'),
            Input('d-max-min', 'children')])
def min_stats(product, d_min_min, adminl, d_max_min):
    dly_min_min = d_min_min
    adminl = adminl
    dly_max_min = d_max_min
    if product == 'climate-for-day':
        return html.Div([
            html.Div([
                html.H6('Minimum Temperatures', style={'text-align':'center', 'color':'blue'})
            ]),
            html.Div([
                html.Div([
                    html.Div([
                        html.H6('Minimum', style={'text-align':'center', 'color': 'blue'}),
                        html.H6('{}'.format(dly_min_min), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                    html.Div([
                        html.H6('Average', style={'text-align':'center', 'color': 'blue'}),
                        html.H6('{:.0f}'.format(adminl), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                    html.Div([
                        html.H6('Maximum', style={'text-align':'center', 'color': 'blue'}),
                        html.H6('{}'.format(dly_max_min), style={'text-align':'center'})
                    ],
                        className='round1 four columns'
                    ),
                ],
                    className='row'
                ),
            ],
                className='pretty_container'
            ),
                
        ],
            # className='twelve columns'
        ),

@app.callback([
    Output('datatable-interactivity', 'data'),
    Output('datatable-interactivity', 'columns'),
    Output('d-max-max', 'children'),
    Output('avg-of-dly-highs', 'children'),
    Output('d-min-max', 'children'),
    Output('d-min-min', 'children'),
    Output('avg-of-dly-lows', 'children'),
    Output('d-max-min', 'children')],
    [Input('all-data', 'children'),
    Input('date', 'date')])
def display_climate_day_table(all_data, selected_date):
    dr = pd.read_json(all_data)
    
    # dr['Date']=dr['Date'].dt.strftime("%Y-%m-%d") 
    dr.set_index(['Date'], inplace=True)
    # print(dr)
    # print(selected_date)
    dr = dr[(dr.index.month == int(selected_date[5:7])) & (dr.index.day == int(selected_date[8:10]))]
    # dr = df_all_temps[(df_all_temps['Date'][5:7] == date[5:7]) & (df_all_temps['Date'][8:10] == date[8:10])]
    dr = dr.reset_index()
    # print(dr)
    columns=[
        {"name": i, "id": i,"selectable": True} for i in dr.columns
    ]
    
    dr['Date'] = dr['Date'].dt.strftime('%Y-%m-%d')
    d_max_max = dr['TMAX'].max()
    avg_of_dly_highs = dr['TMAX'].mean()
    d_min_max = dr['TMAX'].min()
    # print(avg_of_dly_highs)
    d_min_min = dr['TMIN'].min()
    avg_of_dly_lows = dr['TMIN'].mean()
    d_max_min = dr['TMIN'].max()

    return dr.to_dict('records'), columns, d_max_max, avg_of_dly_highs, d_min_max, d_min_min, avg_of_dly_lows, d_max_min  

@app.callback(
    Output('climate-day-table', 'children'),
    [Input('product', 'value')])
def display_climate_stuff(value):
    if value == 'climate-for-day':
        return dt.DataTable(id='datatable-interactivity',
        data=[{}], 
        columns=[{}], 
        fixed_rows={'headers': True, 'data': 0},
        style_cell_conditional=[
            {'if': {'column_id': 'Date'},
            'width':'100px'},
            {'if': {'column_id': 'TMAX'},
            'width':'100px'},
            {'if': {'column_id': 'TMIN'},
            'width':'100px'},
        ],
        style_data_conditional=[
            {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
            },
        ],
        style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
        },
        # editable=True,
        # filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        selected_columns=[],
        selected_rows=[],
        # page_action="native",
        page_current= 0,
        page_size= 10,
        )

@app.callback(
    Output('period-picker', 'children'),
    [Input('product', 'value')])
def display_period_selector(product_value):
    if product_value == 'temp-graph':
        return  dcc.RadioItems(
                    id = 'period',
                    options = [
                        {'label':'Annual (Jan-Dec)', 'value':'annual'},
                        {'label':'Winter (Dec-Feb)', 'value':'winter'},
                        {'label':'Spring (Mar-May)', 'value':'spring'},
                        {'label':'Summer (Jun-Aug)', 'value':'summer'},
                        {'label':'Fall (Sep-Nov)', 'value':'fall'},
                    ],
                    value = 'annual',
                    labelStyle = {'display':'block'}
                )
    elif product_value == 'fyma-graph':
        return  dcc.RadioItems(
                    id = 'temp-param',
                    options = [
                        {'label':'Max Temp', 'value':'Tmax'},
                        {'label':'Min Temp', 'value':'Tmin'},
                    ],
                    value = 'Tmax',
                    labelStyle = {'display':'block'}
                )

@app.callback(
    Output('date-picker', 'children'),
    [Input('product', 'value')])
    # Input('year', 'value')])
def display_date_selector(product_value):
    if product_value == 'climate-for-day':
        return  html.P('Select Date (MM-DD)'), dcc.DatePickerSingle(
                    id='date',
                    display_format='MM-DD',
                    date=today
                )


@app.callback(
    Output('year-picker', 'children'),
    [Input('product', 'value')])
def display_year_selector(product_value):
    if product_value == 'temp-graph':
        return html.P('Enter Year (YYYY)') ,dcc.Input(
                    id = 'year',
                    type = 'number',
                    # value = str(current_year),
                    min = 1950, max = current_year
                )


@app.callback(Output('graph1', 'figure'),
             [Input('temp-data', 'children'),
             Input('rec-highs', 'children'),
             Input('rec-lows', 'children'),
             Input('norms', 'children'),
             Input('year', 'value'),
             Input('period', 'value')])
def update_figure(temp_data, rec_highs, rec_lows, norms, selected_year, period):
    # print(period)
    previous_year = int(selected_year) - 1
    selected_year = selected_year
    temps = pd.read_json(temp_data)
    temps = temps.drop([0,1], axis=1)
    temps.columns = ['date','TMAX','TMIN']
    temps['date'] = pd.to_datetime(temps['date'])
    temps = temps.set_index(['date'])
    temps['dif'] = temps['TMAX'] - temps['TMIN']
   
   
    temps_cy = temps[temps.index.year.isin([selected_year])]
    temps_py = temps[temps.index.year.isin([previous_year])]
    df_record_highs_ly = pd.read_json(rec_highs)
    df_record_highs_ly = df_record_highs_ly.set_index(1)
    df_record_lows_ly = pd.read_json(rec_lows)
    df_record_lows_ly = df_record_lows_ly.set_index(1)
    df_rl_cy = df_record_lows_ly[:len(temps_cy.index)]
    df_rh_cy = df_record_highs_ly[:len(temps_cy.index)]
    
    df_norms = pd.read_json(norms)
    df_norms_cy = df_norms[:len(temps_cy.index)]
  
    temps_cy.loc[:,'rl'] = df_rl_cy[0].values
    temps_cy.loc[:,'rh'] = df_rh_cy[0].values
    temps_cy.loc[:,'nh'] = df_norms_cy[3].values
    temps_cy.loc[:,'nl'] = df_norms_cy[4].values
   
    if period == 'spring':
        temps = temps_cy[temps_cy.index.month.isin([3,4,5])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index
      
    elif period == 'summer':
        temps = temps_cy[temps_cy.index.month.isin([6,7,8])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    elif period == 'fall':
        temps = temps_cy[temps_cy.index.month.isin([9,10,11])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    elif period == 'winter':
        date_range = []
        date_time = []
        sdate = date(int(previous_year), 12, 1)
        edate = date(int(selected_year), 12, 31)

        delta = edate - sdate

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            date_range.append(day)
        for j in date_range:
            day = j.strftime("%Y-%m-%d")
            date_time.append(day)

        temps_py = temps_py[temps_py.index.month.isin([12])]
        temps_cy = temps_cy[temps_cy.index.month.isin([1,2])]
        temp_frames = [temps_py, temps_cy]
        temps = pd.concat(temp_frames, sort=True)
        date_time = date_time[:91]  
        
        df_record_highs_jan_feb = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_highs_dec = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(12-)')]
        high_frames = [df_record_highs_dec, df_record_highs_jan_feb]
        df_record_highs = pd.concat(high_frames)

        df_record_lows_jan_feb = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_lows_dec = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(12-)')]
        low_frames = [df_record_lows_dec, df_record_lows_jan_feb]
        df_record_lows = pd.concat(low_frames)

        df_high_norms_jan_feb = df_norms[3][0:60]
        df_high_norms_dec = df_norms[3][335:]
        high_norm_frames = [df_high_norms_dec, df_high_norms_jan_feb]
        df_high_norms = pd.concat(high_norm_frames)

        df_low_norms_jan_feb = df_norms[4][0:60]
        df_low_norms_dec = df_norms[4][335:]
        low_norm_frames = [df_low_norms_dec, df_low_norms_jan_feb]
        df_low_norms = pd.concat(low_norm_frames)

        bar_x = date_time
        nh_value = df_high_norms
        nl_value = df_low_norms
        rh_value = df_record_highs[0]
        rl_value = df_record_lows[0]

    else:
        temps = temps_cy
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    mkr_color = {'color':'black'}
      
    trace = [
            go.Bar(
                y = temps['dif'],
                x = bar_x,
                base = temps['TMIN'],
                name='Temp Range',
                marker = mkr_color,
                hovertemplate = 'Temp Range: %{y} - %{base}<extra></extra><br>'
                                # 'Record High: %{temps[6]}'                  
            ),
            go.Scatter(
                y = nh_value,
                x = bar_x,
                # hoverinfo='none',
                name='Normal High',
                marker = {'color':'indianred'}
            ),
            go.Scatter(
                y = nl_value,
                x = bar_x,
                # hoverinfo='none',
                name='Normal Low',
                marker = {'color':'slateblue'}
            ),
            go.Scatter(
                y = rh_value,
                x = bar_x,
                # hoverinfo='none',
                name='Record High',
                marker = {'color':'red'}
            ),
            go.Scatter(
                y = rl_value,
                x = bar_x,
                # hoverinfo='none',
                name='Record Low',
                marker = {'color':'blue'}
            ),
        ]
    layout = go.Layout(
                xaxis = {'rangeslider': {'visible':True},},
                yaxis = {"title": 'Temperature F'},
                title ='Daily Temps',
                plot_bgcolor = 'lightgray',
                height = 700,
        )
    return {'data': trace, 'layout': layout}

@app.callback(Output('fyma-graph', 'figure'),
             [Input('temp-param', 'value'),
             Input('df5', 'children'),
             Input('max-trend', 'children'),
             Input('min-trend', 'children'),
             Input('all-data', 'children')])
def update_fyma_graph(selected_param, df_5, max_trend, min_trend, all_data):
    # print(all_data)
    fyma_temps = pd.read_json(all_data)
    fyma_temps['Date']=fyma_temps['Date'].dt.strftime("%Y-%m-%d") 
    fyma_temps.set_index(['Date'], inplace=True)

    df_5 = pd.read_json(df_5)

    all_max_temp_fit = pd.DataFrame(max_trend)
    all_max_temp_fit.index = df_5.index
    all_max_temp_fit.index = all_max_temp_fit.index.strftime("%Y-%m-%d")

    all_min_temp_fit = pd.DataFrame(min_trend)
    all_min_temp_fit.index = df_5.index
    all_min_temp_fit.index = all_min_temp_fit.index.strftime("%Y-%m-%d")

    all_max_rolling = fyma_temps['TMAX'].dropna().rolling(window=1825)
    all_max_rolling_mean = all_max_rolling.mean()
    
    all_min_rolling = fyma_temps['TMIN'].dropna().rolling(window=1825)
    all_min_rolling_mean = all_min_rolling.mean()

    if selected_param == 'Tmax':
        trace = [
            go.Scatter(
                y = all_max_rolling_mean,
                x = fyma_temps.index,
                name='Max Temp'
            ),
            go.Scatter(
                y = all_max_temp_fit[0],
                x = all_max_temp_fit.index,
                name = 'trend',
                line = {'color':'red'}
            ),
        ]
    elif selected_param == 'Tmin':
        trace = [
            go.Scatter(
                y = all_min_rolling_mean,
                x = fyma_temps.index,
                name='Min Temp'
            ),
            go.Scatter(
                y = all_min_temp_fit[0],
                x = all_min_temp_fit.index,
                name = 'trend',
                line = {'color':'red'}
            ),
        ]
    layout = go.Layout(
        xaxis = {'rangeslider': {'visible':True},},
        yaxis = {"title": 'Temperature F'},
        title ='5 Year Rolling Mean {}'.format(selected_param),
        plot_bgcolor = 'lightgray',
        height = 500,
    )
    return {'data': trace, 'layout': layout}


@app.callback(
    Output('graph', 'children'),
    [Input('product', 'value')])
def display_graph(value):
    if value == 'temp-graph':
        return dcc.Graph(id='graph1')
    elif value == 'fyma-graph':
        return dcc.Graph(id='fyma-graph')

@app.callback(Output('all-data', 'children'),
            [Input('product', 'value')])
def all_temps_cleaner(product_value):
    # print(product_value)
    cleaned_all_temps = df_all_temps
    cleaned_all_temps.columns=['dow','sta','Date','TMAX','TMIN']
    cleaned_all_temps['Date'] = pd.to_datetime(cleaned_all_temps['Date'])
    cleaned_all_temps = cleaned_all_temps.drop(['dow','sta'], axis=1)

    return cleaned_all_temps.to_json(date_format='iso')

@app.callback(Output('title-date-range', 'children'),
            [Input('product', 'value'),
            Input('all-data', 'children')])
def all_temps_cleaner(product, temps):
    # print(temps)
    title_temps = pd.read_json(temps)
    title_temps['Date']=title_temps['Date'].dt.strftime("%Y-%m-%d")
    last_day = title_temps.iloc[-1, 0] 
    
    return '1950-01-01 through {}'.format(last_day)

@app.callback(Output('rec-highs', 'children'),
             [Input('year', 'value')])
def rec_high_temps(selected_year):
    if int(selected_year) % 4 == 0:
        rec_highs = df_rec_highs
    else:
        rec_highs = df_rec_highs.drop(df_rec_highs.index[59])
    return rec_highs.to_json()

@app.callback(Output('rec-lows', 'children'),
             [Input('year', 'value')])
def rec_low_temps(selected_year):
    if int(selected_year) % 4 == 0:
        rec_lows = df_rec_lows
    else:
        rec_lows = df_rec_lows.drop(df_rec_lows.index[59])
    return rec_lows.to_json()

@app.callback(Output('norms', 'children'),
             [Input('year', 'value')])
def norm_highs(selected_year):
    if int(selected_year) % 4 == 0:
        norms = df_norms
    else:
        norms = df_norms.drop(df_norms.index[59])
    return norms.to_json()

@app.callback(
    Output('df5', 'children'),
    [Input('all-data', 'children'),
    Input('product', 'value')])
def clean_df5(all_data, product_value):
    title_temps = pd.read_json(all_data)
    title_temps['Date']=title_temps['Date'].dt.strftime("%Y-%m-%d")
    df_date_index = df_all_temps.set_index(['Date'])
    df_ya_max = df_date_index.resample('Y').mean()
    df5 = df_ya_max[:-1]
    df5 = df5.drop(['dow'], axis=1)
    # print(df5)
    return df5.to_json(date_format='iso')

@app.callback(
    Output('max-trend', 'children'),
    [Input('df5', 'children'),
    Input('product', 'value')])
def all_max_trend(df_5, product_value):
    
    df5 = pd.read_json(df_5)
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5['TMAX'])

    return (slope*xi+intercept)

@app.callback(
    Output('min-trend', 'children'),
    [Input('df5', 'children'),
    Input('product', 'value')])
def all_min_trend(df_5, product_value):
    
    df5 = pd.read_json(df_5)
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5['TMIN'])
    
    return (slope*xi+intercept)

@app.callback(Output('temp-data', 'children'),
             [Input('year', 'value'),
             Input('period', 'value')])
def all_temps(selected_year, period):
    previous_year = int(selected_year) - 1
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")
        cursor = connection.cursor()

        postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) IN ({},{}) ORDER BY "DATE" ASC'.format(selected_year, previous_year)
        cursor.execute(postgreSQL_select_year_Query)
        temp_records = cursor.fetchall()
        df = pd.DataFrame(temp_records)
        
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return df.to_json()

if __name__ == "__main__":
    app.run_server(port=8050, debug=False)