
# pws_components.py  reuseable components for pages
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import date
from zoneinfo import ZoneInfo
from lib.pwsapi import get_station_codes, get_station_data, get_all_stations
from datetime import date, timedelta

from .pwsapi import get_hourly_readings, yesterday_readings, latest_readings
import dash_ag_grid as dag
import pandas as pd



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


def latest_readings_values(station_code, threshold_data_note_recent_enough_hours = 6):
    """get latest reading but check if it's too old for the UI to display"""
    r = latest_readings(station_code = station_code)
    
    if 'minutes_since_latest_reading' in r and r['minutes_since_latest_reading'] < threshold_data_note_recent_enough_hours*60:
        return(r) 
    else:
        return {}


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
        
            #df_table = dbc.Table.from_dataframe(df)
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


######################################
#### EWX RM API Model Components
from .ewx_api import tomcast, weather_model


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


def tomcast_model(station_code:str, select_date:date):
    """get simple tomcast model output and format for Dash.  

    Args:
        station_code (str): valid station code from database
        select_date (date): date to run model on, as date or string
    Returns:
        Dash UI element or string
    """
    # input checking
    if not station_code or station_code is None:
        return(dbc.Alert("select a station above", color="error"))
    
    if not select_date or not(isinstance(select_date, str)):
        print(f"got this for select_date: {select_date}")
        return("invalid date")

    # allow either date object or a date string in iso format
    if isinstance(select_date,str):
        select_date = date.fromisoformat(select_date)
    
    # run model and format output to data frame
    model_output = tomcast(station_code, select_date)

    # convert to UI table
    if isinstance(model_output, pd.DataFrame):
        # to-do : add style/colors to table
        return(dbc.Table.from_dataframe(model_output, responsive=True))
        
    else: # assume it's not a data frame, must be string with message
        return(dbc.Alert(model_output))


def weather_summary_form():
    today =  datetime.now(tz=ZoneInfo('US/Eastern')).date().strftime("%Y-%m-%d")
    
    # using bootstrap classes here becuase the default style is large and thin which doesn't match
    form = dbc.Row(
        [
            dbc.Col(
                dcc.DatePickerSingle(id='weather-summary-date-picker',
                                     display_format='YYYY-MM-DD',
                                     first_day_of_week = 1,                                       
                                     placeholder="Select Date",
                                     date = today, 
                                     className="fs-6 fw-semibold"),
                className="me-3",
                width = "auto"

                ),
            dbc.Col(
                dbc.Button("Run Weather Model", 
                               id="run-weather-summary-button", 
                               class_name="btn btn-success d-none d-sm-inline-block"), 
                width="auto"
                ),
        ],
        className="g-2",
        )
    
    return(form)
        
        
def weather_summary_table(station_code:str, select_date:date=None):
    """run weather model and format for inclusion in Dash UI

    Args:
        station_code (str): valid PWS station code from database
        select_date (date, optional): date to END pulling data.  starts from 
            01-01 of year of date. Defaults to None, which uses today
    """
    model_output = weather_model(station_code, select_date)

    if isinstance(model_output, pd.DataFrame):
        
        # for now, select few columns, and sort by date descending
        columns = ['date', 'atmp_min', 'atmp_avg','atmp_max', 'dd0_single', 'dd0_accum']
        column_defs = [{"field": c} if c != 'date' else {"field": c, "sort": "desc"} for c in columns]

        model_output_filtered= model_output.loc[:,columns]
        
        grid = dag.AgGrid(
            id="weather_summary_grid",
            rowData=model_output_filtered.to_dict("records"),
            columnDefs=column_defs,
            dashGridOptions={'pagination':True,
                             'sortingOrder': ['desc', 'asc', None]},
            columnSize="sizeToFit",
            )
        
        return(grid)
        
    else: # assume it's not a data frame, must be string with message
        return(dbc.Alert(model_output))    
    