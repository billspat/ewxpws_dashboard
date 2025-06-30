
import sys
from os import getenv, path
from dotenv import load_dotenv
load_dotenv()
from datetime import date
import pandas as pd
from dash import ctx, dcc, Dash, html, Input, Output, State
import dash_ag_grid as dag
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Table as dbcTable
from dash_template_rendering import TemplateRenderer, render_dash_template_string


import lib.pws_components as pwsc
from lib.pws_components import * 
from lib.pwsapi import get_all_stations, get_station_data
from lib.pws_map import station_map, station_marker_id, station_from_marker_id
from lib.converters import degree2compass, kph2mph, c2f, mm2inch

#### CONFIG AND APP SETUP
bs53css = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
APP_PATH =  path.abspath(path.dirname(__file__))
app = Dash(__name__, prevent_initial_callbacks=True,  external_stylesheets= [bs53css])  

from flask_caching import Cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': getenv('DASH_CACHE', path.join(APP_PATH, 'cache-directory'))
})
TIMEOUT:int = 60 # seconds

@cache.memoize(timeout=TIMEOUT)
def station_records()->list:
    return(get_all_stations())



#### PAGE LAYOUT
# note using external library dash_template_rendering which uses a jinja file
# as a template rather than putting all the HTML tag functions directly in 
# app.py which is much easier to edit.  
# see https://github.com/pschleiter/dash-template-rendering

# have to hack the default html that dash creates to work with our template
TEMPLATES_DIR = getenv('DASH_TEMPLATE_DIR', path.join(APP_PATH, "templates"))
TemplateRenderer(dash=app)

# custom function to read file into string for  render_dash_template_string
# and to cache it
@cache.memoize(timeout=TIMEOUT)
def get_template(template_file, template_dir:str = TEMPLATES_DIR)->str:
  with open(path.join(template_dir, template_file)) as template_file:
    main_template:str = template_file.read()
  return(main_template)

# hack default template to work with our layout 
body_with_class_for_template = '<body class="layout-fluid">'
app.index_string = app.index_string.replace('<body>', body_with_class_for_template)

# render the jinja template using template file    
app.layout =  render_dash_template_string(get_template(template_file = "main.html"),
    interval_component = dcc.Interval(
            id='interval-component',
            interval= 5*60*1000, # 5 minutes in milliseconds
            n_intervals=1
        ),
    station_table = pwsc.station_table_narrow(station_records()),
    station_map = station_map(station_records()),
    hourly_weather_form = hourly_weather_form(),
    weather_viz = dcc.Loading(html.Div(id = "weather-summary-viz", className="mt-3 p-1")),
    tomcast_form = pwsc.tomcast_form(), 
    tomcast_results = dcc.Loading(html.Div(id="tomcast-results", className="mt-3 p-1")),
    weather_summary_form = pwsc.weather_summary_form(),
    weather_summary_results = dcc.Loading(html.Div(id = "weather-summary-table", className="mt-3 p-1")),
    applescab_form = pwsc.applescab_form(), 
    applescab_results = dcc.Loading(html.Div(id="applescab-results", className="mt-3 p-1")),
    counter_debug  = html.Span("0", id = "counter-debug"),
  )


#### REACTIVITY #####
    
## table row click, stores the station code of the selected row in an
# element on the html page, that is read by several other components.  
# this is helpful so the 'selected_row' doesn't have to be sent 
# and this component can be used as a state value
# This callback is not affected by the page time, only table row click
@app.callback(
    [
        Output("text_station_table_selection", "children"),
        Output("text_station_table_selection", "href"),
        Output("station_type_cell", "children"),
        Output('tomcast-results', 'children',allow_duplicate=True)
    ],
    [Input("station_table", "selectedRows")],
    prevent_initial_call=True,
)
def station_table_row_data(row  )->tuple[str,str,str,str]:
    if row is None or row == []:
        return ("","", "", "") 
    
    # we got a list but just want one, so pick
    if isinstance(row,list): row = row[0]
    
    if isinstance(row, dict) and 'station_code' in row:
        station_code = row['station_code']
        station_type = row['type']
            
    else:
        station_code = ""
        station_type = ""
        
    return (station_code, station_code, station_type,  "")
    #except Exception as e:
    #    return ("","", e)


### load latest weather stats from selected station
@app.callback(
    [
        Output("latest_reading_date_cell", "children"),
        Output("latest-atmp", "children"),
        Output("latest-pcpn", "children"),
        Output("latest-relh", "children"),
        Output("latest-wspd", "children"),
        Output("latest-wdir", "children"),
        Output("latest-lws", "children"),
        Output("counter-debug", "children"),         
    ],
    [
        Input("station_table", "selectedRows"),
        Input('interval-component', 'n_intervals')
    ],
    prevent_initial_call=True,
)
def station_latest_weather(row, n):
    
    from datetime import datetime
    
    if not row:
        return ("","--","--","--","--", "", "--", n)
    
    if isinstance(row,list): row = row[0]

    if isinstance(row, dict) and 'station_code' in row:        
        latest_reading = latest_readings_values(row['station_code'])
        if isinstance(latest_reading, dict) and 'atmp' in latest_reading: 
            latest_reading_dateime = datetime.fromisoformat(latest_reading['local_datetime'])
            formatted_datetime = latest_reading_dateime.strftime("%I:%M %p %m-%d-%Y")
            
            atmp = round(c2f(latest_reading['atmp']),1) if latest_reading.get('atmp') or latest_reading.get('atmp') == 0 else "--"
            pcpn = round(mm2inch(latest_reading['pcpn']),1) if latest_reading.get('pcpn') or latest_reading.get('pcpn') == 0 else "0"
            relh = round(latest_reading['relh'],1) if latest_reading.get('relh') or latest_reading.get('relh') == 0 else "--"
            wspd = round(kph2mph(latest_reading['wspd']),1) if latest_reading.get('wspd') or latest_reading.get('wspd') == 0 else "--"
            wdir = degree2compass(latest_reading['wdir'])if latest_reading.get('wdir') else "--"
            lws = latest_reading['lws'] if latest_reading.get('lws') or latest_reading.get('lws') == 0 else "--"
            return (formatted_datetime,
                    atmp,                             
                    pcpn,
                    relh,
                    wspd,
                    wdir,
                    lws,
                    n)        
    return ("no recent readings","--","--","--","--", "",n)


