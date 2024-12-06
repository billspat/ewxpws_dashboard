
# pws_components.py  reuseable components for pages
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import date, time
from zoneinfo import ZoneInfo
from lib.pwsapi import get_station_codes, get_station_data, get_all_stations
from datetime import date, timedelta

from .pwsapi import get_hourly_readings,latest_readings
import dash_ag_grid as dag
import pandas as pd

from .converters import hour_number2clock_str, degree2compass, kph2mph, c2f, mm2inch, today_localtime_str, first_of_year_string, days_ago



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


def hourly_readings_dataframe(station_code, for_date = None):
    """wrangle data from hourly summary from pws api into dataframe for
    presentation in American units

    Args:
        station_code (_type_): _description_
        for_date (_type_, optional): _description_. Defaults to None.
    """
    
    if station_code:
        # get a data frame of readings or empty df
        hourly_weather_json = get_hourly_readings(station_code=station_code, start_date = for_date) 
        if not hourly_weather_json:
            return("No Data")        
        
        weather_df = pd.DataFrame(hourly_weather_json)
        if(weather_df is None or (type(weather_df) != type(pd.DataFrame([{}]))) or weather_df.empty):
            return("No Data")        
        else:
            view_df = pd.DataFrame().assign(
                # date = weather_df['represented_date'],
                hour     = weather_df.represented_hour,
                time     = weather_df.represented_hour.map(hour_number2clock_str), 
                atmp     = round(c2f(weather_df.atmp_avg_hourly),1),
                relh     = round(weather_df.relh_avg_hourly,0),
                pcpn     = round(mm2inch(weather_df.pcpn_total_hourly),2),
                lws_pwet = weather_df.lws_pwet_hourly,
                wspd     = round(kph2mph(weather_df.wspd_avg_hourly),1),
                wspd_max = weather_df.wspd_max_hourly,
                wdir_avg = weather_df.wdir_avg_hourly.map(degree2compass)
            )
            
            view_df = view_df.sort_values(by=['hour'], ascending=False)
            return(view_df)
        
            #df_table = dbc.Table.from_dataframe(df)
            #return(df_table)
    else:
        return("Select a station code")
    


def hourly_readings_table(station_code, for_date = None):

    readings_df = hourly_readings_dataframe(station_code, for_date)
    
    if(readings_df is None or (type(readings_df) != type(pd.DataFrame([{}]))) or readings_df.empty):
        return(html.Div("no recent data", className="fw-bold"))
    
    
    weather_column_defs = [
        { 'headerName': 'hour', 'field': 'hour', 'hide':'true'},
        { 'headerName': 'Time', 'field': 'time',  'sortable': False  },
        { 'headerName': 'Air Temp (F)', 'field': 'atmp' },
        { 'headerName': 'Rel Humidity', 'field': 'relh' },
        { 'headerName': 'Precip (inch)', 'field': 'pcpn' },
        { 'headerName': 'Leaf Percent Wet', 'field': 'lws_pwet' },
        { 'headerName': 'Windspeed Avg (mph)', 'field': 'wspd' },
        { 'headerName': 'Windspeed Max (mph)', 'field': 'wspd_max' },
        { 'headerName': 'Wind Direction (avg)', 'field': 'wdir_avg' },
        ]
    
    readings_table = dag.AgGrid(
        id="readings_table",
        rowData = readings_df.to_dict('records'),
        columnDefs = weather_column_defs,
        defaultColDef={"resizable": True, "sortable": True, 
                    "filter": False,
                    "initialWidth": 200,
                    "wrapHeaderText": True,
                    "autoHeaderHeight": True,
                    },
        columnSize="sizeToFit",
        # dashGridOptions={"rowSelection": "single", "cellSelection": False, "animateRows": False},        
    )
    
    # readings_table =  dbc.Table.from_dataframe(readings_df, responsive=True)
        
    return(readings_table)




# this currently is not used.   Need to determine how to insert a whole AG grid into html 
    # there is a "I can't json this" error

def hourly_readings_grid_view(weather_df):
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


def pws_date_picker(id:str = "", initial_date_str:str = None):
    
    if initial_date_str is None or not(initial_date_str):
        initial_date_str = today_localtime_str()
    
    dps = dcc.DatePickerSingle(id=id,
                display_format='YYYY-MM-DD',
                first_day_of_week = 1,                                       
                placeholder="Select Date",
                date = initial_date_str, 
                className="fs-6 fw-semibold me-3",
                min_date_allowed=first_of_year_string(),
                max_date_allowed=today_localtime_str(),
                )
    
    return(dps)

def hourly_weather_form():
    today =  datetime.now(tz=ZoneInfo('US/Eastern')).date().strftime("%Y-%m-%d")
    
    # using bootstrap classes here becuase the default style is large and thin which doesn't match
    form = dbc.Row(
        [dbc.Col(pws_date_picker(id='hourly-weather-date-picker'),
                width = "auto",
                className="g-2",
                )]
        )
        
    return(form)

