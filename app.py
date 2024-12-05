
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
from lib.pwsapi import get_all_stations
from lib.pws_map import station_map, station_marker_id, station_from_marker_id
from lib.converters import degree2compass, kph2mph, c2f, mm2inch

### CONFIG
ag_hall_coordinates = [42.73104, -84.47951]
bs53css = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"

app = Dash(__name__, prevent_initial_callbacks=True,  external_stylesheets= [bs53css])  #dbc.themes.BOOTSTRAP

APP_PATH =  path.abspath(path.dirname(__file__))
TEMPLATES_DIR = getenv('DASH_TEMPLATE_DIR', path.join(APP_PATH, "templates"))

TemplateRenderer(dash=app)

from flask_caching import Cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': getenv('DASH_CACHE', path.join(APP_PATH, 'cache-directory'))
})

TIMEOUT:int = 60

@cache.memoize(timeout=TIMEOUT)
def station_records()->list:
    return(get_all_stations())

@cache.memoize(timeout=TIMEOUT)
def get_template(template_file, template_dir:str = TEMPLATES_DIR)->str:
  with open(path.join(template_dir, template_file)) as template_file:
    main_template:str = template_file.read()
  return(main_template)
  
    
app.layout =  render_dash_template_string(get_template(template_file = "main.html"),
    station_table = pwsc.station_table_narrow(station_records()),
    station_map = station_map(station_records()),
    hourly_weather_form = hourly_weather_form(),
    tomcast_form = pwsc.tomcast_form(), 
    weather_summary_form = pwsc.weather_summary_form()    
  )
 

#### REACTIVITY 

### table row click, delivers a station code for later 


#### TODO! 

### remove the hourly_readings_table output from here, and only 
# output the station_code in the text_station_table_selection 
# THEN use the callback below that updates the hourly table when the date is 
# selected, to update when either date is selected or the 
@app.callback(
    [Output("text_station_table_selection", "children"),
    Output("text_station_table_selection", "href"),
    Output("station_type_cell", "children"),
    Output("hourly_readings_table", "children", allow_duplicate=True),
    Output('tomcast-results', 'children',allow_duplicate=True)],
    Input("station_table", "selectedRows"),
    prevent_initial_call=True,
)
def station_table_row_data(row)->tuple[str,str,str,str]:
    if row is None or row == []:
        return ("","", "",  dbc.Alert("select a station above", color="warning"),"")
    # we got a list but just want one
    #try:
    if isinstance(row,list): row = row[0]
    if isinstance(row, dict) and 'station_code' in row:
        station_code = row['station_code']
        station_type = row['type']
        readings_table  = hourly_readings_table(station_code)
            
    else:
        station_code = ""
        station_type = ""
        readings_table = html.Div("invalid station selection", className="fw-bold")    
        
    return (station_code, station_code, station_type, readings_table, "") 
    #except Exception as e:
    #    return ("","", e)


### latest weather stats
@app.callback(
    [
        Output("latest_reading_date_cell", "children"),
        Output("latest-atmp", "children"),
        Output("latest-pcpn", "children"),
        Output("latest-relh", "children"),
        Output("latest-wspd", "children"),
        Output("latest-wdir", "children"),
    ],
    Input("station_table", "selectedRows"),
    prevent_initial_call=True,
)
def station_latest_weather(row):
    
    from datetime import datetime
    
    if row is None or row == []:
        return ("","--","--","--","--", "")
    
    if isinstance(row,list): row = row[0]

    if isinstance(row, dict) and 'station_code' in row:        
        latest_reading = latest_readings_values(row['station_code'])
        if isinstance(latest_reading, dict) and 'atmp' in latest_reading: 
            latest_reading_dateime = datetime.fromisoformat(latest_reading['local_datetime'])
            formatted_datetime = latest_reading_dateime.strftime("%I:%M %p %m-%d-%Y")
            return (formatted_datetime , 
                    round(c2f(latest_reading['atmp']),1), 
                    round(mm2inch(latest_reading['pcpn']),1), 
                    round(latest_reading['relh'],1),
                    round(kph2mph(latest_reading['wspd']),1),
                    degree2compass(latest_reading['wdir'])  
                    )        
    return ("no recent readings","--","--","--","--", "")


### map marker click
# the output is to select the table row, which then triggers the row click
@app.callback(
        # Output("text_station_map_coordinates", "children"),
        Output("station_table", "selectedRows"),
        [Input(station_marker_id(station), 'n_clicks') for station in list(station_records().values())],
        prevent_initial_call=True,
        )
def display_marker_click(*args):
    if not ctx.triggered_id:
        return({})
    else:
        station_code = station_from_marker_id(ctx.triggered_id)
        # station_record = station_records[station_code]
        return({"function": f"params.data.station_code == '{station_code}'"})            
        # return(station_code, {"function": f"params.data.station_code == '{station_code}'"})   



# ##### Hourly Weather
# @app.callback(
#     Output("hourly_readings_table", "children", allow_duplicate=True),
#     Input("hourly-weather-date-picker", "value"),
#     State("text_station_table_selection", "children"),
#     prevent_initial_call=True,
# )
# def redraw_hourly_weather_table(hourly_weather_date_str, station_code):
#     for_date = date.fromisoformat(hourly_weather_date_str)
#     readings_table  = hourly_readings_table(station_code, for_date = for_date)
#     return(readings_table)
# # hourly-weather-date-picker


##### WEATHER SUMMARY


### clear the weather summary table when new station is selected
@app.callback(
    Output('weather-summary-table', 'children',allow_duplicate=True),
    Input("station_table", "selectedRows"),
    prevent_initial_call=True,
)
def clear_weather_summary_table(row):
    # TODO - check if the row selected is actually different first!
    return("")


@app.callback(
    Output('weather-summary-table', 'children', allow_duplicate=True),
    Input('run-weather-summary-button','n_clicks'),
    State("text_station_table_selection", "children"),
    State("weather-summary-date-picker", "date"),
    prevent_initial_call=True,
    )
def weather_summary(n_clicks, station_code, select_date):
    # input checking 
    if not station_code:
        return(dbc.Alert("select a station above", color="error"))
    
    if not select_date or not(isinstance(select_date, str)):
        return(dbc.Alert("select a date and click 'run tomcast'"))
    
    # run model and format output
    weather_summary_grid = pwsc.weather_summary_table(station_code, select_date)
    return(weather_summary_grid)



##### TOMCAST 
@app.callback(
    Output('tomcast-results', 'children',allow_duplicate=True),
    Input('run-tomcast-button','n_clicks'),
    State("text_station_table_selection", "children"),
    State("tomcast-date-picker", "date"),
    prevent_initial_call=True,
    )
def tomcast(n_clicks, station_code, select_date):
    # input checking 
    if not station_code:
        return(dbc.Alert("select a station above", color="error"))
    
    if not select_date or not(isinstance(select_date, str)):
        return(dbc.Alert("select a date and click 'run tomcast'"))
    
    # run model and format output
    return(tomcast_model(station_code, select_date))
    
  
                
if __name__ == "__main__":
    # debug = None required to respect DASH_DEBUG environment var (True /False)
    app.run(debug=None)