### map marker click, which selects a table row
# which then triggers the row selection. 
# see Dash AG Grig docs for how sending a function can select a row
@app.callback(
        Output("station_table", "selectedRows", allow_duplicate = True),
        [Input(station_marker_id(station), 'n_clicks') for station in list(station_records().values())],
        prevent_initial_call=True,
        )
def display_marker_click(*args):
    if not ctx.triggered_id:
        return({})
    else:
        station_code = station_from_marker_id(ctx.triggered_id)
        return({"function": f"params.data.station_code == '{station_code}'"})            

##### weather line graph, currently only air temp
@app.callback(
    Output("weather-summary-viz",'children'),
    Input("text_station_table_selection", "children"),
    prevent_initial_call=True,
)
def redraw_weather_viz(station_code):
    if not station_code:
        return(dbc.Alert("select a station above", color="warning"))
    
    return(dcc.Graph(figure=pwsc.weather_summary_viz(station_code),id='weather-graph'))


##### Hourly Weather table from the PWS API 
@app.callback(
    Output("hourly_readings_table", "children", allow_duplicate=True),
    [
        Input("hourly-weather-date-picker", "date"),
        Input("text_station_table_selection", "children"),
        Input('interval-component', 'n_intervals')
    ],
    prevent_initial_call=True,
)
def redraw_hourly_weather_table(hourly_weather_date, station_code, n):
    if not station_code:
        return(dbc.Alert("select a station above", color="warning"))
    
    # for_date = date.fromisoformat(hourly_weather_date)
    readings_table  = hourly_readings_table(station_code, for_date = hourly_weather_date)
    return(readings_table)


###### MODEL FORMS AND OUTPUTS

## turn on/off model output and forms as stations are selected
@app.callback(
    [
        Output('data_section', 'style'), 
        Output('no_station_message', 'style')
    ],
    Input("station_table", "selectedRows"),
    prevent_initial_call=True,
)
def display_form_on_select(row):    
    style_to_hide_model_form = ({'display': 'none'},{'display': 'inline'})
    style_to_show_model_form = ({"diplay":"inline"},{'display': 'none'})
    
    if row is None or row == []:
        return (style_to_hide_model_form) 
    if isinstance(row,list): row = row[0]
    if isinstance(row, dict) and 'station_code' in row:
        station_code = row['station_code']
    else:
        station_code = ""
    
    if station_code:            
        return (style_to_show_model_form ) 
    else:
        return(style_to_hide_model_form )
    

##### WEATHER SUMMARY model
# clear the weather summary table when new station is selected
@app.callback(
    Output('weather-summary-table', 'children',allow_duplicate=True),
    Input("station_table", "selectedRows"),
    prevent_initial_call=True,
)
def clear_weather_summary_table(row):
    # TODO - check if the row selected is actually different first!
    return("")

# submit click 
@app.callback(
    Output('weather-summary-table', 'children', allow_duplicate=True),
    [Input('run-weather-summary-button','n_clicks'),],
    State("text_station_table_selection", "children"),
    State("weather-summary-date-picker", "date"),
    prevent_initial_call=True,
    )
def weather_summary(n_clicks, station_code, select_date):
    # input checking 
    if not station_code:
        return(dbc.Alert("select a station above", color="error"))
    
    if not select_date or not(isinstance(select_date, str)):
        return(dbc.Alert("select a date and click 'run'"))
    
    # run model and format output
    weather_summary_grid = pwsc.weather_summary_table(station_code, select_date)
    return(weather_summary_grid)


##### TOMCAST ####################


## TOMCAST MODEL RUN
@app.callback(
    Output('tomcast-results', 'children'),  
    Input('run-tomcast-button','n_clicks'),
    State("text_station_table_selection", "children"),
    State("tomcast-date-picker", "date"),
    State("tomcast-spray-date-picker", "date"),
    prevent_initial_call=True,
    )
def tomcast(n_clicks, station_code, select_date, date_start_accumulation):
    # input checking 
    if not station_code:
        return dbc.Alert("select a station above", color="error")
    
    if not select_date or not(isinstance(select_date, str)):
        return dbc.Alert("select a date, optional spray date, and click 'run tomcast'")
    
    # run model and format output
    return tomcast_model(station_code, select_date,date_start_accumulation)



##### APPLESCAB ####################

@app.callback(
    Output('applescab-results', 'children'),  
    Input('run-applescab-button','n_clicks'),
    State("text_station_table_selection", "children"),
    State("applescab-date-picker", "date"),
    State("applescab-greentip-date-picker", "date"),
    prevent_initial_call=True,
    )
def run_applescab(n_clicks, station_code, select_date, gt_start):
    # input checking 
    if not station_code:
        return dbc.Alert("select a station above", color="error")
    
    if not select_date or not(isinstance(select_date, str)):
        return dbc.Alert("select a date, optional green tip date, and click 'run'")
    
    # run model and format output
    model_table = pwsc.applescab_model(station_code, select_date, gt_start)
    return(model_table)
                
if __name__ == "__main__":
    # debug = None required to respect DASH_DEBUG environment var (True /False)
    app.run(debug=None)