######################################
#### EWX RM API Model Components
from .ewx_api import tomcast, weather_summary


def tomcast_form():

    seven_days_ago_str =  days_ago(d=7).strftime("%Y-%m-%d")
    # using bootstrap classes here becuase the default style is large and thin which doesn't match
    form = dbc.Row(
        [

            dbc.Col([
                html.Div("Date of last spray/date to start accumulating DSV:", 
                        className="col-auto me-3 d-none d-sm-inline-block"),
                pws_date_picker(id='tomcast-spray-date-picker', initial_date_str= seven_days_ago_str )
                ],
                className="me-3",
                width = "auto"             
                ),
            dbc.Col([
                html.Div("Date:", 
                        className="col-auto me-3 d-none d-sm-inline-block"),
                pws_date_picker(id='tomcast-date-picker')
                ],
                width = "auto"
                ),
            dbc.Col(
                dbc.Button("Run Tomcast", 
                            id="run-tomcast-button", 
                            class_name="btn btn-success d-none d-sm-inline-block"
                            ), 
                
                width="auto"
                ),
            dbc.Col(
                html.Div("",
                     className="col-auto me-3 d-none d-sm-inline-block text-muted", 
                     id="tomcast_loading_message"),
            )

        ],
        className="g-2",
        )
    
    return(form)


def tomcast_model(station_code:str, 
                  select_date:date, 
                  date_start_accumulation:date=None):
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
    tomcast_output = tomcast(station_code, select_date, 
                             date_start_accumulation=date_start_accumulation)
    
    if not isinstance(tomcast_output, pd.DataFrame):
        return(tomcast_output)
    
    # to-do : add style/colors to table
    tomcast_column_defs = [
        { 'headerName': 'Date', 'field': 'Date', },
        { 'headerName': 'Disease Severity Units (DSV)', 'field': 'DSV' },
        { 'headerName': 'Accumulated  Disease Severity Units (DSV)', 'field': 'SumDSV' },
        { 'headerName': 'Risk', 'field': 'Risk' },
        { 'headerName': 'Day Number', 'field': 'TomcastDay' },
        { 'headerName': 'highlight', 'field': 'highlight', 'hide':'true' },
    ]
    
    
    # assign bootstrap colors based on risk
    tomcastRowClassRules = {
        "bg-warning-subtle": "params.data.Risk == 'low'",
        "bg-warning": "params.data.Risk == 'moderate'",
        "bg-danger fw-bold" : "params.data.Risk == 'high'",
        }   
    
    tomcast_table = dag.AgGrid(
        id="tomcast_table",
        rowData = tomcast_output.to_dict('records'),
        columnDefs = tomcast_column_defs,
        defaultColDef={"resizable": True, 
                    "sortable": False, 
                    "filter": False,
                    "wrapHeaderText": True,
                    "autoHeaderHeight": True,                    
                    },
        columnSize="sizeToFit",
        rowClassRules = tomcastRowClassRules,
        )
        
    return(tomcast_table)

######### WEATHER SUMMARY ############

def weather_summary_form():
    today =  datetime.now(tz=ZoneInfo('US/Eastern')).date().strftime("%Y-%m-%d")
    
    # using bootstrap classes here becuase the default style is large and thin which doesn't match
    form = dbc.Row(
        [
            dbc.Col(
                pws_date_picker(id='weather-summary-date-picker'),
                className="me-3",
                width = "auto"
                ),
            dbc.Col(
                dbc.Button("Calculate Weather Summary", 
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
    model_output = weather_summary(station_code, select_date)
    
    if not isinstance(model_output, pd.DataFrame):
        # not a data frame, assume it's a message
        return(dbc.Alert(model_output)) 
        
    # for now, select few columns
    ws_columns = ['date', 'atmp_min', 'atmp_avg', 'atmp_max',  'dd0_single', 'dd0_accum', 'pcpn_single','pcpn0_accum', 'l_wet_0']

    from .ewx_api import weather_summary_table_headers as ws_headers        
    ws_column_defs = [ { 'field': c, 'headerName': ws_headers[c] } for c in ws_columns]  
    model_output_filtered= model_output.loc[:,ws_columns]
    
    # note: sort by date descending to show most recent data first
    grid = dag.AgGrid(
        id="weather_summary_grid",
        rowData=model_output_filtered.to_dict("records"),
        columnDefs=ws_column_defs,
        dashGridOptions={"filter": False,
                    "wrapHeaderText": True,
                    "autoHeaderHeight": True,
                    "pagination":True,
                    "sortingOrder": ['desc', 'asc', None],
                    "initialWidth": 200,                    
                    },
        
        
        columnSize="sizeToFit",
        )
    
    return(grid)
        
           
    