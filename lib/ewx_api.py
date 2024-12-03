""" ewx_api.py: functions to work with the Enviroweather RM API in Python
"""


## this goes into the PWS API module

from dotenv import load_dotenv
from datetime import datetime, date
from zoneinfo import ZoneInfo
import requests, json
load_dotenv()
from os import getenv
from pandas import DataFrame
from typing import Union


####### MODULE STYLE ##############

#### CONSTANTS
BASE_EWX_API_URL=getenv('BASE_EWX_API_URL', 'https://enviroweather.msu.edu/ewx-api/api')
BASE_RM_API_URL=getenv('BASE_RM_API_URL', 'https://enviroweather.msu.edu/rm-api/api')
PWS_STATION_TYPE = 6
MICHIGAN_TIME_ZONE_KEY = 'US/Eastern'
MICHIGAN_TIME_ZONE = ZoneInfo(MICHIGAN_TIME_ZONE_KEY)

global current_token_value
current_token_value = None
        
def token_value(base_ewx_api_url = BASE_EWX_API_URL):
    global current_token_value
    if current_token_value is None:
        current_token_value = aquire_token(base_ewx_api_url)
    
    return current_token_value
        
         
def aquire_token(base_ewx_api_url = BASE_EWX_API_URL)->str:
    token_url = f"{base_ewx_api_url}/db2/siteToken"
    r = requests.get(url = token_url)
    if r.status_code == 200:
        request_data:dict = r.json()
        if 'data' in request_data and 'token' in request_data['data']:
            token =request_data["data"]["token"]
            return(token)
    return ""


def get_result_model_keys(base_ewx_api_url:str = BASE_EWX_API_URL):
    """get keys from rm api (currently unused except for testing)"""
    url =  f"{base_ewx_api_url}/db2/resources?type=rm-api"   
    ewx_token = token_value(base_ewx_api_url)
    payload = {}
    
    response = requests.request("GET", 
                                url, 
                                headers=ewx_headers(base_ewx_api_url), 
                                data=payload)
    return(response.text)


def ewx_headers(base_ewx_api_url:str = BASE_EWX_API_URL):
    """ standard headers used in all requests"""
    return {
        'Accept': "application/json",
        'Authorization': f"Bearer ${token_value(base_ewx_api_url)}"
        }

def date_to_api_str(d):
    """ convert date to correct type and format for use in EWX API's
    
    assumes the date in the time zone for the station
    
    """
    if d is None:
    # must set timezone explicitly since no guarantee tz of server (or if it's UTC)
        d = datetime.now(tz=MICHIGAN_TIME_ZONE).date()
    elif isinstance(d, datetime):
        select_date = select_date.date()
    
    d_str = d.strftime("%Y-%m-%d")
    return(d)

    
def ewx_request(url:str,base_ewx_api_url:str = BASE_EWX_API_URL):
    """issue a standard request to EWX API given a url crafted for a specific model

    Args:
        url (str): URL for a specific model type with all parameters in place
        base_ewx_api_url (str, optional): api to get a token from, defaults to BASE_EWX_API_URL.

        should raise errors if bad HTTP or other reason, but for this POC, just
        return data or nothing
        
    Returns:
        ANY: the 'data' element of a standard RM-API array output
    """
    headers = ewx_headers(base_ewx_api_url)
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        response_data = response.json()
        # response_data = json.loads(response_json)
        
        if 'data' in response_data:
            return(response_data['data'])

    #TODO handle errors, http errors and errors embedded in
    
    print(f"request error {response.status_code} {response.text} url {url}")
    return None


def tomcast(station_code:str, select_date:Union[datetime,date,None] = None, weather:bool = True, base_rm_api_url:str = BASE_RM_API_URL, base_ewx_api_url:str = BASE_EWX_API_URL, ):
    """generate model URL for the TOMCAST model.   Date optional (will use today's date if none given)
    
    Args:
        station_code (str): PWS station code valid from database
        select_date (datetime | date | None, optional): optional date or datetime. Defaults to None.  If none sent, creates current date using timezone sent
        weather (bool, optional): ask the api to include weather data with the model output. Defaults to True
        base_rm_api_url (str, optional): url to use for the rm api (model). Defaults to module constant BASE_RM_API_URL, which is production api
        base_ewx_api_url (str, optional): api to get a token from, defaults to BASE_EWX_API_URL.
        
    Returns:
        Pandas DataFrame to send to UI for formatting
    """
    # model params    
    result_model_code:str = "tomcast"        
    select_date_str = date_to_api_str(select_date)
    
    #example https://enviroweather.msu.edu/rm-api/api/db2/run?stationCode=EWXDAVIS01&stationType=6&selectDate=2024-08-01&resultModelCode=tomcast"
    model_url = f"{BASE_RM_API_URL}/db2/run?stationCode={station_code}&stationType={PWS_STATION_TYPE}&selectDate={select_date_str}&resultModelCode={result_model_code}&weather={weather}"    
    model_data = ewx_request(model_url, base_ewx_api_url)

    if model_data:
        tomcast_df = DataFrame(model_data['Table'])
        return(tomcast_df)
    else:        
        return(DataFrame([{}]))
