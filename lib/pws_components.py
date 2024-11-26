
# pws_components.py  reuseable components for pages
from dash import html
from lib.pwsapi import get_station_codes, get_station_data, get_all_stations
from datetime import date, timedelta

from .pwsapi import get_hourly_readings, yesterday_readings
from dash_bootstrap_components import Table as dbcTable


## Config
main_pws_title = 'MSU Enviroweather Personal Weather Station Dashboard'
site_nav = ["map", "station", "hourly", "about"]
sidebar_width = 250
DAYS_MISSING_THRESHOLDS = [1,4]

pws_title = html.H2(["MSU Enviroweather ", html.B(" Personal Weather Station Dashboard"),])

YESTERDAY = date.today() - timedelta(days = 1)

import dash_ag_grid as dag
import pandas as pd
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
        # get a data frame of readings, or None
        df = yesterday_readings(station_code)
        if(not df):
            return("No Data")
        else:
            df_table = dbcTable.from_dataframe(df)
            return(df_table)
    else:
        return("Select a station")