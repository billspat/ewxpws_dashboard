
# pws_components.py  reuseable components for pages
from dash import html
from lib.pwsapi import get_station_codes, get_station_data, get_all_stations
from datetime import date, timedelta

from .pwsapi import get_hourly_readings, yesterday_readings
import dash_ag_grid as dag
import pandas as pd
# from dash_bootstrap_components import Table as dbcTable


## Config
main_pws_title = 'MSU Enviroweather Personal Weather Station Dashboard'
site_nav = ["map", "station", "hourly", "about"]
sidebar_width = 250
DAYS_MISSING_THRESHOLDS = [1,4]

pws_title = html.H2(["MSU Enviroweather ", html.B(" Personal Weather Station Dashboard"),])

YESTERDAY = date.today() - timedelta(days = 1)


def station_table(station_records):
    
    station_data = list(station_records.values())

    station_fields = list(station_data[0].keys())
    fields_to_hide = ['id', 'install_date', 'ewx_user_id', 'background_place', 'timezone', 'lat', 'lon', 
                  'api_config', 
                  'expected_readings_day', 
                  'expected_readings_hour', 
                  'first_reading_datetime_utc', 
                  'latest_reading_datetime_utc', 
                  'active']
    

    station_column_defs = [{"field": f} for f in station_fields]
    station_column_state = [{"colId": f, "hide": (f in fields_to_hide)} for f in station_fields]


    grid = dag.AgGrid(
        id="station_table",
        rowData=station_data,
        columnDefs=station_column_defs,
        columnState = station_column_state,
        defaultColDef={"resizable": True, "sortable": True, "filter": True},
        columnSize="sizeToFit",
        dashGridOptions={"rowSelection": "single", "cellSelection": False, "animateRows": False},
    )
    
    return(grid)


from datetime import date, datetime
def station_status(station):
    # convert from the string the comes from the station
    last_reading_dt = datetime.fromisoformat(station['latest_reading_datetime'])
    day_diff = (datetime.now().date() - last_reading_dt.date() ).days
    if day_diff <= DAYS_MISSING_THRESHOLDS[0]: return('Green')
    if day_diff <= DAYS_MISSING_THRESHOLDS[1]: return('Yellow')
    return('Red')



def station_current_temperature(station_code):
    allreadings = get_hourly_readings(station_code)
    latest = allreadings[-1]
    return(latest['atmp'])
    
        
def station_table_narrow(station_records):
    """table of stations with a few carefully columns for narrow column display

    Args:
        station_records (dict[dict]): dictionary of station records keyed on station code that comes from API
        
    Returns:
        dash_ag_grid.AgGrid table for placing on dash page
        
    """
    df = pd.DataFrame(list(station_records.values()))
    table_df = pd.DataFrame().assign(location = df.location_description, 
                                     type=df['station_type'] + " (" + df["sampling_interval"].map(str)+" min)",
                                     station_code = df.station_code, 
                                     latest_reading = df.latest_reading_datetime)
    
    station_fields = list(table_df.columns)
    station_column_defs = [{"field": f} for f in station_fields]

    grid = dag.AgGrid(
        id="station_table",
        rowData = table_df.to_dict('records'),
        columnDefs = station_column_defs,
        defaultColDef={"resizable": True, "sortable": True, "filter": True},
        columnSize="sizeToFit",
        dashGridOptions={"rowSelection": "single", "cellSelection": False, "animateRows": False},
        
    )
    
    return(grid)




def yesterday_readings_table(station_code):
    if station_code:
        # get a data frame of readings or empty df
        weather_df = yesterday_readings(station_code)
        if(weather_df is None or (type(weather_df) != type(pd.DataFrame([{}]))) or weather_df.empty):
            return("No Data")        
        else:
            view_df = pd.DataFrame().assign(
                date = weather_df['represented_date'],
                hour = weather_df.represented_hour, 
                atmp = weather_df.atmp_avg_hourly,
                relh = weather_df.relh_avg_hourly,
                pcpn = round(weather_df.pcpn_total_hourly,3),
                lws_pwet = weather_df.lws_pwet_hourly,
                wspd = weather_df.wspd_avg_hourly,
                wspd_max = weather_df.wspd_max_hourly
            )
            view_df = view_df.sort_values(by=['hour'], ascending=False)
            return(view_df)
        
            #df_table = dbcTable.from_dataframe(df)
            #return(df_table)
    else:
        return("Select a station code")
    

from datetime import time


# this currently is not used.   Need to determine how to insert a whole AG grid into html 
    # there is a "I can't json this" error

def readings_grid_view(weather_df):
    """given data frame of weather from database, convert to presentation grid"""
    table_df = pd.DataFrame().assign(
        date = weather_df.represented_date,
        hour = f"{str(time(hour = weather_df.represented_hour-1, minute=0))} - {str(time(hour = weather_df.represented_hour-1, minute=59))}", 
        atmp = weather_df.atmp_avg_hourly,
        relh = weather_df.relh_avg_hourly,
        pcpn = weather_df.pcpn_total_hourly,
        lws = weather_df.lws_pwet_hourly,
        wspd = weather_df.wspd_avg_hourly,
        wspd_max = weather_df.wspd_max_hourly
    )

    fields = list(table_df.columns)    
    column_defs = [{"field": f} for f in fields]
    grid = dag.AgGrid(
        id="weather_readings",
        rowData=table_df,
        columnDefs=column_defs,
        defaultColDef={"resizable": True, "sortable": True, "filter": True},
        columnSize="sizeToFit",
        dashGridOptions={"rowSelection": "single", "cellSelection": False, "animateRows": False},
    )   
    return(grid)


import dash_bootstrap_components as dbc
from dash import dcc
from datetime import date
from zoneinfo import ZoneInfo

def tomcast_form():
    today =  datetime.now(tz=ZoneInfo('US/Eastern')).date().strftime("%Y-%m-%d")
    
    # using bootstrap classes here becuase the default style is large and thin which doesn't match
    form = dbc.Row(
        [
            dbc.Col(
                dcc.DatePickerSingle(id='tomcast-date-picker',
                                     display_format='YYYY-MM-DD',
                                     first_day_of_week = 1,                                       
                                     placeholder="Select Date",
                                     date = today, 
                                     className="fs-6 fw-semibold"),
                className="me-3",
                width = "auto"

                ),
            dbc.Col(
                dbc.Button("Run Tomcast for Select Date", 
                               id="run-tomcast-button", 
                               class_name="btn btn-success d-none d-sm-inline-block"), 
                width="auto"
                ),
        ],
        className="g-2",
        )
    
    
    return(form)
    
    
from .ewx_api import request_tomcast_api, format_tomcast_model_output
def run_tomcast_model(station_code:str, select_date:date):
    """get simple tomcast model output and format for Dash.  
    example use tc = request_tomcast_api(station_code='EWXDAVIS01', select_date=date(2024, 8, 1))
    tc_df = format_tom

    Args:
        station_code (str): _description_
        select_date (date): _description_
    """
    # TODO validate station code
    # must be a data TODO validate date
    if isinstance(select_date, str):
        select_date = date.fromisoformat(select_date)
        
    tc = request_tomcast_api(station_code, select_date)
    tc_df = format_tomcast_model_output(station_code = station_code, tomcast_api_output=tc)
    
    return(tc_df)
    