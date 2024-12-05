import requests
from warnings import warn
from . import BASE_PWS_API_URL
from datetime import date, timedelta
import pandas as pd
            
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
        station_code (_type_, optional): station code from weatherstation table in db. Defaults to None.
        start_date (_type_, optional): date to start. 
            Defaults to None, which means today, unles there is an end date, 
            which will be set to the end date
        end_date (_type_, optional): date to end on, could be same as start. 
            Defaults to None, meaning same as start_date
        api_url (_type_, optional): PWS API url. Defaults to BASE_PWS_API_URL.
    """
    
    EMPTY_DATA = [{}]
    
    if(not station_code):
        return(EMPTY_DATA)
    
    # default handling of dates for maximum flexibilty
    if(not start_date):
        if(not end_date): 
            start_date = str(date.today())
            end_date = str(date.today())
        else:
            start_date = end_date
    else:
        if(not end_date):
            end_date = start_date
            

    # check if start and end great than today
    url = f"{api_url}/weather/{station_code}/hourly?start={start_date}&end={end_date}"
    r = requests.get(url)
    if r.status_code == 200:
        return(r.json())
    else:
        return(EMPTY_DATA)
 



# NOTE This may not be needed, was created in early days to handle bad data 
# from dash callbacks
def hourly_readings(station_code=None, for_date = None):
    """invoke get_hourly_readings for one day, to get a data frame of weather 
    
    Args:
        station_code (str, optional): valid station code from db. Defaults to None, which returns empthy data
                     None is used here because Dash sometimes returns empty values or no Value
        for_date (str, optional): date to pull, if 
        
    Returns:
        always returns a data frame with weather data or empty   
    """
    
    if station_code:
        readings = get_hourly_readings(station_code, start_date = for_date)
        if readings:
            readings_df = pd.DataFrame(readings)
            if not readings_df.empty:
                return(readings_df)
     
    empty_df = pd.DataFrame([{}])   
    return(empty_df)
    
def yesterday_readings(station_code=None):
    """ get a data frame of weather.  When using this in the dash page, use 
    the dash bootstrap component library convenience function
    df = hourly_readings_table('MYSTATION')
    if df:
        html = dbc.Table.from_dataframe(hourly_readings_table('MYSTATION'))
    else:
        html = "no readings"
    
    """
    
    if station_code:
        readings = get_hourly_readings(station_code)
        if readings:
            readings_df = pd.DataFrame(readings)

            return(readings_df)
        else:
            return(None)
    else:
        return(None)


def latest_readings(station_code=None, api_url = BASE_PWS_API_URL):
    """  in 'latest' api endpoing, which gets the rows in readings table that 
    is the most recent for display.  
    It's up to displaying component how to determine if these 
    are actually 'recent
    
    Args:
        station_code (str, optional): valid station code from db. Defaults to 
            None, which returns empty data
             None is used here because Dash sometimes returns empty values or no Value
        api_url (str, optional): base url of the PWS API.  defaults to constant 
            set at top of this module
    """
    EMPTY_DATA = [{}]
    
    if(not station_code):
        return(EMPTY_DATA)
    
    url = f"{api_url}/weather/{station_code}/latest"
    r = requests.get(url)
    if r.status_code == 200:
        return(r.json())
    else:
        return(EMPTY_DATA)
    

        


