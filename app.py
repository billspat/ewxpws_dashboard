
from os import getenv, path
from datetime import date
import pandas as pd
from dash import ctx, dcc, Dash, html, Input, Output, State
import dash_ag_grid as dag
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Table as dbcTable
from dash_template_rendering import TemplateRenderer, render_dash_template_string


from lib.pws_components import pws_title, station_table, station_table_narrow, yesterday_readings_table, run_tomcast_model, tomcast_form, latest_readings_values
from lib.pwsapi import get_all_stations
from lib.pws_map import station_map, station_marker_id, station_from_marker_id

### CONFIG
ag_hall_coordinates = [42.73104, -84.47951]
bs53css = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"

app = Dash(__name__, prevent_initial_callbacks=True,  external_stylesheets= [bs53css])  #dbc.themes.BOOTSTRAP
TemplateRenderer(dash=app)

from flask_caching import Cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT:int = 60

@cache.memoize(timeout=TIMEOUT)
def station_records()->list:
    return(get_all_stations())

@cache.memoize(timeout=TIMEOUT)
def get_template(template_file_path:str = "templates/main.html")->str:
  with open(template_file_path) as template_file:
    main_template:str = template_file.read()
  return(main_template)
  
    
app.layout =  render_dash_template_string(get_template(template_file_path = "templates/main.html"),
    station_table = station_table_narrow(station_records()),
    station_map = station_map(station_records()),
    tomcast_form = tomcast_form()
  )
 

#### REACTIVITY 

from lib.pws_components import readings_grid_view
### table row click, delivers a station code for later use
@app.callback(
    [Output("text_station_table_selection", "children"),
    Output("text_station_table_selection", "href"),
    Output("station_type_cell", "children"),
    Output("daily_readings_table", "children"),
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
    
        # try:
        readings_df = yesterday_readings_table(station_code)
        if(readings_df is None or (type(readings_df) != type(pd.DataFrame([{}]))) or readings_df.empty):
            readings_table = html.Div("no recent data", className="fw-bold")
        else:
            readings_table =  dbcTable.from_dataframe(readings_df, responsive=True)
            
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
    ],
    Input("station_table", "selectedRows"),
    prevent_initial_call=True,
)
def station_latest_weather(row):
    
    from datetime import datetime
    
    if row is None or row == []:
        return ("","--","--","--","--")
    
    if isinstance(row,list): row = row[0]

    if isinstance(row, dict) and 'station_code' in row:        
        latest_reading = latest_readings_values(row['station_code'])
        if isinstance(latest_reading, dict) and 'atmp' in latest_reading: 
            latest_reading_dateime = datetime.fromisoformat(latest_reading['local_datetime'])
            formatted_datetime = latest_reading_dateime.strftime("%I:%M %p %m-%d-%Y")
            return (formatted_datetime , 
                    round(latest_reading['atmp'],1), 
                    round(latest_reading['pcpn'],1), 
                    round(latest_reading['relh'],1),
                    round(latest_reading['wspd'],1)                    
                    )        
    return ("no recent readings","--","--","--","--")


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



##### TOMCAST

@app.callback(
    Output('tomcast-results', 'children',allow_duplicate=True),
    Input('run-tomcast-button','n_clicks'),
    State("text_station_table_selection", "children"),
    State("tomcast-date-picker", "date"),
    prevent_initial_call=True,
    )
def tomcast(n_clicks, station_code = 'EWXDAVIS01', select_date = date(2024, 8, 1)):
    
    if not station_code or station_code is None:
        return(dbc.Alert("select a station above", color="error"))
    
    if not select_date or not(isinstance(select_date, str)):
        print(f"got this for select_date: {select_date}")
        # select_date = date(2024, 8, 1)

    if isinstance(select_date,str):
        select_date = date.fromisoformat(select_date)
    
    tomcast_output_df = run_tomcast_model(station_code, select_date)

    if isinstance(tomcast_output_df, pd.DataFrame):
        tomcast_table = dbcTable.from_dataframe(tomcast_output_df, responsive=True)
        return(tomcast_table)
    else: # assume it's not a data frame, must be string with message
        return(tomcast_output_df)

                  
if __name__ == "__main__":
    # debug = None required to respect DASH_DEBUG environment var (True /False)
    app.run(debug=None)
