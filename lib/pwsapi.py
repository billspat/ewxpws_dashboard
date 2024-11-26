import requests
from warnings import warn
from . import BASE_PWS_API_URL
from datetime import date, timedelta

            
def get_station_codes(api_url:str = BASE_PWS_API_URL):
    r = requests.get(url = f"{api_url}/stations/")
    if r.status_code == 200:
        station_codes = r.json()['station_codes']
    else:
        station_codes = []
        
    return(station_codes)

def get_station_data(station_code:str, api_url:str = BASE_PWS_API_URL):
    """get decscriptive data of a single station from the PWS API 

    Args:
        station_code (str): _description_
        api_url (str, optional): _description_. Defaults to BASE_PWS_API_URL.

    Raises:
        RuntimeError: _description_
    """
    
    if(not api_url):
        raise RuntimeError( "you must set the URL to reach the PWS API, for example BASE_PWS_API_URL")
    
    r = requests.get(url = f"{api_url}/stations/{station_code}")
    if r.status_code == 200:
        return(r.json())
    else:
        return({})

def station_latlon(station_code):
    if station_code:
        station_data = get_station_data(station_code)
        lat = station_data['lat']
        lon = station_data['lon']
    else:
        lat = 43
        lon = -82
        
    return ([lat, lon])

def get_all_stations(api_url:str = BASE_PWS_API_URL):
    """get a table of all station data using a loop
    
    since there is not an API endpoint to list all the stations with details (or a subset), 
    this just loops through and hits the api for each. Very inefficient! 

    Args:
        api_url (str, optional): base of the API to use to pull data.  Defaults to constant BASE_PWS_API_URL.
    """
    # create pandas df instead 
    stations = {}
    station_codes = get_station_codes(api_url)
    
    for station_code in station_codes:
        station_data_json = get_station_data(station_code, api_url)
        # 
        stations[station_code ]  = station_data_json
                                  
    return(stations)


def get_hourly_readings(station_code=None, start_date=None, end_date=None, api_url = BASE_PWS_API_URL):
    """_summary_

    Args:
        station_code (_type_, optional): _description_. Defaults to None.
        start_date (_type_, optional): _description_. Defaults to None.
        end_date (_type_, optional): _description_. Defaults to None.
        api_url (_type_, optional): _description_. Defaults to BASE_PWS_API_URL.
    """
    
    EMPTY_DATA = [{}]
    
    if(not station_code):
        return(EMPTY_DATA)
    
    if(not start_date or not end_date): 
        start_date = str(date.today())
        end_date = str(date.today())

    # check if start and end great than today
    url = f"{api_url}/weather/{station_code}/hourly?start={start_date}&end={end_date}"
    r = requests.get(url)
    if r.status_code == 200:
        return(r.json())
    else:
        return(EMPTY_DATA)
 

import pandas as pd

def yesterday_readings(station_code=None):
    """get a data frame of weather.  When using this in the dash page, use 
    the dash bootstrap component library convenience function
    df = yesterday_readings_table('MYSTATION')
    if df:
        html = dbc.Table.from_dataframe(yesterday_readings_table('MYSTATION'))
    else:
        html = "no readings"
    
    Args:
        station_code (_type_, optional): _description_. Defaults to None.    
        
    Returns:
        always returns a data frame with weather data or empty   
    """
    
    if station_code:
        readings = get_hourly_readings(station_code)
        if readings:
            readings_df = pd.DataFrame(readings)
            if not readings_df.empty:
                return(readings_df)
     
    empty_df = pd.DataFrame([{}])   
    return(empty_df)
    
      
def get_station_temperature():
    # invoke station readings, and filter out just atmp
    return None
        


